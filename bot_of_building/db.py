import sqlite3
from pathlib import Path
from traceback import print_exc
from typing import List

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db.db"
# коннектимся к БД.
def connect(func):
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(str(DB_DIR))
        cur = conn.cursor()
        result = None

        try:
            result = func(cur, *args, **kwargs)
            conn.commit()
        except Exception:
            print(f"[ERROR] {func.__name__}: {print_exc()}")
            conn.rollback()
        finally:
            conn.close()
        return result
    return wrapper
# создаём таблицу, если её нет.
@connect
def create_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                user_id INTEGER UNIQUE,
                age INTEGER DEFAULT 'не указан',
                city TEXT DEFAULT 'не указан',
                reg_date DATE NOT NULL
                )""")
# добавляем пользователя.
@connect
def insert_user(cur, name : str, reg_date : str, user_id : int):
    cur.execute("""INSERT OR REPLACE INTO users(name, reg_date, user_id)
                VALUES (?, ?, ?)
                """, (name, reg_date, user_id))
# получаем айди всех пользователей.
@connect
def get_users_id(cur) -> List[int]:
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    
    return [row[0] for row in rows]
# изменяем город и возраст пользователя.
@connect
def set_age_city(cur, user_id : int, age : int, city : str):
    cur.execute("UPDATE users SET age = ?, city = ? WHERE user_id = ?", (age, city, user_id))
# возвращаем информацию о пользователе.
@connect
def get_all_user_info(cur, user_id : int) -> List:
    cur.execute("SELECT name, age, city, reg_date FROM users WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()

    return [r for row in rows for r in row]

if __name__ == "__main__":
    # create_table()
    # insert_user("Максим", 5)
    # insert_user("Дима", 6)
    # set_age_city(5, 12, "Пружаны")
    # lists = get_all_user_info(5)
    # print(lists)
    pass