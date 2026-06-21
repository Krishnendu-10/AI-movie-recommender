import os
import asyncio
from telethon import TelegramClient, functions

# --- YOUR CREDENTIALS & PATHS ---
API_ID = 32445563
API_HASH = '7af811e3dcafaec28d10fc186c38f8bd'
SOURCE_FOLDER = r"D:\backup\lenovo_backup\10_09_2025\MOVIES\7zip"

client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    print("Connecting to Telegram...")
    await client.start()
    print("Connected!")

    # 1. Create a Standard Private Supergroup (No broken Forum flags required)
    print("Creating a new private group...")
    created_group = await client(functions.channels.CreateChannelRequest(
        title="My Movies Backup",
        about="Automated folder backup using Threads",
        megagroup=True
    ))
    
    group = created_group.chats[0]
    print(f"Group '{group.title}' created successfully.")

    # 2. Iterate through the source folder
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: The path {SOURCE_FOLDER} does not exist.")
        return

    subfolders = [f for f in os.listdir(SOURCE_FOLDER) if os.path.isdir(os.path.join(SOURCE_FOLDER, f))]

    for folder_name in subfolders:
        folder_path = os.path.join(SOURCE_FOLDER, folder_name)
        
        # 3. Create the "Thread Starter" message for this folder
        print(f"\nCreating thread for folder: {folder_name}")
        thread_starter = await client.send_message(
            entity=group,
            message=f"📁 **{folder_name}**\nAll files for this subfolder are inside this thread."
        )

        # 4. Iterate and upload files directly into the thread
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not files:
            print(f"  No files found in '{folder_name}'.")
            continue

        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            print(f"  Uploading: {file_name} ...")
            
            try:
                # The 'reply_to' parameter puts the file neatly inside the folder's thread
                await client.send_file(
                    entity=group,
                    file=file_path,
                    reply_to=thread_starter.id,
                    caption=file_name 
                )
                print(f"  ✅ Successfully uploaded {file_name}")
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Failed to upload {file_name}. Error: {e}")

    print("\nBackup complete!")

with client:
    client.loop.run_until_complete(main())