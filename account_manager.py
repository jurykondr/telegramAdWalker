
import os
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from config import API_ID, API_HASH, SESSION_DIR

def add_account(phone_number: str):
    session_path = os.path.join(SESSION_DIR, f"{phone_number.replace('+', '')}")
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
            code = input(f"[{phone_number}] Введите код из Telegram: ")
            try:
                client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input(f"[{phone_number}] Аккаунт защищен 2FA. Введите пароль: ")
                client.sign_in(password=password)
        print(f"[✓] Аккаунт {phone_number} успешно авторизован.")
    except Exception as e:
        print(f"[✗] Ошибка при авторизации {phone_number}: {e}")
    finally:
        client.disconnect()
