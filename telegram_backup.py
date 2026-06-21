"""
Telegram Group + Topics Auto-Uploader
--------------------------------------
Creates a Telegram supergroup with "Topics" (forum) enabled,
then for each subfolder in SOURCE_FOLDER, creates a topic with
that subfolder's name and uploads all files inside it to that topic.

Requirements:
    pip install telethon

Run:
    python upload_to_telegram.py
"""

import os
import asyncio
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError

# ============== CONFIG ==============
API_ID = 32445563
API_HASH = '7af811e3dcafaec28d10fc186c38f8bd'
SOURCE_FOLDER = r"D:\backup\lenovo_backup\10_09_2025\MOVIES\7zip"

GROUP_TITLE = "My Movie Backup"
GROUP_DESCRIPTION = "Auto-created backup group"

SESSION_NAME = "uploader_session"

# Telegram free account upload limit per file
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB

# Delay between file uploads (helps avoid flood limits on free accounts)
UPLOAD_DELAY_SECONDS = 5
# ======================================


client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def progress_callback(current, total, filename):
    percent = current / total * 100
    print(f"\r  Uploading {filename}: {percent:6.2f}% ({current}/{total} bytes)", end="")


async def create_group_with_topics():
    await client.start()

    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (id={me.id})")

    # 1. Create a megagroup (supergroup)
    print(f"\nCreating supergroup: {GROUP_TITLE}")
    result = await client(functions.channels.CreateChannelRequest(
        title=GROUP_TITLE,
        about=GROUP_DESCRIPTION,
        megagroup=True
    ))

    # Get the channel object
    channel = result.chats[0]
    channel_entity = await client.get_entity(channel.id)
    print(f"Group created: {channel_entity.title} (id={channel_entity.id})")

    # 2. Enable "Topics" (forum) feature on the group
    print("Enabling Topics (forum) mode...")
    await client(functions.channels.ToggleForumRequest(
        channel=channel_entity,
        enabled=True
    ))

    await asyncio.sleep(2)

    # 3. Iterate over subfolders -> create topic + upload files
    if not os.path.isdir(SOURCE_FOLDER):
        print(f"ERROR: Source folder does not exist: {SOURCE_FOLDER}")
        return

    subfolders = [
        f for f in os.listdir(SOURCE_FOLDER)
        if os.path.isdir(os.path.join(SOURCE_FOLDER, f))
    ]

    if not subfolders:
        print("No subfolders found in source folder.")
        return

    print(f"\nFound {len(subfolders)} subfolders.\n")

    for folder_name in subfolders:
        folder_path = os.path.join(SOURCE_FOLDER, folder_name)
        print(f"=== Processing folder: {folder_name} ===")

        # Create a forum topic named after the subfolder
        try:
            topic_result = await client(functions.channels.CreateForumTopicRequest(
                channel=channel_entity,
                title=folder_name,
                icon_color=0x6FB9F0  # arbitrary blue color
            ))
        except FloodWaitError as e:
            print(f"FloodWait: sleeping {e.seconds}s before creating topic...")
            await asyncio.sleep(e.seconds)
            topic_result = await client(functions.channels.CreateForumTopicRequest(
                channel=channel_entity,
                title=folder_name,
                icon_color=0x6FB9F0
            ))

        # Extract the topic's message id (top_id) - needed for sending to that topic
        topic_msg_id = None
        for update in topic_result.updates:
            if isinstance(update, types.UpdateMessageID):
                topic_msg_id = update.id
                break
            if hasattr(update, "message") and hasattr(update.message, "id"):
                topic_msg_id = update.message.id

        if topic_msg_id is None:
            print(f"  WARNING: could not determine topic id for '{folder_name}', skipping uploads.")
            continue

        print(f"  Topic created with id: {topic_msg_id}")

        # 4. List files in this subfolder (non-recursive; change to os.walk for recursive)
        files = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        if not files:
            print("  No files in this folder.")
            continue

        for filename in files:
            filepath = os.path.join(folder_path, filename)
            filesize = os.path.getsize(filepath)

            if filesize > MAX_FILE_SIZE:
                print(f"  SKIPPING {filename} - exceeds {MAX_FILE_SIZE / (1024**3):.1f} GB limit")
                continue

            print(f"  Uploading: {filename} ({filesize / (1024*1024):.2f} MB)")

            try:
                await client.send_file(
                    channel_entity,
                    filepath,
                    caption=filename,
                    reply_to=topic_msg_id,  # send into this topic's thread
                    progress_callback=lambda c, t, fn=filename: asyncio.create_task(
                        progress_callback(c, t, fn)
                    ),
                    force_document=True,  # avoids re-encoding/compression for media
                )
                print()  # newline after progress bar
            except FloodWaitError as e:
                print(f"\n  FloodWait: sleeping {e.seconds}s...")
                await asyncio.sleep(e.seconds)
                # retry once
                await client.send_file(
                    channel_entity,
                    filepath,
                    caption=filename,
                    reply_to=topic_msg_id,
                    force_document=True,
                )
            except Exception as e:
                print(f"\n  ERROR uploading {filename}: {e}")

            # Throttle to be gentle on free account limits
            await asyncio.sleep(UPLOAD_DELAY_SECONDS)

        print(f"=== Done with folder: {folder_name} ===\n")

    print("All done!")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(create_group_with_topics())