import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime

class Config:
    BASE_URL = "https://s.cafef.vn"
    TIMEOUT = 10
    DATA_FOLDER = "Data"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
options = webdriver.ChromeOptions()
#options.add_argument('--headless')

class StockCrawler:
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.driver = None
        self.categories = [0, 2, 1, 4, 5, 3]

    def initialize_driver(self):
        self.driver = webdriver.Chrome(options=options)

    def make_request(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            return None

    def filter_news_by_category(self, category_id):
        if not self.driver:
            self.initialize_driver()

        url = f"{Config.BASE_URL}/tin-doanh-nghiep/{self.stock_code}/event.chn"
        self.driver.get(url)

        category_dropdown = WebDriverWait(self.driver, Config.TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, f'a{category_id}'))
        )
        category_dropdown.click()

        try:
            WebDriverWait(self.driver, Config.TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'newsitem'))
            )
        except TimeoutException as e:
            print(f"TimeoutException: {e}")

    def scrape_article_data(self, filter_news_by_category):
        timestamp = filter_news_by_category.find("span", {"class": "timeTitle"})
        title = filter_news_by_category.find("a", {"class": "docnhanhTitle"})

        if timestamp and title:
            timestamp_text, title_text = timestamp.text.strip(), title.text.strip()
            article_link = filter_news_by_category.find("a", {"class": "docnhanhTitle"})["href"]
            article_url = f"{Config.BASE_URL}{article_link}"

            article_response = self.make_request(article_url)

            if article_response:
                article_soup = BeautifulSoup(article_response.text, "html.parser")
                first_paragraph = article_soup.find("h2", class_="intro")

                if first_paragraph:
                    first_paragraph_text = first_paragraph.text.strip()
                    return {
                        'Thời gian đăng bài': timestamp_text,
                        'Link bài viết': article_url,
                        'Tiêu đề bài viết': title_text,
                        'First paragraph': first_paragraph_text
                    }
        return None

    def crawl_stock_data(self, num_articles=None, start_date=None, end_date=None):
        if not self.stock_code:
            logger.error("Mã cổ phiếu không hợp lệ.")
            return

        stock_folder = os.path.join(Config.DATA_FOLDER, f"Data_{self.stock_code}")
        os.makedirs(stock_folder, exist_ok=True)

        for category_id in self.categories:
            self.filter_news_by_category(category_id)
            category_name = self.driver.find_element(By.ID, f'a{category_id}').text.strip()

            category_folder = os.path.join(stock_folder, f"Data_{self.stock_code}_{category_name}")
            os.makedirs(category_folder, exist_ok=True)

            data = []
            while num_articles is None or len(data) < num_articles:
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                news_container = soup.find("div", {"id": "divTopEvents"})
                news_articles = news_container.find_all("li")

                for article in news_articles:
                    article_data = self.scrape_article_data(article)
                    if article_data:
                        data.append(article_data)

                next_button = self.driver.find_element(By.ID, "spanNext")

                if "disabled" in next_button.get_attribute("class"):
                    break
                else:
                    next_button.click()

                if not news_articles:
                    break

                if start_date and end_date:
                    # Convert string dates to datetime objects
                    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                    # Check if the timestamp of the last article is within the specified range
                    last_article_timestamp = datetime.strptime(data[-1]['Thời gian đăng bài'],
                                                               "%d/%m/%Y %H:%M")

                    if not (start_datetime <= last_article_timestamp <= end_datetime):
                        break

            # Filter the data based on the date range
            if start_date and end_date:
                data = [item for item in data if
                             start_datetime <= datetime.strptime(item['Thời gian đăng bài'],
                                                                 "%d/%m/%Y %H:%M") <= end_datetime]

            df = pd.DataFrame(data)
            output_path = os.path.join(category_folder, f'Data_{self.stock_code}_{len(data)}_articles.xlsx')
            df.to_excel(output_path, index=False)
            logger.info(f"Dữ liệu đã được lưu tại: {output_path}")

if __name__ == "__main__":
    stock_code = input("Nhập mã cổ phiếu: ").upper()
    start_date = input("Nhập ngày bắt đầu (YYYY-MM-DD), để trống nếu muốn lấy tất cả: ")
    end_date = input("Nhập ngày kết thúc (YYYY-MM-DD), để trống nếu muốn lấy tất cả: ")

    crawler = StockCrawler(stock_code)
    crawler.crawl_stock_data(start_date=start_date, end_date=end_date)
