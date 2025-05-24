import re
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import StartBotRequest
from config import API_ID, API_HASH, SESSION_DIR

def parse_tg_link(link):
    """Определяет тип ссылки и извлекает имя."""
    if "t.me/" not in link:
        return None, None

    clean_link = link.split("t.me/")[-1].strip("/")
    if '?' in clean_link:
        username, param = clean_link.split('?', 1)
        return 'bot', (username, param)
    elif clean_link.startswith('+'):
        return 'invite', clean_link
    else:
        return 'channel', clean_link

async def perform_action(phone: str, link: str):
    session_path = SESSION_DIR + phone.replace('+', '')
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        await client.start()
        action_type, payload = parse_tg_link(link)

        if action_type == 'channel':
            print(f"[{phone}] Присоединяемся к каналу: {payload}")
            await client(JoinChannelRequest(payload))
        elif action_type == 'bot':
            bot_username, param = payload
            print(f"[{phone}] Запускаем бота: @{bot_username}")
            await client(StartBotRequest(bot_username, param=param, start_param=''))
        elif action_type == 'invite':
            print(f"[{phone}] Присоединение по invite-ссылке пока не реализовано.")
        else:
            print(f"[{phone}] Неподдерживаемая или внешняя ссылка: {link}")
    except Exception as e:
        print(f"[{phone}] ❌ Ошибка: {e}")
    finally:
        await client.disconnect()
