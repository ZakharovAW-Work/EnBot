from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import db
from keyboards import stop_kb

router = Router()

class Cards(StatesGroup):
    ask = State()

@router.message(Command("cards"))
async def cards_cmd(msg: Message, state):
    await start_cards(msg, state, msg.from_user.id)

async def start_cards(message, state, chat_id):   # вызывается и из callback-кнопки
    due = await db.due_words(chat_id)
    if not due:
        await message.answer("Нет слов для повторения 🎉"); return
    await state.set_state(Cards.ask)
    await state.update_data(queue=[dict(w) for w in due])
    await ask_next(message, state)

async def ask_next(message, state):
    queue = (await state.get_data())["queue"]
    await state.update_data(current=queue[0])
    await message.answer(f"Переведите: <b>{queue[0]['ru']}</b>", reply_markup=stop_kb())

@router.message(Cards.ask, F.text)
async def answer(msg: Message, state):
    data = await state.get_data()
    word, queue = data["current"], data["queue"][1:]
    ok = msg.text.strip().lower() == word["en"].lower()
    await db.review_result(msg.from_user.id, word["id"], ok)
    await msg.answer(f"{'✅ Верно' if ok else '❌ Правильно'}: <b>{word['en']}</b>")
    if not queue:
        await state.clear()
        await msg.answer("Сессия окончена! До следующего повторения 😉")
    else:
        await state.update_data(queue=queue)
        await ask_next(msg, state)