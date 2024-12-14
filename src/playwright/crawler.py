import os
import csv
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

class Crawler:
    def __init__(self, base_url):
        load_dotenv()
        self.base_url = base_url
        self.data = []
        self.stop_crawling = False

    def crawl_all_pages(self, last_known_time=None):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)

            while True:
                page.wait_for_selector("#datatable", state="visible")
                self.__extract_data(page, last_known_time=last_known_time)

                if self.stop_crawling:
                    print("Reached the previously transaction.")
                    break

                # 按下一頁
                try:
                    next_button = page.locator("#datatable_next")
                    next_button_class = next_button.get_attribute("class")

                    if "disabled" in next_button_class:
                        print("Reached the last page.")
                        break

                    next_button.click()
                    page.wait_for_timeout(2000)
                except Exception as e:
                    print("Error occurred during pagination:", e)
                    break

            browser.close()

    def __extract_data(self, page, last_known_time=None):
        rows = page.locator("table#datatable tbody tr")

        for i in range(rows.count()):
            row = rows.nth(i)
            
            transaction_hash = row.locator("td:nth-child(2) .hash-tag.text-truncate").text_content()
            timestamp = row.locator("td:nth-child(4) .showDate span").text_content()
            action = row.locator("td:nth-child(5) .text-success").text_content()
            price = row.locator("td:nth-child(6)").text_content()
            market = row.locator("td:nth-child(7) span").text_content()
            
            buyer_cell = row.locator("td:nth-child(8)")
            buyer_text = buyer_cell.text_content().strip()
            if buyer_text == "-":
                continue  #跳過沒有買家的資料
            buyer = buyer_cell.locator(".js-clipboard").get_attribute("data-clipboard-text")

            nft_full_id = row.locator("td:nth-child(10) a .hash-tag.text-truncate span", has_text="#").text_content()
            nft_id = str(nft_full_id).split("#")[1]

            transaction_datetime = pd.to_datetime(timestamp)
            # 檢查是否為新資料
            if last_known_time and transaction_datetime <= last_known_time:
                self.stop_crawling = True
                return

            self.data.append({
                "Transaction Hash": transaction_hash,
                "DateTime (UTC)": timestamp,
                "Action": action,
                "Price": price,
                "Market": market,
                "Buyer": buyer,
                "Token ID": nft_id
            })

    def save_to_csv(self, folder="src/db/raw"):
        if not self.data:
            print("No data to save.")
            return

        fieldnames = self.data[0].keys()

        try:
            with open(folder, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)

            print(f"Data successfully saved to {folder}")
        except Exception as e:
            print(f"Error occurred while saving to CSV: {e}")

    def crawl_pages_with_limit(self, page_limit=2):
        current_page = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)

            while current_page < page_limit:
                page.wait_for_selector("#datatable", state="visible")
                self.__extract_data(page)

                try:
                    next_button = page.locator("#datatable_next")
                    next_button_class = next_button.get_attribute("class")
                    
                    if "disabled" in next_button_class:
                        print("Reached the last page.")
                        break

                    next_button.click()
                    page.wait_for_timeout(2000)
                except Exception as e:
                    print("Error occurred during pagination:", e)
                    break
               
            browser.close()


if __name__ == "__main__":
    crawler = Crawler(base_url=os.getenv('CRAW_PAGE'))
    crawler.crawl_all_pages()
    crawler.save_to_csv('transactions.csv')

