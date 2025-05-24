import asyncio
import logging
from urllib.parse import urlparse
from pathlib import Path

from aiotdlib import Client, ClientSettings
from aiotdlib.api import InputMessageText
from config import API_ID, API_HASH


async def process_account(phone_number: str, channel_username: str):
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    log = lambda msg: logging.info(msg)

    log(f"[{phone_number}] process_account started")
    log(f"[{phone_number}] initializing ClientSettings...")

    normalized_phone = phone_number.replace("+", "")
    session_path = Path(f"sessions/{normalized_phone}").resolve()
    session_path.mkdir(parents=True, exist_ok=True)

    settings = ClientSettings(
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number,
        files_directory=str(session_path)
    )

    client = Client(settings=settings)
    await client.start()
    log(f"[{phone_number}] client started")

    try:
        log(f"[{phone_number}] Ищем канал @{channel_username}...")
        chat = await client.api.search_public_chat(username=channel_username)
        chat_id = chat.id
        log(f"[{phone_number}] Получен chat_id: {chat_id}")

        log(f"[{phone_number}] Запрашиваем рекламные сообщения...")
        sponsored_list = await client.api.get_chat_sponsored_messages(chat_id=chat_id)

        if not sponsored_list:
            log(f"[{phone_number}] Нет рекламных сообщений в @{channel_username}")
            await client.stop()
            return

        log(f"[{phone_number}] Найдено {len(sponsored_list)} рекламных сообщений")

        for i, msg in enumerate(sponsored_list):
            log(f"[{phone_number}] Реклама #{i}")

            sponsor_msg_id = getattr(msg, "sponsor_message_id", None)
            raw_msg = getattr(msg, "message", None)
            real_msg_id = getattr(raw_msg, "id", None) if raw_msg else None

            if not real_msg_id:
                log(f"[{phone_number}] Пропускаем рекламу [index={i}]: нет message.id")
                continue

            log(f"[{phone_number}] Кликаем по рекламе [index={i}] (message_id={real_msg_id})...")
            try:
                await client.api.click_chat_sponsored_message(chat_id=chat_id, message_id=real_msg_id)
                log(f"[{phone_number}] Клик выполнен (message_id={real_msg_id})")
            except Exception as e:
                log(f"[{phone_number}] Ошибка при клике по рекламе: {e}")
                continue

            await asyncio.sleep(3)

            sci = getattr(msg, "sponsor_chat_info", None)
            if not sci or not getattr(sci, "url", None):
                log(f"[{phone_number}] Нет sponsor_chat_info или sponsor_chat_info.url")
                continue

            url = sci.url
            log(f"[{phone_number}] Переход по ссылке: {url}")
            parsed = urlparse(url)
            username = parsed.path.strip("/")

            if parsed.path.startswith("/+"):
                log(f"[{phone_number}] Приватная ссылка, подписка невозможна: {url}")
                continue

            try:
                target_chat = await client.api.search_public_chat(username=username)
                if target_chat.type_.ID in ['chatTypeSupergroup', 'chatTypeBasicGroup']:
                    log(f"[{phone_number}] Подписка на канал @{username}...")
                    await client.api.join_chat(chat_id=target_chat.id)
                elif target_chat.type_.ID == 'chatTypePrivate':
                    log(f"[{phone_number}] Стартуем бота @{username}...")
                    await client.api.send_message(
                        chat_id=target_chat.id,
                        input_message_content=InputMessageText(
                            text={"@type": "text", "text": "/start"}
                        )
                    )
            except Exception as e:
                log(f"[{phone_number}] Ошибка при переходе: {e}")

        log(f"[{phone_number}] Останавливаем клиента")
        await client.stop()

    except Exception as e:
        logging.error(f"[{phone_number}] Фатальная ошибка: {e}")
        await client.stop()
