# Telegram User Bot

This is a Telegram bot that monitors groups and extracts store information from images using OCR. It also detects Temu share URLs and extracts keywords from them.

## Prerequisites

Before running the application, you need to set up your Telegram API credentials:

1. Create a `.env` file in the root directory with the following content:
```
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
```

Note: You must run the interactive group selection once before running the main bot. The TARGET_GROUP_CHAT_ID is no longer used from the .env file.

## Features

- Monitors Telegram groups for new messages
- Downloads images and extracts store names using OCR
- Detects Temu share URLs (https://share.temu.com/) in text messages
- Extracts keywords from Temu share URLs
- Processes images with EasyOCR to extract store names

## Running with Docker

### Setup Telegram Session (Required):

Before running the main application, you need to authenticate and create a session file:

```bash
docker-compose run setup-session
```

This will prompt you for your phone number and the login code sent to your Telegram. Run this in an environment where you can interact with it.

### Select Target Group (Optional but Recommended):

Instead of hardcoding the TARGET_GROUP_CHAT_ID in your .env file, you can interactively select which group to monitor:

```bash
docker-compose run telegram-bot python main.py --select-group
```

This will connect to your Telegram account, list all accessible groups/channels, and allow you to select one to monitor. The selection will be saved and remembered for future runs.

### Build and run the main application:

```bash
docker-compose up telegram-bot
```

### Run the test script:

```bash
docker-compose run test-extractor
```

### Or run both services:

```bash
docker-compose up
```

## Running without Docker

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Setup Telegram Session (Required):

Before running the main application, you need to authenticate and create a session file:

```bash
python setup_session.py
```

This will prompt you for your phone number and the login code sent to your Telegram. Run this in an environment where you can interact with it.

### Select Target Group (Optional but Recommended):

Instead of hardcoding the TARGET_GROUP_CHAT_ID in your .env file, you can interactively select which group to monitor:

```bash
python main.py --select-group
```

This will connect to your Telegram account, list all accessible groups/channels, and allow you to select one to monitor. The selection will be saved and remembered for future runs.

### Run the main application:

```bash
python main.py
```

### Run the image extractor test:

```bash
python test_temu_extractor_easyocr.py
```

### Run the Temu keyword extractor test:

```bash
python test_temu_keyword_extractor.py https://share.temu.com/example
```

## Modules

### temu_extractor_easyocr.py
Processes images and extracts store names using EasyOCR.

### temu_keyword_extractor.py
Extracts keywords from Temu share URLs by scraping HTML meta tags.

### telegram_client.py
Main Telegram client that monitors groups, downloads images, and processes both images and text messages.

## Notes

- The `group_images` directory is used to store images downloaded from the monitored Telegram group
- The OCR functionality uses EasyOCR to extract store names from images
- The keyword extraction functionality scrapes meta tags from Temu share URLs
- Make sure your `.env` file is properly configured before running the application
- You must run `python main.py --select-group` once to select which group to monitor before running the main application