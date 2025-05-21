from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def authorize(driver, phone_number):
    print("Открытие страницы Telegram Web...")

    driver.get("https://web.telegram.org/k/")

    time.sleep(3)

    try:
        login_by_phone = driver.find_element(By.XPATH, "//a[contains(text(), 'LOG IN BY PHONE NUMBER')]")
        login_by_phone.click()
        print("Кнопка 'LOG IN BY PHONE NUMBER' нажата.")
    except Exception as e:
        print("Не удалось нажать на ссылку входа по номеру:", e)
        return

    time.sleep(2)

    try:
        phone_input = driver.find_element(By.XPATH, "//input[@name='phone_number']")
        phone_input.click()
        phone_input.send_keys(Keys.CONTROL + "a")
        phone_input.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        phone_input.send_keys(phone_number)
        print(f"Phone number {phone_number} enteres")
    except Exception as e:
        print("Not valid number:", e)
        return

    print("Enter the code and push 'Enter'")
    input()
