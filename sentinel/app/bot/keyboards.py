"""Telegram inline keyboards for feedback, deeper insights, and quizzes."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_item_feedback_keyboard(item_id: str) -> InlineKeyboardMarkup:
    """Returns inline interactive feedback buttons for digest items."""
    buttons = [
        [
            InlineKeyboardButton(text="👍 Useful", callback_data=f"feed_pos:{item_id}"),
            InlineKeyboardButton(text="👎 Skip", callback_data=f"feed_neg:{item_id}"),
            InlineKeyboardButton(text="🔖 Save", callback_data=f"save:{item_id}"),
        ],
        [
            InlineKeyboardButton(text="🔬 Go Deeper", callback_data=f"deep:{item_id}"),
            InlineKeyboardButton(text="🧠 Learn This", callback_data=f"learn:{item_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quiz_options_keyboard(question_id: str, options: List[str]) -> InlineKeyboardMarkup:
    """Returns option buttons for daily interactive quizzes."""
    buttons = []
    for idx, opt in enumerate(options):
        # Truncate label for button
        label = opt[:30] + "..." if len(opt) > 30 else opt
        buttons.append([InlineKeyboardButton(text=f"{idx+1}. {label}", callback_data=f"quiz:{question_id}:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
