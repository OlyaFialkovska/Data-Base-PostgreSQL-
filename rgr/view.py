from typing import Dict, Any, List, Optional
from model import SCHEMA

MAIN_MENU = """
------Меню дій-----
1) Переглянути всі рядки таблиці
2) Додати рядок
3) Редагувати рядок
4) Видалити рядок
5) Пошук даних
6) Назад

Виберіть опцію: """

def choose_table() -> str:
    keys = list(SCHEMA.keys())
    print("Доступні таблиці:")
    for i, t in enumerate(keys, start=1):
        print(f"{i}) {t}")
    while True:
        try:
            k = int(input("Оберіть номер таблиці: "))
            if 1 <= k <= len(keys):
                return keys[k-1]
        except:
            pass
        print("Такого номеру не існує. Спробуйте ще.")

def ask_pk(table: str) -> Any:
    pk = SCHEMA[table]['pk']
    if not pk:
        print("У таблиці немає простого первинного ключа. Операція потребує ручного SQL.")
        return None
    raw = input(f"Введіть значення PK ({pk}): ")
    return raw

def ask_new_row(table: str) -> Dict[str, Any]:
    from model import parse_value
    cols = SCHEMA[table]['columns']
    data = {}
    print("Введення нового рядка:")
    for c, t in cols.items():
        raw = input(f"{c} ({t}): ")
        value = parse_value(t, raw)
        data[c] = value
    return data

def ask_updates(table: str) -> Dict[str, Any]:
    from model import parse_value
    cols = SCHEMA[table]['columns']
    print("Залиште поле порожнім, щоб не змінювати.")
    updates = {}
    for c, t in cols.items():
        if c == SCHEMA[table]['pk']:
            continue
        raw = input(f"{c} ({t}): ")
        if raw.strip() == '':
            continue
        updates[c] = parse_value(t, raw)
    return updates
