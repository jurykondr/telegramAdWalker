import asyncio
import re
from typing import Optional

from aiotdlib import Client
from aiotdlib.client_settings import ClientSettings
from aiotdlib.api import (
    GetChatSponsoredMessages,
    ClickChatSponsoredMessage,
    JoinChatByInviteLink,
    SearchPublicChat,
    SendMessage,
    InputMessageText,
    FormattedText,
)


class TdlibClient:
    def __init__(self, phone: str, api_id: int, api_hash: str, session_path: str, proxy: Optional[dict] = None):
        self.phone = phone
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_path = session_path
        self.proxy = proxy
        self.client: Optional[Client] = None

    async def create_client(self):
        settings = ClientSettings(
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone_number=self.phone,
            database_directory=f"{self.session_path}/tdlib/{self.phone}/db",
            files_directory=f"{self.session_path}/tdlib/{self.phone}/files",
            use_file_database=True,
            use_chat_info_database=True,
            use_message_database=True,
            use_secret_chats=False,
            system_language_code="en",
            device_model="Linux",
            application_version="1.0",
            enable_storage_optimizer=True,
            ignore_file_names=True,
            use_test_dc=False
        )

        self.client = Client(settings)
        await self.client.start()
        print(f"[INFO] Авторизация прошла успешно: {self.phone}")

    async def get_sponsored_message(self, chat_id: int):
        try:
            return await self.client.send(GetChatSponsoredMessages(chat_id=chat_id))
        except Exception as e:
            print(f"[ERROR] Не удалось получить рекламу: {e}")
            return None

    async def click_sponsored_message(self, chat_id: int, message_id: int):
        try:
            await self.client.send(ClickChatSponsoredMessage(chat_id=chat_id, message_id=message_id))
            print(f"[INFO] Клик по рекламе выполнен: {chat_id} {message_id}")
        except Exception as e:
            print(f"[ERROR] Не удалось кликнуть рекламу: {e}")

    async def join_chat(self, invite_link: str):
        try:
            await self.client.send(JoinChatByInviteLink(invite_link=invite_link))
            print(f"[INFO] Присоединились к каналу: {invite_link}")
        except Exception as e:
            if "USER_ALREADY_PARTICIPANT" in str(e):
                print(f"[INFO] Уже подписан: {invite_link}")
            else:
                print(f"[ERROR] Ошибка при подписке на канал: {invite_link} — {e}")

    async def start_bot(self, username: str):
        try:
            bot = await self.client.send(SearchPublicChat(username=username))
            await self.client.send(
                SendMessage(
                    chat_id=bot.id,
                    input_message_content=InputMessageText(
                        text=FormattedText(text="/start", entities=[]),
                        clear_draft=True
                    )
                )
            )
            print(f"[INFO] Отправлен /start боту @{username}")
        except Exception as e:
            print(f"[ERROR] Не удалось отправить /start боту @{username}: {e}")

    async def handle_sponsored_link(self, url: str):
        if "t.me" not in url:
            print(f"[WARN] Неизвестный формат ссылки: {url}")
            return

        invite_match = re.search(r"t\.me/joinchat/(\S+)", url)
        bot_match = re.search(r"t\.me/(\w+)\?start=", url)
        channel_match = re.search(r"t\.me/(\w+)$", url)

        try:
            if bot_match:
                username = bot_match.group(1)
                await self.start_bot(username)
            elif invite_match:
                invite = invite_match.group(1)
                await self.join_chat(f"https://t.me/joinchat/{invite}")
            elif channel_match:
                username = channel_match.group(1)
                await self.join_chat(f"https://t.me/{username}")
            else:
                print(f"[WARN] Не удалось распознать ссылку: {url}")
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке ссылки: {url} — {e}")

    async def stop(self):
        if self.client:
            try:
                await self.client.stop()
            except asyncio.CancelledError:
                print(f"[WARN] CancelledError во время остановки клиента {self.phone} — игнорируем")
            print(f"[INFO] Сессия завершена: {self.phone}")
