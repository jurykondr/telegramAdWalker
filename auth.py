from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def authorize(driver, phone_number):
    driver.get("https://web.telegram.org/k/")
    input("После авторизации в браузере нажми Enter...")

    # Альтернативно можешь автоматизировать ввод телефона и кода подтверждения.
    # Ручная авторизация надежнее и проще.
