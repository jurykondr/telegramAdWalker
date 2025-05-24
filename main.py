import os
import asyncio

from clicker import perform_action
from account_manager import add_account
from config import SESSION_DIR, ACCOUNTS
from runner import run_mass_click
from tdlib_ads import get_sponsored_url
from tdlib_clicker import mass_click


def list_sessions():
    print("Доступные аккаунты:")
    for f in os.listdir(SESSION_DIR):
        if f.endswith('.session'):
            print(f' - {f}')


if __name__ == '__main__':
    print("=== Telegram Clicker: Управление аккаунтами ===")
    action = input("Выберите действие: [1] Добавить аккаунт, [2] Показать аккаунты, [3] Перейти по ссылке, [4] Массовый переход, [5] Перейти по рекламе канала, [6] Массовый клик рекламы, [7] Авторизовать аккаунты → ")

    if action == '1':
        phone = input("Введите номер телефона (+79001234567): ")
        add_account(phone)
    elif action == '2':
        list_sessions()
    elif action == '3':
        link = input("Введите Telegram-ссылку (t.me/...): ")
        phone = input("Введите номер аккаунта, с которого выполнить: ")
        asyncio.run(perform_action(phone, link))
    elif action == '4':
        link = input("Введите Telegram-ссылку (t.me/...): ")
        asyncio.run(run_mass_click(link))
    elif action == '5':
        channel = input("Введите username канала (без t.me/): ")
        phone = input("Введите номер телефона (+79001234567): ")
        ad_url = asyncio.run(get_sponsored_url(channel, phone))
        if ad_url:
            print(f"[INFO] Начинаем массовый переход по {ad_url}")
            asyncio.run(run_mass_click(ad_url))
    elif action == '6':
        channel = input("Введите username канала (без t.me/): ")
        mass_click(channel, ['+79951579760'])
    # elif action == '7':
    #     auth_all_accounts(ACCOUNTS)
    else:
        print("Неверный выбор.")
