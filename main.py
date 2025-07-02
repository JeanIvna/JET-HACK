#!/usr/bin/env python3
"""
Main entry point for the Telegram gambling signals bot application (Render-ready).
Only runs the Telegram bot using long polling.
"""

import asyncio
import logging
from intelligent_bot import main as bot_main

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Starting Telegram bot (Render-ready, polling mode)...")
    await bot_main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")