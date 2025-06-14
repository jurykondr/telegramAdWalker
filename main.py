import os
import logging
import asyncio
import json

from core.tdlib_client import TdlibClient
from aiotdlib.api import SearchPublicChat

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")

SESSION_PATH = "sessions"


async def main():
    phone = os.environ.get("PHONE")
    api_id = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    channel = os.environ.get("CHANNEL")

    if not all([phone, api_id, api_hash]):
        logging.error("Не заданы все переменные окружения (PHONE, API_ID, API_HASH)")
        return

    logging.info(f"[{phone}] Запуск сессии...")

    client = TdlibClient(
        phone=phone,
        api_id=int(api_id),
        api_hash=api_hash,
        session_path=SESSION_PATH,
    )

    try:
        await client.create_client()

        chat = None
        if channel:
            logging.info(f"[{phone}] Ищем канал по имени: {channel}")
            chat = await client.client.send(SearchPublicChat(username=channel))
        else:
            logging.warning(f"[{phone}] channel не задан — ничего не делаем")
            return

        if not chat:
            logging.warning(f"[{phone}] Канал @{channel} не найден!")
            return

        sponsored = await client.get_sponsored_message(chat.id)
        if not sponsored or not sponsored.messages:
            logging.warning(f"[{phone}] Рекламных сообщений не найдено")
            return

        msg = sponsored.messages[0]
        url = msg.sponsor_info.link
        logging.info(f"[{phone}] Найдена реклама: {url}")

        await client.click_sponsored_message(chat.id, msg.id)
        await client.handle_sponsored_link(url)

    except Exception as e:
        logging.error(f"[{phone}] Ошибка: {e}")
    finally:
        await client.client.idle()
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
