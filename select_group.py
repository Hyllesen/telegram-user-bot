#!/usr/bin/env python3
"""
Interactive group selection script for Telegram User Bot.
Run this script to select which group chat to monitor.
"""

import asyncio
import os
import json
from telethon import TelegramClient
from telethon.errors import AuthKeyError
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Define the path for storing the selected group
SELECTED_GROUP_FILE = Path("selected_group.json")

async def select_target_group():
    """Interactively select a target group from the user's chats"""
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')

    if not api_id or not api_hash:
        raise ValueError("Missing required environment variables: API_ID or API_HASH")

    print("Connecting to Telegram to fetch your chats...")
    
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

    try:
        # Connect and authenticate
        await client.connect()

        if not await client.is_user_authorized():
            print("Session is not authorized. Please run setup_session.py first.")
            return

        print("Fetching your chats...")
        
        # Get all dialogs (chats)
        dialogs = await client.get_dialogs()
        
        # Filter out only groups/channels/private chats
        groups = []
        for dialog in dialogs:
            # Include groups, channels, and private chats (but not the user's own chat)
            if (hasattr(dialog.entity, 'megagroup') or 
                hasattr(dialog.entity, 'broadcast') or 
                dialog.is_user) and dialog.name != 'Saved Messages':
                
                # Format the group info for display
                group_info = {
                    'name': dialog.name,
                    'id': dialog.id,
                    'entity': dialog.entity
                }
                
                # For megagroups, determine the full ID format
                if hasattr(dialog.entity, 'megagroup') and dialog.entity.megagroup:
                    full_group_id = int(f"-100{dialog.entity.id}")
                    group_info['full_id'] = full_group_id
                
                groups.append(group_info)

        if not groups:
            print("No groups or channels found in your account.")
            return

        print(f"\nFound {len(groups)} chats. Select one to monitor:\n")
        
        # Display the groups with indices
        for i, group in enumerate(groups, 1):
            print(f"{i}. {group['name']} (ID: {group['id']})")
            
            # Show the full ID for megagroups if available
            if 'full_id' in group:
                print(f"   Full ID: {group['full_id']} (use this for megagroups)")

        print(f"\n{len(groups) + 1}. Enter group ID manually")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{len(groups) + 1}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(groups):
                    # User selected a group from the list
                    selected_group = groups[choice_idx]
                    
                    # Determine which ID to use
                    if 'full_id' in selected_group:
                        selected_id = selected_group['full_id']
                        print(f"Selected: {selected_group['name']} (Full ID: {selected_id})")
                    else:
                        selected_id = selected_group['id']
                        print(f"Selected: {selected_group['name']} (ID: {selected_id})")
                    
                    break
                elif choice_idx == len(groups):
                    # User wants to enter ID manually
                    manual_id = input("Enter the group ID manually: ").strip()
                    try:
                        selected_id = int(manual_id)
                        print(f"Selected group with ID: {selected_id}")
                        break
                    except ValueError:
                        print("Invalid ID format. Please enter a numeric ID.")
                        continue
                else:
                    print(f"Please enter a number between 1 and {len(groups) + 1}")
            except ValueError:
                print(f"Please enter a number between 1 and {len(groups) + 1}")

        # Save the selected group ID to the persistent storage
        save_selected_group(selected_id)
        
        print(f"\nSelected group ID {selected_id} has been saved successfully!")
        print("The bot will now monitor this group when restarted.")

    except AuthKeyError:
        print("Authentication error. Please run setup_session.py to set up your session.")
    except Exception as e:
        print(f"Error during group selection: {e}")
    finally:
        await client.disconnect()


def save_selected_group(group_id):
    """Save the selected group ID to a persistent file"""
    try:
        with SELECTED_GROUP_FILE.open('w') as f:
            json.dump({'group_id': group_id}, f)
    except Exception as e:
        print(f"Error saving selected group: {e}")
        raise


def load_selected_group():
    """Load the selected group ID from the persistent file"""
    try:
        if SELECTED_GROUP_FILE.exists():
            with SELECTED_GROUP_FILE.open('r') as f:
                data = json.load(f)
                return data.get('group_id')
        return None
    except Exception as e:
        print(f"Error loading selected group: {e}")
        return None


def remove_selected_group():
    """Remove the selected group file (reset to default)"""
    try:
        if SELECTED_GROUP_FILE.exists():
            SELECTED_GROUP_FILE.unlink()
            print("Selected group has been reset. The bot will now use the TARGET_GROUP_CHAT_ID from .env")
    except Exception as e:
        print(f"Error removing selected group: {e}")


if __name__ == "__main__":
    asyncio.run(select_target_group())