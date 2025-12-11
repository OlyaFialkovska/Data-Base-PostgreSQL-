from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import PG_DSN

# SQLAlchemy НЕ вміє працювати з DSN у форматі "host=... dbname=... user=..."
# Тому ми вручну конвертуємо DSN у параметри

def parse_dsn(dsn: str):
    """
    Конвертує рядок host=... port=... dbname=... user=... password=...
    у словник параметрів.
    """
    params = {}
    for part in dsn.split():
        key, value = part.split("=")
        params[key] = value
    return params


dsn_params = parse_dsn(PG_DSN)

# Формуємо правильний URL для SQLAlchemy:
url = (
    f"postgresql+psycopg://{dsn_params['user']}:{dsn_params['password']}"
    f"@{dsn_params['host']}:{dsn_params['port']}/{dsn_params['dbname']}"
)

# Створюємо engine
engine = create_engine(url, echo=False)

# База ORM
Base = declarative_base()

# Фабрика сесій
SessionLocal = sessionmaker(bind=engine)


def get_session():
    return SessionLocal()
