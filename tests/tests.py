import os
import asyncio
import logging
import asyncpg

from dotenv import load_dotenv
from asyncpg_lite import DatabaseManager
from sqlalchemy import Integer, String


DB_LINK = os.getenv("PG_LINK")
DB_PASS = os.getenv("PGPG_PASS_LINK")
DB_USER = os.getenv("DB_USER")

async def main():

    async with asyncpg.create_pool(
        'postgresql://postgres:123@localhost:5432/test_db'
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    '''
                    CREATE TABLE users(
                        id serial PRIMARY KEY,
                        name text,
                        dob date
                    )
                    '''
                )

asyncio.run(main())