from telethon import TelegramClient
from telethon.errors import (
    ChatWriteForbiddenError,
    ChannelPrivateError
)
import asyncio
import os
import datetime


# =========================
# CONFIGURATION
# =========================

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
MESSAGE = os.environ["MESSAGE"]

client = TelegramClient(
    "session",
    api_id,
    api_hash,
    connection_retries=5,
    retry_delay=5
)


# =========================
# LOAD GROUPS
# =========================

def load_groups():
    with open("groups.txt", "r") as f:
        return [
            x.strip()
            for x in f
            if x.strip()
        ]


# =========================
# SAVE VALID GROUPS
# =========================

def save_groups(groups):
    with open("groups.txt", "w") as f:
        for group in groups:
            f.write(group + "\n")


# =========================
# LOGGING
# =========================

def log(text):
    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    print(f"[{timestamp}] {text}", flush=True)


# =========================
# CONNECT WITH RETRIES
# =========================

async def connect_with_retry(max_retries=6):

    for attempt in range(1, max_retries + 1):

        try:
            log(
                f"Connecting to Telegram... "
                f"attempt {attempt}/{max_retries}"
            )

            await client.connect()

            if not await client.is_user_authorized():
                log("✗ Telegram session is not authorized")
                return False

            log("✓ Successfully connected to Telegram")

            return True

        except Exception as e:

            log(
                f"⚠ Connection failed | "
                f"{type(e).__name__}: {e}"
            )

            try:
                await client.disconnect()
            except Exception:
                pass

            if attempt == max_retries:
                log(
                    "✗ Could not connect to Telegram "
                    "after all retries"
                )
                return False

            delay = min(10 * attempt, 60)

            log(
                f"Retrying connection in {delay} seconds..."
            )

            await asyncio.sleep(delay)

    return False


# =========================
# SEND MESSAGES
# =========================

async def send_messages():

    valid_groups = []

    # Connect to Telegram
    connected = await connect_with_retry()

    if not connected:
        log("✗ Telegram connection failed")
        return

    try:

        groups = load_groups()

        log(
            f"Loaded {len(groups)} groups from groups.txt"
        )

        for index, group in enumerate(groups, start=1):

            log(
                f"Processing group "
                f"{index}/{len(groups)}: {group}"
            )

            try:

                msg = await client.send_message(
                    group,
                    MESSAGE
                )

                log(
                    f"✓ SENT | "
                    f"group={group} | "
                    f"message_id={msg.id}"
                )

                valid_groups.append(group)

                # Wait between messages
                await asyncio.sleep(16)

            except ChatWriteForbiddenError:

                log(
                    f"✗ REMOVED | "
                    f"no permission | "
                    f"group={group}"
                )

            except ChannelPrivateError:

                log(
                    f"✗ REMOVED | "
                    f"private/inaccessible | "
                    f"group={group}"
                )

            except Exception as e:

                log(
                    f"⚠ SKIPPED | "
                    f"group={group} | "
                    f"error={type(e).__name__}: {e}"
                )

                # Keep the group in the file
                valid_groups.append(group)

    finally:

        log("Disconnecting from Telegram...")

        try:
            await client.disconnect()
        except Exception as e:
            log(f"⚠ Disconnect error: {e}")

    # Save remaining groups
    save_groups(valid_groups)

    log(
        f"Finished. "
        f"Remaining groups: {len(valid_groups)}"
    )


# =========================
# START
# =========================

if __name__ == "__main__":

    try:
        asyncio.run(send_messages())

    except KeyboardInterrupt:
        log("Script stopped manually.")

    except Exception as e:
        log(
            f"✗ Fatal error | "
            f"{type(e).__name__}: {e}"
        )
        raise
