import psycopg
from config import PG_DSN

try:
    with psycopg.connect(PG_DSN) as conn:
        print("+Підключення до бази даних успішне!")
except Exception as e:
    print("!!!Помилка підключення:", e)
