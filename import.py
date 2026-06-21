import os
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, ToggleForumRequest, CreateForumTopicRequest
from telethon.tl.types import UpdateNewChannelMessage

# --- YOUR CREDENTIALS & PATHS ---
API_ID = 32445563
API_HASH = '7af811e3dcafaec28d10fc186c38f8bd'
SOURCE_FOLDER = r"D:\backup\lenovo_backup\10_09_2025\MOVIES\7zip"

# Initialize the Telegram Client
# 'session_name' creates a local file to save your login so you don't have to log in every time
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    print("Connecting to Telegram...")
    await client.start()
    print("Connected!")

    # 1. Create a Private Supergroup (megagroup=True is required for Forums)
    print("Creating a new private group...")
    created_group = await client(CreateChannelRequest(
        title="My Movies Backup",
        about="Automated folder backup with topics",
        megagroup=True
    ))
    
    # Extract the group entity so we can interact with it
    group = created_group.chats[0]
    print(f"Group '{group.title}' created successfully.")

    # 2. Enable the 'Forum' (Topics) feature in the group
    await client(ToggleForumRequest(channel=group, enabled=True))
    print("Enabled Forum topics in the group.")

    # 3. Iterate through the source folder
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: The path {SOURCE_FOLDER} does not exist.")
        return

    # List only directories (subfolders) in the base path
    subfolders = [f for f in os.listdir(SOURCE_FOLDER) if os.path.isdir(os.path.join(SOURCE_FOLDER, f))]

    for folder_name in subfolders:
        folder_path = os.path.join(SOURCE_FOLDER, folder_name)
        
        # 4. Create a Forum Topic for this subfolder
        print(f"\nCreating topic for folder: {folder_name}")
        topic_result = await client(CreateForumTopicRequest(
            channel=group,
            title=folder_name
        ))

        # We need the ID of the newly created topic to send files into it
        # Telegram returns an 'Updates' object; we find the message ID that created the topic
        topic_id = None
        for update in topic_result.updates:
            if isinstance(update, UpdateNewChannelMessage):
                topic_id = update.message.id
                break
        
        if not topic_id:
            print(f"Failed to get Topic ID for {folder_name}. Skipping...")
            continue

        # 5. Iterate through files in this subfolder and upload them
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not files:
            print(f"  No files found in '{folder_name}'.")
            continue

        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            print(f"  Uploading: {file_name} ...")
            
            try:
                # Send the file to the specific group, replying to the topic ID
                await client.send_file(
                    entity=group,
                    file=file_path,
                    reply_to=topic_id,
                    caption=file_name # Optional: adds the filename as a text caption
                )
                print(f"  ✅ Successfully uploaded {file_name}")
                
                # Sleep briefly to avoid triggering Telegram's spam/flood limits
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Failed to upload {file_name}. Error: {e}")

    print("\nBackup complete!")

# Run the asynchronous main function
with client:
    client.loop.run_until_complete(main())