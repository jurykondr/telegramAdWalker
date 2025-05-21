from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import time


def auto_scroll(driver, scroll_pause_time=2, max_scrolls=10):
    """Автоматически прокручивает страницу вниз."""
    last_height = driver.execute_script("return document.body.scrollHeight")

    for scroll in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # ждем загрузку
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            print("Достигнут конец страницы.")
            break

        last_height = new_height
        print(f"Прокрутка {scroll + 1} выполнена.")


def scrape_ads(driver, channel_url, session_dir):
    driver.get(channel_url)
    print("Страница канала открыта. Начинаем автоматическую прокрутку...")

    auto_scroll(driver, scroll_pause_time=2, max_scrolls=15)

    html = driver.page_source
    filename = os.path.join(session_dir, 'channel_page.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML сохранён в {filename}")

    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]

    links_file = os.path.join(session_dir, 'extracted_links.txt')
    with open(links_file, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')

    print(f"Ссылки извлечены и сохранены в {links_file}")


def visit_links(driver, links, delay=5):
    """Автоматически переходит по каждой ссылке."""
    for link in links:
        print(f'Переход на {link}')
        driver.get(link)
        time.sleep(delay)
