import asyncio
import argparse
from telegram_client import TelegramGroupMonitor
from select_group import select_target_group
import signal
import sys

def signal_handler(sig, frame):
    print('\nShutting down gracefully...')
    sys.exit(0)

async def main():
    parser = argparse.ArgumentParser(description='Telegram User Bot')
    parser.add_argument('--select-group', action='store_true', 
                        help='Run in group selection mode to choose which group to monitor')
    args = parser.parse_args()

    if args.select_group:
        # Run in group selection mode
        await select_target_group()
    else:
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)

        # Create and start the Telegram group monitor
        monitor = TelegramGroupMonitor()

        try:
            await monitor.start()
        except KeyboardInterrupt:
            print("\nStopping the client...")
            await monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())