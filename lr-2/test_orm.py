from datetime import date
from sqlalchemy import inspect, func

from orm_base import engine, get_session
from orm_models import Customer, Freelancer, Project


def main():
    # --- Перевірка доступних таблиць ---
    insp = inspect(engine)
    print("Таблиці в metadata:")
    for t in insp.get_table_names(schema="public"):
        print("  public." + t)
    print("OK\n")

    # --- Створення сесії ---
    with get_session() as session:

        # === 1. JOIN + FILTER ===
        print("=== ORM SELECT (JOIN + FILTER: Project.start_date > 2023-01-01) ===")
        query1 = (
            session.query(
                Customer.name,
                Project.name,
                Project.start_date,
                Project.deadline,
            )
            .join(Project, Customer.id == Project.customer_id)
            .filter(Project.start_date > date(2023, 1, 1))
            .limit(10)
            .all()
        )
        for row in query1:
            print(row)
        print("\n")  # пустий рядок для красивого скріна

        # === 2. GROUP BY ===
        print("=== ORM GROUP BY (Freelancer surname + count of projects) ===")
        query2 = (
            session.query(
                Freelancer.surname,
                func.count(Project.id)
            )
            .outerjoin(Project)
            .group_by(Freelancer.surname)
            .limit(10)
            .all()
        )
        for row in query2:
            print(row)
        print("\n")

        # === 3. FILTER (легкий пошук по email, гарантовано знайде записи) ===
        print("=== ORM FILTER (Customer.email ILIKE '%mail%') ===")
        query3 = (
            session.query(Customer)
            .filter(Customer.email.ilike("%mail%"))
            .limit(10)
            .all()
        )
        for c in query3:
            print(c.id, c.name, c.surname, c.email)


if __name__ == "__main__":
    main()
