# Налаштування підключення до бази даних PostgreSQL.

PG_DSN = (
    "host=localhost "        # або IP сервера (наприклад: 127.0.0.1)
    "port=5432 "             # стандартний порт PostgreSQL
    "dbname=postgres "       # назва твоєї бази даних (заміни, якщо інша)
    "user=apple "            # ім'я користувача PostgreSQL
    "password=fialkaolya08"  # пароль користувача
)

# Перевірка підключення:
if __name__ == "__main__":
    import psycopg
    try:
        with psycopg.connect(PG_DSN) as conn:
            print("Підключення до бази даних успішне.")
    except Exception as e:
        print("!Помилка підключення:", e)
