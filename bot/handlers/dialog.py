import random, re
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import db
from keyboards import stop_kb

router = Router()

class Dialog(StatesGroup):
    talk = State()

SERVICE = {"i","you","he","she","it","we","they","do","does","is","are","am","the",
           "a","an","and","or","to","in","on","at","my","your","not","no","yes",
           "every","day","what","can","like","very","please"}

TEMPLATES = ["Do you like {noun}?", "Can you {verb}?", "Do you {verb} every day?",
             "Is the {noun} {adj}?", "What {noun} do you like?"]

def tokenize(t): return set(re.findall(r"[a-z']+", t.lower()))

def make_question(by_kind):
    usable = [t for t in TEMPLATES
              if all(by_kind.get(k) for k in re.findall(r"\{(\w+)\}", t))]
    t = random.choice(usable or ["Do you like English?"])
    return t.format(**{k: random.choice(by_kind[k]).lower()
                       for k in re.findall(r"\{(\w+)\}", t)})

@router.message(Command("chat"))
async def chat_cmd(msg: Message, state):
    await start_dialog(msg, state, msg.from_user.id)

async def start_dialog(message, state, chat_id):
    words = await db.known_words(chat_id)
    if not words:
        await message.answer("Словарь пуст — начните с карточек."); return
    by_kind = {}
    for w in words: by_kind.setdefault(w["kind"], []).append(w["en"])
    await state.set_state(Dialog.talk)
    await state.update_data(known_en=[w["en"].lower() for w in words], by_kind=by_kind)
    await message.answer("Пишем по-английски! Отвечайте предложениями.", reply_markup=stop_kb())
    await message.answer(make_question(by_kind))

@router.message(Dialog.talk, F.text)
async def talk(msg: Message, state):
    data = await state.get_data()
    unknown = tokenize(msg.text) - set(data["known_en"]) - SERVICE
    reply = random.choice(["Nice!", "Great!", "I see!"])
    if unknown:
        reply += f"\nНезнакомые слова: {', '.join(sorted(unknown))}. " \
                 f"Добавить в словарь? /add слово — перевод"
    await msg.answer(reply)
    await msg.answer(make_question(data["by_kind"]))