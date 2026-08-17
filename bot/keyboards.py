from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def session_kb() -> InlineKeyboardMarkup:
    """Меню выбора режима занятия."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🃏 Карточки", callback_data="session:cards"),
                InlineKeyboardButton(text="💬 Диалог", callback_data="session:dialog"),
            ],
            [InlineKeyboardButton(text="➕ Добавить слово в словарь", callback_data="session:add_word")],
        ]
    )


def stop_kb() -> InlineKeyboardMarkup:
    """Кнопка выхода из активной сессии."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏹ Завершить", callback_data="session:stop")]
        ]
    )