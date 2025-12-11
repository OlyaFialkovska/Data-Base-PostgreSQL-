from typing import Any, Dict, List, Tuple, Optional
import datetime
import psycopg
from psycopg import sql
from psycopg.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from psycopg.errors import RestrictViolation
from config import PG_DSN
import time

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


def get_conn():
    return psycopg.connect(PG_DSN)


def ident(name: str) -> sql.Identifier:
    return sql.Identifier(name)


def qname(table: str, column: str) -> sql.SQL:
    return sql.SQL('.').join([ident('public'), sql.Identifier(table), ])


def list_all(table: str) -> List[Tuple]:
    with get_conn() as conn, conn.cursor() as cur:
        query = sql.SQL('SELECT * FROM {}.{} ORDER BY 1').format(
            ident('public'), ident(table)
        )
        cur.execute(query)
        return cur.fetchall()


def get_columns(table: str) -> List[str]:
    return list(SCHEMA[table]['columns'].keys())


def insert_row(table: str, data: Dict[str, Any]) -> None:
    cols = list(data.keys())
    values = [data[c] for c in cols]
    with get_conn() as conn, conn.cursor() as cur:
        query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
            ident('public'),
            ident(table),
            sql.SQL(', ').join(sql.Identifier(c) for c in cols),
            sql.SQL(', ').join(sql.Placeholder() for _ in cols),
        )
        try:
            cur.execute(query, values)
        except (UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation) as e:
            conn.rollback()
            raise
        conn.commit()


def update_row(table: str, pk_name: str, pk_value: Any, updates: Dict[str, Any]) -> int:
    if not updates:
        return 0
    assignments = [sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder()) for k in updates.keys()]
    values = list(updates.values()) + [pk_value]
    with get_conn() as conn, conn.cursor() as cur:
        query = sql.SQL("UPDATE {}.{} SET {} WHERE {} = {}").format(
            ident('public'),
            ident(table),
            sql.SQL(', ').join(assignments),
            sql.Identifier(pk_name),
            sql.Placeholder(),
        )
        try:
            cur.execute(query, values)
        except (ForeignKeyViolation, CheckViolation, NotNullViolation) as e:
            conn.rollback()
            raise
        conn.commit()
        return cur.rowcount


def delete_row(table: str, pk_name: str, pk_value: Any) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        query = sql.SQL("DELETE FROM {}.{} WHERE {} = {}").format(
            ident('public'),
            ident(table),
            sql.Identifier(pk_name),
            sql.Placeholder(),
        )
        try:
            cur.execute(query, (pk_value,))
        except (ForeignKeyViolation, RestrictViolation) as e:
            conn.rollback()
            raise
        conn.commit()
        return cur.rowcount


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

def search_projects_by_date_range(start_date, end_date):
    with get_conn() as conn, conn.cursor() as cur:
        t0 = time.time()
        cur.execute("""
            SELECT c."Name" AS customer_name,
                   p."Name" AS project_name,
                   p."Start date", p."Deadline"
            FROM "Project_" p
            JOIN "Customer_" c ON c.id = p."Customer_id"
            WHERE p."Start date" BETWEEN %s AND %s
            ORDER BY p."Start date";
        """, (start_date, end_date))
        rows = cur.fetchall()
        ms = (time.time() - t0) * 1000
        return rows, ms


def search_freelancers_by_surname_like(pattern):
    with get_conn() as conn, conn.cursor() as cur:
        t0 = time.time()
        cur.execute("""
            SELECT f."Surname", COUNT(p.id) AS total_projects
            FROM "Freelancer_" f
            LEFT JOIN "Project_" p ON p."Freelancer_id" = f.id
            WHERE f."Surname" ILIKE %s
            GROUP BY f."Surname"
            ORDER BY total_projects DESC;
        """, (pattern,))
        rows = cur.fetchall()
        ms = (time.time() - t0) * 1000
        return rows, ms


def count_projects_by_platform(name_like):
    with get_conn() as conn, conn.cursor() as cur:
        t0 = time.time()
        cur.execute("""
            SELECT pl."name" AS platform_name, COUNT(pr.id) AS project_count
            FROM "Platform_" pl
            LEFT JOIN "Customer_Platform_" cp ON cp."Platform_id" = pl.id
            LEFT JOIN "Customer_" c ON c.id = cp."Customer_id"
            LEFT JOIN "Project_" pr ON pr."Customer_id" = c.id
            WHERE pl."name" ILIKE %s
            GROUP BY pl."name"
            ORDER BY project_count DESC;
        """, (name_like,))
        rows = cur.fetchall()
        ms = (time.time() - t0) * 1000
        return rows, ms