from typing import Any, Dict, List, Tuple
import datetime
import time

from psycopg.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation, RestrictViolation

from orm_base import get_session
from orm_models import (
    Platform,
    Freelancer,
    Customer,
    Project,
    FreelancerPlatform,
    CustomerPlatform,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


#  СХЕМА 
SCHEMA: Dict[str, Dict[str, Any]] = {
    'Platform_': {
        'pk': 'id',
        'columns': {
            'id': 'int',
            'name': 'str',
            'creation date': 'date',
        }
    },
    'Freelancer_': {
        'pk': 'id',
        'columns': {
            'id': 'int',
            'Name': 'str(30)',
            'Surname': 'str(30)',
            'Email': 'str(30)',
            'Password': 'str(30)',
        }
    },
    'Customer_': {
        'pk': 'id',
        'columns': {
            'id': 'int',
            'Name': 'str(30)',
            'Surname': 'str(30)',
            'Email': 'str(30)',
            'Password': 'str(30)',
        }
    },
    'Project_': {
        'pk': 'id',
        'columns': {
            'id': 'int',
            'Name': 'str(20)',
            'Deadline': 'date',
            'Start date': 'date',
            'End date': 'date',
            'Customer_id': 'int?',
            'Freelancer_id': 'int?',
        }
    },
    'Freelancer_Platform_': {
        'pk': None,
        'columns': {
            'Freelancer_id': 'int',
            'Platform_id': 'int',
        }
    },
    'Customer_Platform_': {
        'pk': None,
        'columns': {
            'Customer_id': 'int',
            'Platform_id': 'int',
        }
    },
}

# Відповідність назви таблиці -> ORM-клас
TABLE_MODEL_MAP = {
    'Platform_': Platform,
    'Freelancer_': Freelancer,
    'Customer_': Customer,
    'Project_': Project,
    'Freelancer_Platform_': FreelancerPlatform,
    'Customer_Platform_': CustomerPlatform,
}

# Відповідність "імені колонки з SCHEMA" -> "атрибут у ORM-класі"
COLUMN_ATTR_MAP: Dict[str, Dict[str, str]] = {
    'Platform_': {
        'id': 'id',
        'name': 'name',
        'creation date': 'creation_date',
    },
    'Freelancer_': {
        'id': 'id',
        'Name': 'name',
        'Surname': 'surname',
        'Email': 'email',
        'Password': 'password',
    },
    'Customer_': {
        'id': 'id',
        'Name': 'name',
        'Surname': 'surname',
        'Email': 'email',
        'Password': 'password',
    },
    'Project_': {
        'id': 'id',
        'Name': 'name',
        'Deadline': 'deadline',
        'Start date': 'start_date',
        'End date': 'end_date',
        'Customer_id': 'customer_id',
        'Freelancer_id': 'freelancer_id',
    },
    'Freelancer_Platform_': {
        'Freelancer_id': 'freelancer_id',
        'Platform_id': 'platform_id',
    },
    'Customer_Platform_': {
        'Customer_id': 'customer_id',
        'Platform_id': 'platform_id',
    },
}


def get_columns(table: str) -> List[str]:
    return list(SCHEMA[table]['columns'].keys())

#  ВАЛІДАЦІЯ ВВОДУ
def parse_value(type_decl: str, raw: str) -> Any:
    td = type_decl.strip().lower()
    if td.startswith('str'):
        limit = None
        if '(' in td and ')' in td:
            try:
                limit = int(td[td.find('(') + 1:td.find(')')])
            except:
                pass
        value = raw.strip()
        if limit and len(value) > limit:
            raise ValueError(f"Рядок занадто довгий (>{limit} символів)")
        return value
    if td.startswith('int'):
        if raw == '' and td.endswith('?'):
            return None
        try:
            return int(raw)
        except:
            raise ValueError("Очікувалось ціле число")
    if td.startswith('date'):
        if raw == '' and td.endswith('?'):
            return None
        try:
            return datetime.date.fromisoformat(raw)
        except:
            raise ValueError("Очікувалась дата у форматі YYYY-MM-DD")
    if td.endswith('?') and (raw is None or raw.strip() == ''):
        return None
    return raw

# ---CRUD-ФУНКЦІЇ ЧЕРЕЗ ORM

def list_all(table: str) -> List[Tuple]:
    """Повертає список рядків таблиці як кортежі (як і раніше)."""
    Model = TABLE_MODEL_MAP[table]
    col_names = get_columns(table)
    attr_map = COLUMN_ATTR_MAP[table]
    attrs = [attr_map[c] for c in col_names]

    with get_session() as session:
        query = session.query(Model)
        pk_name = SCHEMA[table]['pk']
        if pk_name is not None:
            pk_attr = getattr(Model, attr_map[pk_name])
            query = query.order_by(pk_attr)
        rows = query.all()
        result = [tuple(getattr(row, a) for a in attrs) for row in rows]
        return result


def insert_row(table: str, data: Dict[str, Any]) -> None:
    """Вставка нового рядка через ORM."""
    Model = TABLE_MODEL_MAP[table]
    attr_map = COLUMN_ATTR_MAP[table]
    obj_kwargs = {attr_map[k]: v for k, v in data.items()}

    with get_session() as session:
        obj = Model(**obj_kwargs)
        session.add(obj)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            # Пробуємо «пробросити» оригінальну помилку psycopg,
            # щоб контролер міг її впізнати як ForeignKeyViolation тощо.
            if hasattr(e, "orig") and isinstance(
                e.orig, (UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation)
            ):
                raise e.orig
            raise


def update_row(table: str, pk_name: str, pk_value: Any, updates: Dict[str, Any]) -> int:
    """Оновлення рядка за PK через ORM. Повертає кількість оновлених рядків."""
    if not updates:
        return 0
    Model = TABLE_MODEL_MAP[table]
    attr_map = COLUMN_ATTR_MAP[table]

    with get_session() as session:
        pk_attr = getattr(Model, attr_map[pk_name])
        obj = session.query(Model).filter(pk_attr == pk_value).one_or_none()
        if obj is None:
            return 0

        for col, val in updates.items():
            setattr(obj, attr_map[col], val)

        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if hasattr(e, "orig") and isinstance(
                e.orig, (ForeignKeyViolation, CheckViolation, NotNullViolation)
            ):
                raise e.orig
            raise
        return 1


def delete_row(table: str, pk_name: str, pk_value: Any) -> int:
    Model = TABLE_MODEL_MAP[table]
    attr_map = COLUMN_ATTR_MAP[table]

    with get_session() as session:
        pk_attr = getattr(Model, attr_map[pk_name])
        obj = session.query(Model).filter(pk_attr == pk_value).one_or_none()
        if obj is None:
            return 0
        session.delete(obj)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if hasattr(e, "orig") and isinstance(e.orig, (ForeignKeyViolation, RestrictViolation)):
                raise e.orig
            raise
        return 1

#---ПОШУКИ / АНАЛІТИКА ЧЕРЕЗ ORM

def search_projects_by_date_range(start_date, end_date):
    from sqlalchemy import and_

    with get_session() as session:
        t0 = time.time()
        q = (
            session.query(
                Customer.name.label("customer_name"),
                Project.name.label("project_name"),
                Project.start_date,
                Project.deadline,
            )
            .join(Project, Customer.id == Project.customer_id)
            .filter(and_(Project.start_date >= start_date, Project.start_date <= end_date))
            .order_by(Project.start_date)
        )
        rows = q.all()
        ms = (time.time() - t0) * 1000
        return rows, ms


def search_freelancers_by_surname_like(pattern):
    with get_session() as session:
        t0 = time.time()
        q = (
            session.query(
                Freelancer.surname,
                func.count(Project.id).label("total_projects"),
            )
            .outerjoin(Project, Project.freelancer_id == Freelancer.id)
            .filter(Freelancer.surname.ilike(pattern))
            .group_by(Freelancer.surname)
            .order_by(func.count(Project.id).desc())
        )
        rows = q.all()
        ms = (time.time() - t0) * 1000
        return rows, ms


def count_projects_by_platform(name_like):
    with get_session() as session:
        t0 = time.time()
        q = (
            session.query(
                Platform.name.label("platform_name"),
                func.count(Project.id).label("project_count"),
            )
            .outerjoin(CustomerPlatform, CustomerPlatform.platform_id == Platform.id)
            .outerjoin(Customer, Customer.id == CustomerPlatform.customer_id)
            .outerjoin(Project, Project.customer_id == Customer.id)
            .filter(Platform.name.ilike(name_like))
            .group_by(Platform.name)
            .order_by(func.count(Project.id).desc())
        )
        rows = q.all()
        ms = (time.time() - t0) * 1000
        return rows, ms
