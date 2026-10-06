"""Telegram Interactive Inline Keyboards for quick 1-tap actions."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """Returns a rich interactive keyboard for quick 1-tap engineering workflows."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔬 Reproduce Script", callback_data="act_reproduce"),
                InlineKeyboardButton(text="🎙️ Standup Soundbite", callback_data="act_soundbite"),
            ],
            [
                InlineKeyboardButton(text="👔 1:1 Status Update", callback_data="act_status"),
                InlineKeyboardButton(text="🏛️ Design Pattern", callback_data="act_pattern"),
            ],
            [
                InlineKeyboardButton(text="🚨 Incident Drill", callback_data="act_drill"),
                InlineKeyboardButton(text="🥷 Data Ninja", callback_data="act_ninja"),
            ],
            [
                InlineKeyboardButton(text="⚡ SQL Optimizer", callback_data="act_sql"),
                InlineKeyboardButton(text="💰 Token Budget", callback_data="act_cost"),
            ],
        ]
    )
    return keyboard
