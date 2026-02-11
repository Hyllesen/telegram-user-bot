import asyncio
from telegram_client import TelegramGroupMonitor
import signal
import sys

def signal_handler(sig, frame):
    print('\nShutting down gracefully...')
    sys.exit(0)

async def main():
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