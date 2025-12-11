# view.py
# ----------------------------------------
# Відповідає за взаємодію з користувачем (View у MVC)
# Виведення меню, таблиць, результатів пошуку
# ----------------------------------------

def choose_table(tables):
    """Вибір таблиці користувачем."""
    print("\n=== ВИБІР ТАБЛИЦІ ===")
    tables = list(tables)

    for i, t in enumerate(tables, start=1):
        print(f"{i}) {t}")

    print("0) Вихід")

    choice = input("Виберіть номер таблиці: ").strip()

    if choice == '0':
        return None

    if choice.isdigit() and 1 <= int(choice) <= len(tables):
        return tables[int(choice) - 1]

    print("❌ Невірний вибір.")
    return None


def table_menu(table: str):
    """Меню дій для вибраної таблиці."""
    print(f"\n=== ТАБЛИЦЯ {table} ===")
    print("1) Переглянути всі записи")
    print("2) Додати новий запис")
    print("3) Редагувати запис")
    print("4) Видалити запис")
    print("5) Назад")
    print("6) Пошук даних")

    return input("Виберіть опцію: ").strip()


def show_rows(rows):
    """Виводить список рядків у зручному вигляді."""
    print("\n=== РЕЗУЛЬТАТИ ===")

    if not rows:
        print("Немає записів для відображення.")
        return

    for row in rows:
        print(row)

    print(f"---- Виведено записів: {len(rows)} ----")


# -------------------------------
# Меню пошуку
# -------------------------------

def search_menu():
    print("\n=== МЕНЮ ПОШУКУ ===")
    print("1) Пошук проєктів за діапазоном дат")
    print("2) Пошук фрілансерів за частиною прізвища")
    print("3) Підрахунок кількості проєктів на кожній платформі")
    print("4) Назад")

    return input("Виберіть пункт: ").strip()
