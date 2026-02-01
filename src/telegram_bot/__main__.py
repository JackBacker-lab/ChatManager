from telegram_bot.main import main

if __name__ == "__main__":
    import asyncio
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
