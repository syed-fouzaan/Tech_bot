"""aiogram Bot and Dispatcher setup supporting polling and webhook modes."""

import logging
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, Update, CallbackQuery
from sentinel.app.config import Settings, get_settings
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.bot.keyboards import get_quick_actions_keyboard
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

    async def safe_reply(message: Message, text: str, parse_mode: Optional[str] = "HTML", reply_markup=None):
        try:
            await message.reply(text, parse_mode=parse_mode, reply_markup=reply_markup)
        except Exception:
            try:
                await message.reply(text, reply_markup=reply_markup)
            except Exception as e:
                logger.error("Failed to send message: %s", e)

    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        if not await check_auth(message):
            return
        resp = await cmd_handler.handle_start(message.from_user.id if message.from_user else 0)
        await safe_reply(message, resp, parse_mode="HTML", reply_markup=get_quick_actions_keyboard())

    @dp.message(Command("today"))
    @dp.message(Command("digest"))
    async def cmd_today(message: Message):
        if not await check_auth(message):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_today(session, user_id=user_id)
        await safe_reply(message, resp, parse_mode="HTML", reply_markup=get_quick_actions_keyboard())

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

    @dp.message(Command("drill"))
    @dp.message(Command("incident"))
    async def cmd_drill(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/drill", "/incident"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_drill(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("pr_review"))
    @dp.message(Command("diff"))
    async def cmd_pr_review(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/pr_review", "/diff"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_pr_review(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("roi"))
    @dp.message(Command("migrate"))
    async def cmd_roi(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/roi", "/migrate"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_roi(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("status"))
    @dp.message(Command("one_on_one"))
    async def cmd_status(message: Message):
        if not await check_auth(message):
            return
        user_id = message.from_user.id if message.from_user else 0
        async with async_session_maker() as session:
            resp = await cmd_handler.handle_status(session, user_id=user_id)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("pattern"))
    async def cmd_pattern(message: Message):
        if not await check_auth(message):
            return
        args = message.text.replace("/pattern", "").strip() if message.text else ""
        resp = await cmd_handler.handle_pattern(args)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("optimize_sql"))
    async def cmd_optimize_sql(message: Message):
        if not await check_auth(message):
            return
        text = message.text.replace("/optimize_sql", "").strip() if message.text else ""
        resp = await cmd_handler.handle_optimize_sql(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("calc_cost"))
    @dp.message(Command("tokens"))
    async def cmd_calc_cost(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/calc_cost", "/tokens"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_calc_cost(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("runbook"))
    async def cmd_runbook(message: Message):
        if not await check_auth(message):
            return
        service = message.text.replace("/runbook", "").strip() if message.text else ""
        resp = await cmd_handler.handle_runbook(service)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("data_ninja"))
    @dp.message(Command("transform"))
    async def cmd_data_ninja(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/data_ninja", "/transform"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_data_ninja(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("soundbite"))
    async def cmd_soundbite(message: Message):
        if not await check_auth(message):
            return
        topic = message.text.replace("/soundbite", "").strip() if message.text else ""
        resp = await cmd_handler.handle_soundbite(topic)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("profile_script"))
    @dp.message(Command("debug_code"))
    async def cmd_profile_script(message: Message):
        if not await check_auth(message):
            return
        text = message.text or ""
        for prefix in ["/profile_script", "/debug_code"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        resp = await cmd_handler.handle_profile_script(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("guardrails"))
    async def cmd_guardrails(message: Message):
        if not await check_auth(message):
            return
        text = message.text.replace("/guardrails", "").strip() if message.text else ""
        resp = await cmd_handler.handle_guardrails(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("parse_log"))
    async def cmd_parse_log(message: Message):
        if not await check_auth(message):
            return
        text = message.text.replace("/parse_log", "").strip() if message.text else ""
        resp = await cmd_handler.handle_parse_log(text)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("run_py"))
    async def cmd_run_py(message: Message):
        if not await check_auth(message):
            return
        code = message.text.replace("/run_py", "").strip() if message.text else ""
        resp = await cmd_handler.handle_run_py(code)
        await safe_reply(message, resp, parse_mode=None)

    @dp.message(Command("gen_tests"))
    async def cmd_gen_tests(message: Message):
        if not await check_auth(message):
            return
        code = message.text.replace("/gen_tests", "").strip() if message.text else ""
        resp = await cmd_handler.handle_gen_tests(code)
        await safe_reply(message, resp, parse_mode=None)

    @dp.callback_query()
    async def handle_callback_actions(call: CallbackQuery):
        """Processes 1-tap interactive inline keyboard button actions."""
        if not call.message:
            return
        try:
            await call.answer()
        except Exception:
            pass

        action = call.data
        if action == "act_reproduce":
            resp = await cmd_handler.handle_reproduce("vllm")
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_soundbite":
            resp = await cmd_handler.handle_soundbite("Speculative Decoding")
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_status":
            user_id = call.from_user.id if call.from_user else 0
            async with async_session_maker() as session:
                resp = await cmd_handler.handle_status(session, user_id=user_id)
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_pattern":
            resp = await cmd_handler.handle_pattern()
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_drill":
            resp = await cmd_handler.handle_drill()
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_ninja":
            resp = await cmd_handler.handle_data_ninja("")
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_sql":
            resp = await cmd_handler.handle_optimize_sql("")
            await safe_reply(call.message, resp, parse_mode=None)
        elif action == "act_cost":
            resp = await cmd_handler.handle_calc_cost("5000 gpt-4o-mini")
            await safe_reply(call.message, resp, parse_mode=None)

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
