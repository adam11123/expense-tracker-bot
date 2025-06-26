import aiosqlite
from datetime import date

DB_PATH = "expenses.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL
            );
        """)
        await db.commit()


async def add_expense(user_id: int, amount: int):
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO expenses (user_id, amount, date) VALUES (?, ?, ?)",
            (user_id, amount, today)
        )
        await db.commit()

async def get_monthly_report(user_id: int, year: int, month: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT date, amount FROM expenses
            WHERE user_id = ?
              AND strftime('%Y-%m', date) = ?
            ORDER BY date;
        """, (user_id, f"{year}-{month:02d}"))
        rows = await cursor.fetchall()
    return rows


async def get_total_for_current_month(user_id: int):
    today = date.today()
    year_month = today.strftime('%Y-%m')
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT SUM(amount) FROM expenses
            WHERE user_id = ?
              AND strftime('%Y-%m', date) = ?;
        """, (user_id, year_month))
        row = await cursor.fetchone()
        return row[0] or 0
