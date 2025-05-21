from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime
from auth import authorize
from scrapper import scrape_ads
from config import PHONE_NUMBER, CHANNEL_URL

def main():
    session_dir = os.path.join('sessions', datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(session_dir, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(CHANNEL_URL)
        authorize(driver, PHONE_NUMBER)
        scrape_ads(driver, CHANNEL_URL, session_dir)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
