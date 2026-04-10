import sqlite3
from pathlib import Path
from traceback import print_exc
from typing import List, Literal

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
# создаём таблицы, если их нет.
@connect
def create_table(cur) -> None:
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                user_id INTEGER UNIQUE,
                age INTEGER DEFAULT 'не указан',
                city TEXT DEFAULT 'не указан',
                reg_date DATE NOT NULL
                )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS captcha(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                action_captcha INTEGER NOT NULL DEFAULT 0,
                numb INTEGER DEFAULT 0
                )""")
# добавляем пользователя.
@connect
def insert_user(cur, name : str, reg_date : str, user_id : int) -> None:
    cur.execute("""INSERT OR IGNORE INTO users(name, reg_date, user_id)
                VALUES (?, ?, ?)
                """, (name, reg_date, user_id))
    
    cur.execute("""INSERT OR IGNORE INTO captcha(user_id)
                VALUES (?)
                """, (user_id,))
# получаем айди всех пользователей.
@connect
def get_users_id(cur) -> List[int]:
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    
    return [row[0] for row in rows]
# изменяем город и возраст пользователя.
@connect
def set_age_city(cur, user_id : int, age : int, city : str) -> None:
    cur.execute("UPDATE users SET age = ?, city = ? WHERE user_id = ?", (age, city, user_id))
# возвращаем информацию о пользователе.
@connect
def get_all_user_info(cur, user_id : int) -> List:
    cur.execute("SELECT name, age, city, reg_date FROM users WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()

    return [r for row in rows for r in row]
# возвращаем поле истинности капчи.
@connect
def get_info_captcha(cur, user_id : int) -> List:
    """return the state of the captcha active and numb on captcha."""
    cur.execute("SELECT action_captcha, numb FROM captcha WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()

    return [row for row in rows[0]]
# изменяем число в капче и поле истинности.
@connect
def set_state_captcha(cur, user_id : int, numb : int, res : Literal[0, 1]) -> None:
    """numb is a numb on this captcha; res is a state of the captcha(0 -> disactive, 1 -> active)."""
    cur.execute("UPDATE captcha SET numb = ?, action_captcha = ? WHERE user_id = ?", (numb, res, user_id))

if __name__ == "__main__":
    # create_table()
    # insert_user("Максим", "2026-07-23", 5)
    # insert_user("Дима", 6)
    # set_age_city(5, 12, "Пружаны")
    # lists = get_all_user_info(5)
    # print(lists)
    # set_state_captcha(5, 1451246, 1)
    # print(get_state_captcha(5))
    pass