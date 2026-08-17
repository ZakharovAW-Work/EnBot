import aiosqlite
from datetime import date, timedelta

DB_PATH = "bot.db"
BOX_DAYS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    chat_id     INTEGER PRIMARY KEY,
    tz          TEXT NOT NULL DEFAULT 'Europe/Moscow',
    remind_time TEXT NOT NULL DEFAULT '18:00',
    last_remind TEXT
);
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en TEXT NOT NULL, ru TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'noun'   -- noun | verb | adj
);
CREATE TABLE IF NOT EXISTS user_words (
    chat_id INTEGER NOT NULL, word_id INTEGER NOT NULL,
    box INTEGER NOT NULL DEFAULT 1,
    next_review TEXT NOT NULL,          -- ISO-дата следующего повторения
    PRIMARY KEY (chat_id, word_id)
);
"""

async def init():
    async with aiosqlite.connect(DB_PATH) as con:
        await con.executescript(SCHEMA); await con.commit()

async def learn_word(chat_id, en, ru, kind="noun"):
    async with aiosqlite.connect(DB_PATH) as con:
        cur = await con.execute(
            "INSERT INTO words (en, ru, kind) VALUES (?,?,?)", (en, ru, kind))
        await con.execute(
            "INSERT OR IGNORE INTO user_words (chat_id, word_id, box, next_review) VALUES (?,?,1,?)",
            (chat_id, cur.lastrowid, date.today().isoformat()))
        await con.commit()

async def known_words(chat_id):
    async with aiosqlite.connect(DB_PATH) as con:
        con.row_factory = aiosqlite.Row
        cur = await con.execute("""
            SELECT w.id, w.en, w.ru, w.kind FROM user_words uw
            JOIN words w ON w.id = uw.word_id WHERE uw.chat_id = ?""", (chat_id,))
        return await cur.fetchall()

async def due_words(chat_id):   # слова, срок повторения которых настал
    async with aiosqlite.connect(DB_PATH) as con:
        con.row_factory = aiosqlite.Row
        cur = await con.execute("""
            SELECT w.id, w.en, w.ru FROM user_words uw
            JOIN words w ON w.id = uw.word_id
            WHERE uw.chat_id = ? AND uw.next_review <= ?""",
            (chat_id, date.today().isoformat()))
        return await cur.fetchall()

async def review_result(chat_id, word_id, ok: bool):
    async with aiosqlite.connect(DB_PATH) as con:
        cur = await con.execute(
            "SELECT box FROM user_words WHERE chat_id=? AND word_id=?", (chat_id, word_id))
        row = await cur.fetchone()
        box = (min(row[0] + 1, 5) if ok else 1) if row else 1
        next_rev = (date.today() + timedelta(days=BOX_DAYS[box])).isoformat()
        await con.execute("""
            INSERT INTO user_words (chat_id, word_id, box, next_review) VALUES (?,?,?,?)
            ON CONFLICT(chat_id, word_id)
            DO UPDATE SET box=excluded.box, next_review=excluded.next_review""",
            (chat_id, word_id, box, next_rev))
        await con.commit()

async def all_users():
    async with aiosqlite.connect(DB_PATH) as con:
        con.row_factory = aiosqlite.Row
        return await (await con.execute("SELECT * FROM users")).fetchall()

async def set_last_remind(chat_id, day):
    async with aiosqlite.connect(DB_PATH) as con:
        await con.execute("UPDATE users SET last_remind=? WHERE chat_id=?", (day, chat_id))
        await con.commit()