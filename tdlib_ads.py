import asyncio
from aiotdlib import Client
from config import API_ID, API_HASH

async def get_sponsored_url(channel_username: str, phone_number: str):
    client = Client(
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number
    )

    async with client:
        chat = await client.api.search_public_chat(username=channel_username)
        sponsored = await client.api.get_chat_sponsored_message(chat_id=chat.id)

        if sponsored and sponsored.content and getattr(sponsored.content, "url", None):
            print(f"[✓] Рекламная ссылка: {sponsored.content.url}")
            return sponsored.content.url
        else:
            print("[✗] Реклама не найдена.")
            return None
