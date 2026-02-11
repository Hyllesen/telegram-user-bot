# Telegram User Bot

This is a Telegram bot that monitors groups and extracts store information from images using OCR. It also detects Temu share URLs and extracts keywords from them.

## Prerequisites

Before running the application, you need to set up your Telegram API credentials:

1. Create a `.env` file in the root directory with the following content:
```
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
TARGET_GROUP_CHAT_ID=your_target_group_chat_id
```

## Features

- Monitors Telegram groups for new messages
- Downloads images and extracts store names using OCR
- Detects Temu share URLs (https://share.temu.com/) in text messages
- Extracts keywords from Temu share URLs
- Processes images with EasyOCR to extract store names

## Running with Docker

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