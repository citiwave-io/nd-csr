
# Harvest public information leveraging client side rendering

This utility is designed for harvesting data from web pages using Python for educational and research purpose only. It makes use of libraries such as `requests`, `urllib`, `pandas`, `numpy`, `json`, `BeautifulSoup`, `cloudscraper`, and `selenium`, among others.

## Features

- **Data Extraction**: Leverages both traditional HTTP requests and browser automation via Selenium to extract data from web pages.
- **Parsing**: Uses BeautifulSoup for parsing HTML and extracting information.
- **Browser Automation**: Utilizes the Selenium WebDriver for automated navigation of web pages in a browser-like environment.
- **Headless Option**: Can be configured to run the browser in headless mode, allowing the script to operate without a visible UI.

## Requirements

- Python 3
- Pip (Python package installer)
- Additional Python libraries: `requests`, `urllib`, `re`, `sys`, `pandas`, `numpy`, `json`, `BeautifulSoup`, `cloudscraper`, `selenium`, `schedule`, `time`, `datetime`, `matplotlib`, `hashlib`
- GeckoDriver (for Selenium with Firefox)

## Usage

1. Ensure Python and Pip are installed on your system.
2. Install all required Python libraries using Pip:
   \```
   pip install -r requirements.txt
   \```
3. (Optional) Set up a virtual environment to manage dependencies.
4. Run the script using Python:
   \```
   python final_scraping_code_v2.py
   \```

## Configuration

- Base URL and other parameters can be set within the script.
- Modify the `headless_browser` function to toggle headless mode as needed.

## Note

This script is for educational purposes and should be used responsibly. Always ensure you have permission to scrape data from a website and comply with the website’s terms of service and robots.txt file.
