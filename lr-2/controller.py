# controller.py
# ----------------------------------------
# Логіка роботи програми (Controller у MVC)
# Керує взаємодією між View та Model
# ----------------------------------------

import model
import view


def run():
    """Головний цикл програми."""
    while True:
        table = view.choose_table(model.SCHEMA.keys())
        if table is None:
            print("Завершення роботи...")
            return
        table_menu(table)


def table_menu(table: str):
    """Меню для вибраної таблиці."""
    while True:
        choice = view.table_menu(table)

        # 1. ПЕРЕГЛЯД
        if choice == '1':
            rows = model.list_all(table)
            view.show_rows(rows)

        # 2. ДОДАВАННЯ
        elif choice == '2':
            data = {}
            for col, type_decl in model.SCHEMA[table]['columns'].items():
                raw = input(f"Введіть значення для '{col}': ")
                try:
                    data[col] = model.parse_value(type_decl, raw)
                except Exception as e:
                    print("❌ Помилка валідації:", e)
                    break
            else:
                try:
                    model.insert_row(table, data)
                    print("✅ Рядок успішно додано.")
                except Exception as e:
                    print("❌ Помилка додавання:", e)

        # 3. РЕДАГУВАННЯ
        elif choice == '3':
            pk_name = model.SCHEMA[table]['pk']
            pk_value = input(f"Введіть {pk_name} рядка, який хочете змінити: ")

            updates = {}
            for col, type_decl in model.SCHEMA[table]['columns'].items():
                if col == pk_name:
                    continue
                raw = input(f"Нове значення для '{col}' (Enter — пропустити): ")
                if raw.strip() == "":
                    continue
                try:
                    updates[col] = model.parse_value(type_decl, raw)
                except Exception as e:
                    print("❌ Помилка валідації:", e)
                    break
            else:
                try:
                    count = model.update_row(table, pk_name, pk_value, updates)
                    if count > 0:
                        print("✅ Рядок успішно оновлено.")
                    else:
                        print("⚠️ Рядок не знайдено.")
                except Exception as e:
                    print("❌ Помилка оновлення:", e)

        # 4. ВИДАЛЕННЯ
        elif choice == '4':
            pk_name = model.SCHEMA[table]['pk']
            pk_value = input(f"Введіть {pk_name} рядка, який хочете видалити: ")
            try:
                count = model.delete_row(table, pk_name, pk_value)
                if count > 0:
                    print("🗑️ Рядок видалено.")
                else:
                    print("⚠️ Рядок не знайдено.")
            except Exception as e:
                print("❌ Неможливо видалити запис:", e)

        # 5. НАЗАД
        elif choice == '5':
            return

        # 6. ПОШУК
        elif choice == '6':
            search_menu()

        else:
            print("⚠️ Невірна опція. Спробуйте ще.")


# -------------------------------
# МЕНЮ ПОШУКУ
# -------------------------------

def search_menu():
    while True:
        s = view.search_menu()

        # --- ЗАПИТ 1 ---
        if s == '1':
            start_date = input("Початкова дата (YYYY-MM-DD): ")
            end_date = input("Кінцева дата (YYYY-MM-DD): ")
            try:
                rows, ms = model.search_projects_by_date_range(start_date, end_date)
                view.show_rows(rows)
                print(f"⏱ Час виконання: {ms:.2f} мс")
            except Exception as e:
                print("❌ Помилка:", e)

        # --- ЗАПИТ 2 ---
        elif s == '2':
            pattern = input("Введіть шаблон прізвища (наприклад: %ov%): ")
            try:
                rows, ms = model.search_freelancers_by_surname_like(pattern)
                view.show_rows(rows)
                print(f"⏱ Час виконання: {ms:.2f} мс")
            except Exception as e:
                print("❌ Помилка:", e)

        # --- ЗАПИТ 3 ---
        elif s == '3':
            text = input("Частина назви платформи: ")
            try:
                rows, ms = model.count_projects_by_platform(text)
                view.show_rows(rows)
                print(f"⏱ Час виконання: {ms:.2f} мс")
            except Exception as e:
                print("❌ Помилка:", e)

        # --- НАЗАД ---
        elif s == '4':
            return

        else:
            print("⚠️ Невірний пункт меню.")


