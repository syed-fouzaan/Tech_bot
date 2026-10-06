"""Telegram Webhook receiver router."""

from fastapi import APIRouter, Header, HTTPException, Request
from aiogram.types import Update
from sentinel.app.config import get_settings
from sentinel.app.bot.runner import create_bot, create_dispatcher

router = APIRouter(prefix="/telegram", tags=["Telegram"])
settings = get_settings()
bot = create_bot(settings)
dispatcher = create_dispatcher()


@router.post("/webhook/{secret_token}")
async def telegram_webhook(
    secret_token: str,
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None),
):
    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook path secret")

    if x_telegram_bot_api_secret_token and x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Telegram header secret")

    data = await request.json()
    if bot:
        update = Update.model_validate(data, context={"bot": bot})
        await dispatcher.feed_update(bot, update)

    return {"ok": True}
