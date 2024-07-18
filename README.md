# Stock News Crawler

This project scrapes news articles for specified stock codes from [CafeF](https://s.cafef.vn) using Selenium and BeautifulSoup.

## Features

- Scrapes and filters news articles by category.
- Extracts article data: timestamp, title, link, first paragraph.
- Saves data to categorized folders and Excel files.
- Supports date range filtering.

## Main Components

### Config Class
Contains configuration settings such as the base URL, timeout, and data folder.

### StockCrawler Class
Main class that handles the web scraping process.

- `__init__(self, stock_code)`: Initializes the crawler with a stock code.
- `initialize_driver(self)`: Initializes the Selenium WebDriver.
- `make_request(self, url)`: Makes an HTTP request and returns the response.
- `filter_news_by_category(self, category_id)`: Filters news articles by a specified category.
- `scrape_article_data(self, article)`: Extracts data from a single news article.
- `crawl_stock_data(self, num_articles=None, start_date=None, end_date=None)`: Main method to crawl and save stock data.

## Example

Here is an example of the output structure for a stock code `VNM`:

- Data/
  - Data_VNM/
    - Data_VNM_Category1/
      - Data_VNM_10_articles.xlsx
    - Data_VNM_Category2/
      - Data_VNM_8_articles.xlsx
    - ...


## Acknowledgements

- [CafeF](https://s.cafef.vn) for providing the data source.
- The authors of `selenium`, `beautifulsoup4`, `pandas`, and `requests` libraries.

## Contact

For any questions or feedback, please contact:
- Email: [nhv.analysis@gmail.com](mailto:nhv.analysis@gmail.com)
- LinkedIn: [Vi Nguyen](https://www.linkedin.com/in/vi-nguyen-946a08319/)
  <!-- Replace the image_url with the URL of your logo image -->
<a href="mailto:nhv.analysis@gmail.com">
  <img src="mail.jpg" alt="Mail" width="100" height="100">
</a>
<a href="https://www.linkedin.com/in/vi-nguyen-946a08319/">
  <img src="linkin.png" alt="LinkedIn" width="100" height="100">
</a>
