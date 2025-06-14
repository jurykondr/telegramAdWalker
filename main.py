import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiotdlib import Client, ClientSettings
from aiotdlib.api import API, UpdateAuthorizationState

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env
load_dotenv()

# Получение переменных окружения
phone = os.getenv("PHONE")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
channel = os.getenv("CHANNEL")

# Проверка наличия обязательных переменных
if not all([phone, api_id, api_hash]):
    logger.error("Не заданы все переменные окружения (PHONE, API_ID, API_HASH)")
    sys.exit(1)

async def auth_handler(update: UpdateAuthorizationState, client: Client):
    """Обработчик авторизации"""
    auth_state = update.authorization_state
    if auth_state["@type"] == "authorizationStateWaitTdlibParameters":
        database_dir = os.path.abspath(f"sessions/tdlib/{phone}")
        os.makedirs(database_dir, exist_ok=True)
        await client.api.set_tdlib_parameters(
            api_id=int(api_id),
            api_hash=api_hash,
            database_directory=database_dir,
            use_message_database=True,
            use_secret_chats=True,
            system_language_code="en",
            device_model="Desktop",
            application_version="1.0"
        )
    elif auth_state["@type"] == "authorizationStateWaitPhoneNumber":
        await client.api.set_authentication_phone_number(phone_number=phone)
    elif auth_state["@type"] == "authorizationStateWaitCode":
        code = input("Enter SMS code: ")
        await client.api.check_authentication_code(code=code)
    elif auth_state["@type"] == "authorizationStateReady":
        logger.info(f"[{phone}] Авторизация успешно завершена")

async def search_channel(client: Client, channel_name: str):
    """Поиск публичного канала по имени"""
    try:
        # Проверка состояния клиента
        me = await client.api.get_me()
        logger.info(f"[{phone}] Клиент авторизован как {me.first_name} {me.last_name or ''}")

        # Нормализация имени канала
        channel_name = channel_name if channel_name.startswith('@') else f"@{channel_name}"
        logger.info(f"[{phone}] Поиск канала: {channel_name}")

        # Поиск канала
        result = await client.api.search_public_chat(username=channel_name)
        if result and result.id:
            logger.info(f"[{phone}] Канал найден: {result.title} (ID: {result.id})")
            return result
        else:
            logger.warning(f"[{phone}] Канал {channel_name} не найден")
            return None
    except Exception as e:
        logger.error(f"[{phone}] Ошибка при поиске канала: {str(e)}")
        return None

async def main():
    """Основная функция"""
    client = Client(settings=ClientSettings(api_id=int(api_id), api_hash=api_hash, phone_number=phone))
    client.add_event_handler(auth_handler, update_type=API.Types.UPDATE_AUTHORIZATION_STATE)

    try:
        # Запуск клиента
        logger.info(f"[{phone}] Запуск сессии...")
        await client.start()

        # Поиск канала
        if channel:
            logger.info(f"[{phone}] Переменная CHANNEL: {channel}")
            chat = await search_channel(client, channel)
            if chat:
                logger.info(f"[{phone}] Успешно найден канал: {chat.title}")
            else:
                logger.warning(f"[{phone}] Канал {channel} не найден")
        else:
            logger.warning(f"[{phone}] Переменная CHANNEL не задана")

    except Exception as e:
        logger.error(f"[{phone}] Ошибка в main: {str(e)}")
    finally:
        try:
            await client.stop()
        except asyncio.CancelledError:
            logger.info("Клиент остановлен с отменой, продолжаем.")

if __name__ == "__main__":
    asyncio.run(main())