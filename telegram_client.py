import os
import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import TypeNotFoundError, FloodWaitError, AuthKeyError
from dotenv import load_dotenv
import logging
from pathlib import Path
from datetime import datetime, timedelta
from temu_keyword_extractor import TemuKeywordExtractor
import time

# Load environment variables
load_dotenv()

class TelegramGroupMonitor:
    def __init__(self):
        # Get credentials from environment variables
        api_id = os.getenv('API_ID')
        api_hash = os.getenv('API_HASH')
        self.target_group_identifier = os.getenv('TARGET_GROUP_CHAT_ID')
        self.target_username = '@imelda87541'  # Target user to send matching images

        if not api_id or not api_hash or not self.target_group_identifier:
            raise ValueError("Missing required environment variables: API_ID, API_HASH, or TARGET_GROUP_CHAT_ID")

        # Convert to integer if it's a numeric string, otherwise keep as string
        try:
            self.target_group_chat_id = int(self.target_group_identifier)
        except ValueError:
            # If it's not a numeric ID, treat it as a username/channel name
            self.target_group_chat_id = self.target_group_identifier

        # Create images directory if it doesn't exist
        self.images_dir = Path("group_images")
        self.images_dir.mkdir(exist_ok=True)

        # Initialize the client with additional connection parameters
        self.client = TelegramClient(
            'session_name', 
            api_id, 
            api_hash,
            device_model='Telegram User Bot',
            system_version='1.0',
            app_version='8.0',
            lang_code='en',
            system_lang_code='en'
        )

        # Track previously seen message IDs to avoid duplicates
        self.seen_message_ids = set()

        # Track keywords that have been sent to avoid duplicates
        self.sent_keywords = set()

        # Connection management attributes
        self.last_reconnect_time = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 10  # seconds
        self.connection_health_check_interval = 300  # 5 minutes

        # Initialize the keyword extractor
        self.keyword_extractor = TemuKeywordExtractor()

    async def is_connected(self):
        """Check if the client is connected to Telegram"""
        try:
            # Attempt a lightweight operation to verify connection
            await self.client.get_me()
            return True
        except:
            return False

    async def reconnect(self):
        """Reconnect the client with exponential backoff"""
        current_time = time.time()
        
        # Check if we're within the reconnect delay period
        if current_time - self.last_reconnect_time < self.reconnect_delay:
            wait_time = self.reconnect_delay - (current_time - self.last_reconnect_time)
            print(f"Waiting {wait_time:.1f}s before attempting reconnection...")
            await asyncio.sleep(wait_time)
        
        # Check if we've exceeded max attempts
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"Maximum reconnection attempts ({self.max_reconnect_attempts}) reached. Stopping.")
            return False
        
        print(f"Attempting to reconnect... (attempt {self.reconnect_attempts + 1}/{self.max_reconnect_attempts})")
        
        try:
            # Disconnect first if connected
            if self.client.is_connected():
                await self.client.disconnect()
            
            # Reconnect
            await self.client.connect()
            
            # Re-authorize if needed
            if not await self.client.is_user_authorized():
                print("User authorization required after reconnection...")
                await self.client.start()
            
            # Reset reconnect attempts on success
            self.reconnect_attempts = 0
            self.last_reconnect_time = time.time()
            
            print("Reconnection successful!")
            return True
            
        except Exception as e:
            print(f"Reconnection failed: {e}")
            self.reconnect_attempts += 1
            # Exponential backoff: double the delay after each failed attempt
            self.reconnect_delay = min(self.reconnect_delay * 2, 300)  # Max 5 minutes
            return False
        
    async def start(self):
        """Start the Telegram client and begin listening for messages"""
        # Connect and authorize the client
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print("Session is not authorized. Please make sure you have a valid session.")
                print("If this is the first time running the bot, you'll need to authenticate manually.")
                print("Run this script in an environment where you can enter the login code when prompted.")
                await self.client.start()
            
            if not await self.client.is_user_authorized():
                raise Exception("User authorization failed. Please check your credentials.")
        except Exception as e:
            print(f"Error during initial connection: {e}")
            print("Attempting to reconnect with fresh session...")
            if not await self.reconnect():
                raise Exception("Could not establish connection after multiple attempts.")

        # Debug: List all dialogs to see accessible chats
        print("Fetching all accessible chats...")
        try:
            all_dialogs = await self.client.get_dialogs()
            print("Accessible chats:")
            for dialog in all_dialogs:
                print(f"Chat: {dialog.name}, ID: {dialog.id}")
        except Exception as e:
            print(f"Error fetching dialogs: {e}")

        # Also get the entity for the target group to verify it exists
        try:
            target_entity = await self.client.get_entity(self.target_group_chat_id)
            print(f"Target group entity: {target_entity}")
            print(f"Target group ID: {target_entity.id}")
            print(f"Target group title: {target_entity.title}")

            # For megagroups/channels, the full ID is typically in the format -100xxxxxxxxx
            if hasattr(target_entity, 'megagroup') and target_entity.megagroup:
                # For megagroups, the full ID is usually -100 + regular ID
                full_group_id = int(f"-100{target_entity.id}")
                print(f"Megagroup detected. Using full ID: {full_group_id}")

                # Update the target group chat ID to use the correct format
                self.target_group_chat_id = full_group_id
        except Exception as e:
            print(f"Error getting target group entity: {e}")
            print(f"Make sure the TARGET_GROUP_CHAT_ID '{self.target_group_chat_id}' is correct")
            return

        # Force refresh of the target entity with the updated ID
        try:
            target_entity = await self.client.get_entity(self.target_group_chat_id)
        except Exception as e:
            print(f"Error refreshing target entity: {e}")
            return

        # Start the periodic message fetching task
        fetch_task = asyncio.create_task(self.fetch_recent_messages_periodically())

        print(f"\nStarted periodic monitoring of group: {self.target_group_chat_id}")
        print("Checking for new messages every 5 minutes...")
        print("Press Ctrl+C to stop...")

        try:
            # Wait indefinitely until cancelled
            await fetch_task
        except asyncio.CancelledError:
            print("Monitoring task was cancelled")
    
    async def fetch_recent_messages_periodically(self):
        """Fetch recent messages from the target group every 5 minutes"""
        last_health_check = time.time()
        
        while True:
            try:
                # Perform connection health check periodically
                current_time = time.time()
                if current_time - last_health_check > self.connection_health_check_interval:
                    if not await self.is_connected():
                        print("Connection health check failed, attempting to reconnect...")
                        if not await self.reconnect():
                            print("Reconnection failed, waiting before next health check...")
                            await asyncio.sleep(self.connection_health_check_interval)
                            continue
                    last_health_check = current_time
                
                await self.fetch_recent_messages()
                # Wait for 5 minutes before next fetch
                await asyncio.sleep(300)  # 300 seconds = 5 minutes
            except Exception as e:
                print(f"Error in periodic message fetching: {e}")
                
                # Handle specific connection-related errors
                if isinstance(e, (TypeNotFoundError, AuthKeyError)):
                    print("Critical connection error detected, attempting reconnection...")
                    if not await self.reconnect():
                        print("Reconnection failed after critical error.")
                
                # Wait before retrying to avoid rapid error loops
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def fetch_recent_messages(self):
        """Fetch messages from the last 5 minutes"""
        try:
            # Calculate the time 5 minutes ago
            five_minutes_ago = datetime.now() - timedelta(minutes=5)

            # Get messages from the target group
            try:
                target_entity = await self.client.get_entity(self.target_group_chat_id)
            except (TypeNotFoundError, AuthKeyError) as e:
                print(f"Entity error: {e}. Attempting to reconnect...")
                if not await self.reconnect():
                    print("Reconnection failed, skipping this fetch cycle.")
                    return
                # Retry getting the entity after reconnection
                try:
                    target_entity = await self.client.get_entity(self.target_group_chat_id)
                except Exception as e:
                    print(f"Still unable to get target entity after reconnection: {e}")
                    return
            except Exception as e:
                print(f"Error getting target entity: {e}")
                return

            try:
                messages = await self.client.get_messages(
                    target_entity,
                    limit=50,  # Get up to 50 recent messages
                    offset_date=five_minutes_ago
                )
            except (TypeNotFoundError, AuthKeyError) as e:
                print(f"Message fetch error: {e}. Attempting to reconnect...")
                if not await self.reconnect():
                    print("Reconnection failed, skipping this fetch cycle.")
                    return
                # Retry fetching messages after reconnection
                try:
                    messages = await self.client.get_messages(
                        target_entity,
                        limit=50,
                        offset_date=five_minutes_ago
                    )
                except Exception as e:
                    print(f"Still unable to fetch messages after reconnection: {e}")
                    return
            except Exception as e:
                print(f"Error fetching messages: {e}")
                return

            print(f"Fetched {len(messages)} messages from the last 5 minutes")

            # Process each message
            for message in reversed(messages):  # Process in chronological order
                if message.id in self.seen_message_ids:
                    continue  # Skip already processed messages

                self.seen_message_ids.add(message.id)

                # Check if the message contains media (images)
                if message.media:
                    # Download the image
                    filename = f"group_images/image_{message.id}.jpg"
                    try:
                        await self.client.download_media(message.media, file=filename)
                        print(f"Image saved: {filename}")
                    except (TypeNotFoundError, AuthKeyError) as e:
                        print(f"Media download error: {e}. Attempting to reconnect...")
                        if not await self.reconnect():
                            print("Reconnection failed, skipping media download.")
                            continue
                        # Retry downloading media after reconnection
                        try:
                            await self.client.download_media(message.media, file=filename)
                            print(f"Image saved: {filename}")
                        except Exception as e:
                            print(f"Still unable to download media after reconnection: {e}")
                            continue
                    except Exception as e:
                        print(f"Error downloading media: {e}")
                        continue

                    # Run the ImageProcessor on the downloaded image
                    try:
                        from temu_extractor_easyocr import ImageProcessor
                        processor = ImageProcessor()

                        # Extract store name from the image
                        store_name = processor.process_image(filename)
                        print(f"Store name extracted: {store_name}")

                        # Check if store name matches any pending keywords
                        if store_name and hasattr(self, 'pending_keywords'):
                            matched_keyword = None
                            for keyword in self.pending_keywords:
                                if store_name.lower().startswith(keyword.lower()):
                                    matched_keyword = keyword
                                    break

                            if matched_keyword:
                                print(f"Store name '{store_name}' matches keyword '{matched_keyword}'")

                                # Check if this keyword has already been sent
                                if matched_keyword not in self.sent_keywords:
                                    # Send the image to @imelda87541
                                    await self.send_image_to_user(filename, store_name, matched_keyword)
                                else:
                                    print(f"Image for keyword '{matched_keyword}' already sent, skipping...")
                    except ImportError as e:
                        print(f"temu_extractor_easyocr module not found, skipping extraction: {e}")
                    except Exception as e:
                        print(f"Error running ImageProcessor: {e}")

                # Print text messages to console
                if message.text:
                    print(f"New message: {message.text}")

                    # Check for Temu share URLs that are at least 34 characters long
                    temu_url_pattern = r'https://share\.temu\.com/\S+'
                    temu_urls = re.findall(temu_url_pattern, message.text)

                    if temu_urls:
                        for url in temu_urls:
                            # Ensure the URL is at least 34 characters long
                            if len(url) >= 34:
                                exact_url = url[:34]  # Take exactly first 34 characters
                                print(f"Temu share URL detected (first 34 chars): {exact_url}")

                                # Extract keyword from the exact 34-character URL
                                try:
                                    keyword = self.keyword_extractor.extract_first_keyword(exact_url)
                                    if keyword:
                                        print(f"Extracted keyword from URL: {keyword}")

                                        # Add keyword to the list of keywords to match against store names
                                        # Store this in a way that can be accessed by the image processing section
                                        if not hasattr(self, 'pending_keywords'):
                                            self.pending_keywords = set()
                                        self.pending_keywords.add(keyword)
                                    else:
                                        print(f"No keyword found in URL: {exact_url}")
                                except Exception as e:
                                    print(f"Error extracting keyword from URL {exact_url}: {e}")
                            else:
                                print(f"Temu URL is shorter than 34 characters: {url} (length: {len(url)})")

        except (TypeNotFoundError, AuthKeyError) as e:
            print(f"Critical error in fetch_recent_messages: {e}. Attempting to reconnect...")
            if not await self.reconnect():
                print("Reconnection failed after critical error.")
        except Exception as e:
            print(f"Error fetching recent messages: {e}")
    
    async def send_image_to_user(self, image_path, store_name, keyword):
        """Send an image to the target user without a caption."""
        try:
            # Get the target user entity
            try:
                target_user = await self.client.get_entity(self.target_username)
            except (TypeNotFoundError, AuthKeyError) as e:
                print(f"Entity error when getting target user: {e}. Attempting to reconnect...")
                if not await self.reconnect():
                    print("Reconnection failed, skipping image send.")
                    return
                # Retry getting the entity after reconnection
                try:
                    target_user = await self.client.get_entity(self.target_username)
                except Exception as e:
                    print(f"Still unable to get target user after reconnection: {e}")
                    return

            # Send the image to the user without a caption
            try:
                await self.client.send_file(target_user, image_path)
            except (TypeNotFoundError, AuthKeyError) as e:
                print(f"Send file error: {e}. Attempting to reconnect...")
                if not await self.reconnect():
                    print("Reconnection failed, skipping image send.")
                    return
                # Retry sending the file after reconnection
                try:
                    await self.client.send_file(target_user, image_path)
                except Exception as e:
                    print(f"Still unable to send image after reconnection: {e}")
                    return

            # Add the keyword to the sent keywords set to prevent duplicate sends
            self.sent_keywords.add(keyword)

            print(f"Image sent to {self.target_username} (Keyword: {keyword})")
        except Exception as e:
            print(f"Error sending image to {self.target_username}: {e}")
    
    async def stop(self):
        """Stop the Telegram client"""
        if self.client.is_connected():
            await self.client.disconnect()
        print("Client disconnected successfully.")