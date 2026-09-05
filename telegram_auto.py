from telethon import TelegramClient
from telethon.errors import ChatWriteForbiddenError, ChannelPrivateError
import asyncio
import os
import datetime

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
MESSAGE = os.environ["MESSAGE"]

client = TelegramClient("session", api_id, api_hash)


def load_groups():
    with open("groups.txt") as f:
        return [x.strip() for x in f if x.strip()]


def save_groups(groups):
    with open("groups.txt", "w") as f:
        for g in groups:
            f.write(g + "\n")


def log(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {text}")


async def send_messages():
    valid_groups = []

    async with client:
        for group in load_groups():
            try:
                msg = await client.send_message(group, MESSAGE)
                log(f"✓ SENT | group={group} | message_id={msg.id}")

                await asyncio.sleep(16)
                valid_groups.append(group)

            except (ChatWriteForbiddenError, ChannelPrivateError):
                log(f"✗ REMOVED | no permission | group={group}")

            except Exception as e:
                log(f"⚠ SKIPPED | group={group} | error={e}")
                valid_groups.append(group)

    save_groups(valid_groups)


asyncio.run(send_messages())
