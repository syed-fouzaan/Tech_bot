import asyncio
import logging
import sys
import os

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aiogram import Bot
from sentinel.app.config import get_settings
from sentinel.app.db.session import init_db, async_session_maker
from sentinel.app.bot.runner import create_dispatcher
from sentinel.app.services.ingestion.service import IngestionService
from sentinel.app.bot.handlers import BotCommandHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sentinel.launcher")


async def main():
    settings = get_settings()

    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN.strip() == "":
        logger.error(
            "\n" + "=" * 65 + "\n"
            "❌ TELEGRAM_BOT_TOKEN is missing in sentinel/.env\n\n"
            "Quick 30-second setup:\n"
            "1. Open Telegram and search for @BotFather\n"
            "2. Send /newbot and choose a name and username (e.g. 'MySentinelBot')\n"
            "3. Copy the HTTP API token BotFather gives you\n"
            "4. Paste it into sentinel/.env as:\n"
            "   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz\n"
            "=" * 65 + "\n"
        )
        sys.exit(1)

    logger.info("1. Initializing database schema...")
    await init_db()

    logger.info("2. Triggering live source ingestion (arXiv, HF Hub, GitHub, RSS, HN)...")
    ingestion = IngestionService()
    async with async_session_maker() as session:
        try:
            stats = await ingestion.ingest_and_process(session, limit=6)
            logger.info("   Ingestion complete! Funnel: %s", stats)
        except Exception as e:
            logger.warning("   Ingestion skipped or offline: %s", e)

    logger.info("3. Initializing Telegram Bot and Dispatcher...")
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    cmd_handler = BotCommandHandler()
    dp = create_dispatcher(cmd_handler)

    bot_info = await bot.get_me()
    logger.info(
        "\n" + "=" * 65 + "\n"
        f"🤖 Bot is LIVE on Telegram: @{bot_info.username}\n"
        "Send /start or /today in Telegram to receive your live intelligence brief!\n"
        "=" * 65 + "\n"
    )

    try:
        # Start polling for incoming messages
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
