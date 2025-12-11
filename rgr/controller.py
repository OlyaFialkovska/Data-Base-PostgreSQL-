
from typing import Any
import psycopg.errors
from psycopg.errors import ForeignKeyViolation, UniqueViolation, NotNullViolation, CheckViolation

import model
import view


def run():
    while True:  # головний цикл — вибір таблиці
        print("\n=== Список таблиць ===")
        keys = list(model.SCHEMA.keys())
        for i, t in enumerate(keys, start=1):
            print(f"{i}) {t}")
        print("7) Вийти")

        try:
            k = int(input("Оберіть таблицю (номер): ").strip())
        except ValueError:
            print("Невірний вибір. Спробуйте ще раз.")
            continue

        # вихід з програми
        if k == 7:
            print("👋 Програму завершено.")
            break

        # перевірка діапазону
        if not (1 <= k <= len(keys)):
            print("Невірний вибір. Спробуйте ще раз.")
            continue

        table = keys[k - 1]

        # меню дій для вибраної таблиці
        while True:
            choice = input(view.MAIN_MENU).strip()

            # 1Перегляд
            if choice == '1':
                rows = model.list_all(table)
                print(f"\n{table} ({len(rows)} рядків):")
                for r in rows:
                    print(r)
                print()

            # 2Додавання
            elif choice == '2':
                try:
                    data = view.ask_new_row(table)
                    model.insert_row(table, data)
                    print("+Додано.")
                except UniqueViolation:
                    print("!!!Порушення унікальності (PK або унікальний ключ).")
                except ForeignKeyViolation:
                    print("!!!Порушення зовнішнього ключа (немає пов’язаного запису у батьківській таблиці).")
                except NotNullViolation:
                    print("!!!Обов’язкове поле не може бути порожнім.")
                except CheckViolation:
                    print("!!!Порушення обмеження CHECK.")
                except ValueError as ve:
                    print(f"!!!Помилка валідації: {ve}")
                except Exception as e:
                    print(f"!!!Невідома помилка: {e}")

            # 3Редагування
            elif choice == '3':
                pk = model.SCHEMA[table].get('pk')
                if not pk:
                    print("Для цієї таблиці редагування через PK не підтримано (складний ключ).")
                    continue
                pk_val = input(f"Введіть значення {pk}: ")
                try:
                    updates = view.ask_updates(table)
                    if not updates:
                        print("Нічого не змінено.")
                        continue
                    count = model.update_row(table, pk, pk_val, updates)
                    if count == 0:
                        print("Запис не знайдено.")
                    else:
                        print("+Оновлено.")
                except ForeignKeyViolation:
                    print("!!!Порушення зовнішнього ключа.")
                except ValueError as ve:
                    print(f"!!!Помилка валідації: {ve}")
                except Exception as e:
                    print(f"!!!Невідома помилка: {e}")

            # 4Видалення
            elif choice == '4':
                pk = model.SCHEMA[table].get('pk')
                if not pk:
                    print("Видалення через PK не підтримано (складний ключ).")
                    continue
                pk_val = input(f"Введіть значення {pk} для видалення: ")
                try:
                    count = model.delete_row(table, pk, pk_val)
                    if count == 0:
                        print("Запис не знайдено.")
                    else:
                        print("+Видалено.")
                except (ForeignKeyViolation, psycopg.errors.RestrictViolation):
                    print("!!!Неможливо видалити: існують залежні записи в дочірній таблиці (RESTRICT).")
                except Exception as e:
                    print(f"!!!Невідома помилка: {e}")
            # 5Пошук даних
            elif choice == '5':
                while True:
                    print("""
            === МЕНЮ ПОШУКУ ===
            1) Пошук проєктів за діапазоном дат
            2) Пошук фрілансерів за частиною прізвища
            3) Підрахунок кількості проєктів на кожній платформі
            4) Назад
            """)
                    sub = input("Виберіть пункт: ").strip()

                    # Запит 1
                    if sub == '1':
                        start_date = input("Введіть початкову дату (YYYY-MM-DD): ")
                        end_date = input("Введіть кінцеву дату (YYYY-MM-DD): ")
                        try:
                            rows, ms = model.search_projects_by_date_range(start_date, end_date)
                            for r in rows:
                                print(r)
                            print(f"⏱ Час виконання: {ms:.2f} мс")
                        except Exception as e:
                            print("!!!Помилка під час виконання запиту:", e)

                    # Запит 2
                    elif sub == '2':
                        pattern = input("Введіть частину прізвища (наприклад, %ov%): ")
                        try:
                            rows, ms = model.search_freelancers_by_surname_like(pattern)
                            for r in rows:
                                print(r)
                            print(f"⏱ Час виконання: {ms:.2f} мс")
                        except Exception as e:
                            print("!!!Помилка під час виконання запиту:", e)

                    # Запит 3
                    elif sub == '3':
                        name_like = input("Введіть частину назви платформи (наприклад, %free%): ")
                        try:
                            rows, ms = model.count_projects_by_platform(name_like)
                            for r in rows:
                                print(r)
                            print(f"⏱ Час виконання: {ms:.2f} мс")
                        except Exception as e:
                            print("!!!Помилка під час виконання запиту:", e)

                    elif sub == '4':
                        break
                    else:
                        print("Невірний вибір. Спробуйте ще.")

            # 6Назад — повернення до списку таблиць
            elif choice == '6':
                break

            else:
                print("Невірний вибір. Спробуйте ще раз.")