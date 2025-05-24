import os
import asyncio
import random
from clicker import perform_action
from config import SESSION_DIR, MAX_CONCURRENT_TASKS

def get_all_sessions():
    return [
        f.replace(".session", "")
        for f in os.listdir(SESSION_DIR)
        if f.endswith(".session")
    ]

async def worker(phone, link, delay_range=(10, 30)):
    delay = random.uniform(*delay_range)
    print(f"[{phone}] Ждём {delay:.2f} сек перед действием...")
    await asyncio.sleep(delay)
    await perform_action(phone, link)

async def run_mass_click(link: str):
    phones = get_all_sessions()
    print(f"[INFO] Всего аккаунтов: {len(phones)}")

    sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def limited_worker(phone):
        async with sem:
            await worker(phone, link)

    await asyncio.gather(*(limited_worker(phone) for phone in phones))
