import os
import csv
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

class Crawler:
    def __init__(self, base_url):
        load_dotenv()
        self.base_url = base_url
        self.data = []

    def crawl_pages(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)

            while True:
                page.wait_for_selector("#datatable", state="visible")

                self.__extract_data(page)

                # 按下一頁
                try:
                    next_button = page.locator("li.paginate_button.page-item.next")
        
                    if next_button.is_visible() and not next_button.get_attribute("class").contains("disabled"):
                        next_button.click()
                        page.wait_for_timeout(2000)
                    else:
                        print("Reached the last page or no more pages to crawl.")
                        break
                except Exception as e:
                    print("Error occurred during pagination:", e)
                    break

            browser.close()

    def __extract_data(self, page):
        rows = page.locator("table#datatable tbody tr")

        for i in range(rows.count()):
            row = rows.nth(i)
            
            transaction_hash = row.locator("td:nth-child(2) .hash-tag.text-truncate").text_content()
            timestamp = row.locator("td:nth-child(4) .showDate span").text_content()
            action = row.locator("td:nth-child(5) .text-success").text_content()
            price = row.locator("td:nth-child(6)").text_content()
            market = row.locator("td:nth-child(7) span").text_content()
            buyer = row.locator("td:nth-child(8) .js-clipboard").get_attribute("data-clipboard-text")

            nft_full_id = row.locator("td:nth-child(10) a .hash-tag.text-truncate span")
            nft_id = str(nft_full_id).split("#")[1]

            self.data.append({
                "Transaction Hash": transaction_hash,
                "DateTime (UTC)": timestamp,
                "Action": action,
                "Price": price,
                "Market": market,
                "Buyer": buyer,
                "Token ID": nft_id
            })

    def save_to_csv(self, filename):
        if not self.data:
            print("No data to save.")
            return

        fieldnames = self.data[0].keys()

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)

            print(f"Data successfully saved to {filename}")
        except Exception as e:
            print(f"Error occurred while saving to CSV: {e}")

    def __crawl_pages(self, page, page_limit=1):
        current_page = 0

        while current_page < page_limit:
            self.__extract_data(page)

            next_button = page.locator("li.paginate_button.page-item.next")
            if next_button.is_visible() and not next_button.get_attribute("class").contains("disabled"):
                next_button.click()
                page.wait_for_timeout(2000)
                current_page += 1
            else:
                print("No more pages to crawl.")
                break


if __name__ == "__main__":
    crawler = Crawler(base_url=os.getenv('CRAW_PAGE'))
    crawler.crawl_pages()
    crawler.save_to_csv('test.csv')

