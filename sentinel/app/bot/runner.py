"""aiogram Bot and Dispatcher setup supporting polling and webhook modes."""

import logging
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, Update
from sentinel.app.config import Settings, get_settings
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.db import async_session_maker

logger = logging.getLogger(__name__)


def create_bot(settings: Optional[Settings] = None) -> Optional[Bot]:
    s = settings or get_settings()
    if not s.TELEGRAM_BOT_TOKEN:
        return None
    return Bot(token=s.TELEGRAM_BOT_TOKEN)


def create_dispatcher(handler: Optional[BotCommandHandler] = None) -> Dispatcher:
    dp = Dispatcher()
    cmd_handler = handler or BotCommandHandler()
    settings = get_settings()

    async def check_auth(message: Message) -> bool:
        # ponytail: simple list check guards the bot against unauthorized callers
        if settings.ALLOWED_TELEGRAM_USER_IDS and message.from_user:
            if message.from_user.id not in settings.ALLOWED_TELEGRAM_USER_IDS:
                await message.reply("⛔ Access restricted. You are not on the allowlist.")
                return False
        return True

    async def safe_reply(message: Message, text: str, parse_mode: Optional[str] = "HTML"):
        try:
            await message.reply(text, parse_mode=parse_mode)
        except Exception:
            try:
                await message.reply(text)
            except Exception as e:
                logger.error("Failed to send message: %s", e)

    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_start(message.from_user.id if message.from_user else 0)
        await safe_reply(message, resp, parse_mode="HTML")

    @dp.message(Command("today"))
    @dp.message(Command("digest"))
    async def cmd_today(message: Message):
        if not await check_auth(message):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_today(session, user_id=user_id)
        await safe_reply(message, resp, parse_mode="HTML")

    @dp.message(Command("important"))
    async def cmd_important(message: Message):
        if not await check_auth(message):
            return
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_important(session)
        await safe_reply(message, resp, parse_mode="HTML")

    @dp.message(Command("why"))
    async def cmd_why(message: Message):
        if not await check_auth(message):
            return
        topic = message.text.replace("/why", "").strip() if message.text else ""
        resp = await cmd_handler.handle_why(topic)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("compare"))
    async def cmd_compare(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/compare", "").strip() if message.text else ""
        resp = await cmd_handler.handle_compare(args)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("implement"))
    async def cmd_implement(message: Message):
        if not await check_auth(message):
            return
        tech = message.text.replace("/implement", "").strip() if message.text else ""
        resp = await cmd_handler.handle_implement(tech)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("roadmap"))
    async def cmd_roadmap(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_roadmap()
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("hardware"))
    async def cmd_hardware(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_hardware()
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("fit"))
    async def cmd_fit(message: Message):
        if not await check_auth(message):
            return
        model = message.text.replace("/fit", "").strip() if message.text else ""
        resp = await cmd_handler.handle_fit(model)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("deps"))
    async def cmd_deps(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/deps", "").strip() if message.text else ""
        resp = await cmd_handler.handle_deps(args)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("lab"))
    async def cmd_lab(message: Message):
        if not await check_auth(message):
            return
        topic = message.text.replace("/lab", "").strip() if message.text else ""
        resp = await cmd_handler.handle_lab(topic)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("work"))
    async def cmd_work(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/work", "").strip() if message.text else ""
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_work(args, session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("learned"))
    async def cmd_learned(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/learned", "").strip() if message.text else ""
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_learned(args, session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("career"))
    async def cmd_career(message: Message):
        if not await check_auth(message):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_career(session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("interests"))
    async def cmd_interests(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/interests", "").strip() if message.text else ""
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_interests(args, session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("win"))
    async def cmd_win(message: Message):
        if not await check_auth(message):
            return
        title = message.text.replace("/win", "").strip() if message.text else ""
        resp = await cmd_handler.handle_win(title)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("quiz"))
    async def cmd_quiz(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_quiz()
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("review"))
    async def cmd_review(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_review()
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("memory"))
    async def cmd_memory(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/memory", "").strip() if message.text else ""
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_memory(args, session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("clear"))
    async def cmd_clear(message: Message):
        if not await check_auth(message):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_clear(session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("review_arch"))
    @dp.message(Command("roast"))
    async def cmd_review_arch(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/review_arch", "/roast"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_review_arch(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("reproduce"))
    async def cmd_reproduce(message: Message):
        if not await check_auth(message):
            return
        topic = message.text.replace("/reproduce", "").strip() if message.text else ""
        resp = await cmd_handler.handle_reproduce(topic)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("interview"))
    async def cmd_interview(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/interview", "").strip() if message.text else ""
        resp = await cmd_handler.handle_interview(args)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("brag"))
    @dp.message(Command("promo"))
    async def cmd_promo(message: Message):
        if not await check_auth(message):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_promo(session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_help()
        await safe_reply(message, resp, parse_mode=None)

    @dp.message()
    async def handle_conversational_chat(message: Message):
        """Conversational AI: speaks naturally, remembers multi-turn context and long-term user facts."""
        if not await check_auth(message):
            return
        if not message.text or message.text.startswith("/"):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_conversation(message.text, session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    return dp
