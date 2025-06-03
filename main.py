import asyncio
import json
import logging
import os

from core.tdlib_client import TdlibClient
from aiotdlib.api import SearchPublicChat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s"
)

CONFIG_PATH = "config/accounts.json"
SESSION_PATH = "sessions"


async def run_account(account):
    phone = account["phone"]
    api_id = account["api_id"]
    api_hash = account["api_hash"]
    channel = account.get("channel")
    chat_id = account.get("chat_id")

    logging.info(f"[{phone}] Запуск сессии...")

    client = TdlibClient(
        phone=phone,
        api_id=api_id,
        api_hash=api_hash,
        session_path=SESSION_PATH
    )

    try:
        await client.create_client()

        if not chat_id and channel:
            try:
                logging.info(f"[{phone}] Ищем канал по имени: {channel}")
                chat = await client.client.send(SearchPublicChat(username=channel))
                if chat is None:
                    logging.warning(f"[{phone}] Канал @{channel} не найден!")
                    return
                chat_id = chat.id
            except Exception as e:
                logging.warning(f"[{phone}] Ошибка при поиске канала @{channel}: {e}")
                return

        if not chat_id:
            logging.warning(f"[{phone}] Ни channel, ни chat_id не указаны — пропускаем")
            return

        sponsored = await client.get_sponsored_message(chat_id)
        if not sponsored or not sponsored.messages:
            logging.warning(f"[{phone}] Рекламных сообщений не найдено")
            return

        msg = sponsored.messages[0]
        url = msg.sponsor_info.link
        logging.info(f"[{phone}] Найдена реклама: {url}")

        await client.click_sponsored_message(chat_id, msg.id)

        await client.handle_sponsored_link(url)

    except Exception as e:
        logging.error(f"[{phone}] Ошибка при обработке аккаунта: {e}")
    finally:
        logging.info(f"[{phone}] Останавливаем клиента")
        await client.stop()


async def main():
    if not os.path.exists(CONFIG_PATH):
        logging.error("Файл конфигурации не найден: config/accounts.json")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        accounts = json.load(f)

    tasks = [run_account(account) for account in accounts]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
