import os
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from io import StringIO
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

class DataExtractor:
    def __init__(self, base_url):
        load_dotenv()
        self.base_url = base_url
        self.data = []
        self.s3_client = boto3.client('s3')
        self.stop_crawling = False

    def crawl_all_pages(self, last_known_time=None):
        with sync_playwright() as p:
            browser = p.chromium.launch(
            proxy={
                "server": os.getenv('PROXY_SERVER'),
                "username": os.getenv('PROXY_USER'),
                "password": os.getenv('PROXY_PASSWORD'),
            },
        )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/131.0.0.0 Mobile Safari/537.36",
                locale="zh-TW",
                extra_http_headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "zh-TW,zh;q=0.9",
                    "Cache-Control": "no-cache",
                    "DNT": "1",
                    "Pragma": "no-cache",
                    "Referer": os.getenv('CRAW_PAGE'),
                    "Sec-Fetch-Dest": "script",
                    "Sec-Fetch-Mode": "no-cors",
                    "Sec-Fetch-Site": "same-origin"
                }
            )
            page = context.new_page()
            page.set_default_timeout(60000)
            response = page.goto(self.base_url, wait_until="networkidle")
            print(f"Page load response: {response.status}")
            
            if response.status != 200:
                print("Failed to load page.")
                with open("debug_page.html", "w") as f:
                    f.write(page.content())
                self._upload_to_s3("debug_page.html", os.getenv('BUCKET_NAME'), "debug/debug_page.html")
                print("Page content saved for debugging.")
                return
            
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
                    page.wait_for_timeout(120_000)
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

    def save_raw_to_s3(self, key):
        if not self.data:
            print("No data to save.")
            return False

        #轉為CSV
        df = pd.DataFrame(self.data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        #存到S3
        try:
            self.s3_client.put_object(Bucket=os.getenv('BUCKET_NAME'), Key=key, Body=csv_buffer.getvalue())
            print(f"Data successfully saved to s3://{os.getenv('BUCKET_NAME')}/{key}")
            return True
        except Exception as e:  
            print(f"Error saving data to S3: {e}")
            return False
            
    def _crawl_pages_with_limit(self, page_limit=2):
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
                    current_page += 1
                except Exception as e:
                    print("Error occurred during pagination:", e)
                    break
               
            browser.close()

    #debug用
    def _upload_to_s3(self, file_name, bucket, object_name=None):
        try:
            response = self.s3_client.upload_file(file_name, bucket, object_name or file_name)
            print(f"File uploaded to S3: s3://{bucket}/{object_name or file_name}")
        except NoCredentialsError:
            print("Credentials not available for S3 upload.")
        except Exception as e:
            print(f"Error uploading file to S3: {e}")

if __name__ == "__main__":
    crawler = DataExtractor(base_url=os.getenv('CRAW_PAGE'))
    crawler._crawl_pages_with_limit(page_limit=2)

