from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
import db
from keyboards import session_kb
from handlers.cards import start_cards
from handlers.dialog import start_dialog

router = Router()
START_PHRASES = {"начать", "урок", "занятие", "start"}

class AddWord(StatesGroup):
    wait_ru = State()

@router.message(CommandStart())
async def on_start(msg: Message):
    await db.add_user_if_missing(msg.from_user.id)   # + стартовый набор слов через db.learn_word
    await msg.answer("Привет! Напиши «начать» или выбери режим:", reply_markup=session_kb())

@router.callback_query(F.data.startswith("session:"))
async def session_choice(cq: CallbackQuery, state):
    mode = cq.data.split(":")[1]
    await cq.answer()
    if mode == "stop":
        await state.clear(); await cq.message.answer("Сессия завершена ✅"); return
    if mode == "cards": await start_cards(cq.message, state, cq.from_user.id)
    else:               await start_dialog(cq.message, state, cq.from_user.id)

@router.message(Command("add"))   # /add cat
async def add_cmd(msg: Message, state):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2: await msg.answer("Формат: /add cat"); return
    await state.set_state(AddWord.wait_ru)
    await state.update_data(en=parts[1].strip().lower())
    await msg.answer("Перевод на русский?")

@router.message(AddWord.wait_ru, F.text)
async def add_ru(msg: Message, state):
    en = (await state.get_data())["en"]
    await db.learn_word(msg.from_user.id, en, msg.text.strip())
    await state.clear()
    await msg.answer(f"Слово <b>{en}</b> в словаре ✅")

@router.message(F.text)   # ловит свободный текст ВНЕ сессий (роутер включён последним!)
async def free_text(msg: Message, state):
    if await state.get_state() is not None: return
    if msg.text.strip().lower() in START_PHRASES:
        await msg.answer("Что будем делать?", reply_markup=session_kb())