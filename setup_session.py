#!/usr/bin/env python3
"""
Authentication setup script for Telegram User Bot.
Run this script in an environment where you can interact with it to set up your session.
"""

import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def setup_session():
    """Set up the Telegram session"""
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    
    if not api_id or not api_hash:
        raise ValueError("Missing required environment variables: API_ID or API_HASH")
    
    print("Setting up Telegram session...")
    print("You will be prompted for your phone number and the login code sent to your Telegram.")
    
    # Create client with the same session name as the main bot
    client = TelegramClient(
        'session_name',
        api_id,
        api_hash,
        device_model='Telegram User Bot',
        system_version='1.0',
        app_version='8.0',
        lang_code='en',
        system_lang_code='en'
    )
    
    # Connect and authenticate
    await client.connect()
    
    if not await client.is_user_authorized():
        print("User is not authorized. Starting authentication process...")
        await client.start()
        print("Authentication successful! Session has been saved.")
    else:
        print("User is already authorized. Session is valid.")
    
    # Test the connection
    try:
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username if me.username else 'N/A'})")
        print("Session setup completed successfully!")
    except Exception as e:
        print(f"Error verifying session: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_session())