import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, create_engine

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    if not __factory:
        raise RuntimeError("Session factory not initialized")
    return __factory()


def apply_migrations():
    engine = create_engine('sqlite:///db/school_library.db')
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('books')]

        # Добавляем copies_available, если его нет
        if 'copies_available' not in columns:
            conn.execute(text("ALTER TABLE books ADD COLUMN copies_available INTEGER DEFAULT 1"))
            print("Добавлен столбец copies_available")

        # Добавляем total_copies, если его нет
        if 'total_copies' not in columns:
            conn.execute(text("ALTER TABLE books ADD COLUMN total_copies INTEGER DEFAULT 1"))
            print("Добавлен столбец total_copies")

            # Теперь можно безопасно копировать значения
            conn.execute(text("UPDATE books SET total_copies = 1, copies_available = 1"))
            conn.commit()


def migrate_books():
    engine = create_engine('sqlite:///db/school_library.db')
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS books_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                genre TEXT,
                status BOOLEAN DEFAULT 1,
                img TEXT,
                date DATE,
                reader TEXT,
                copies_available INTEGER DEFAULT 1,
                total_copies INTEGER DEFAULT 1,
                user_id INTEGER
            )
        """))
        conn.execute(text("""
            INSERT INTO books_new 
            SELECT id, title, author, genre, status, img, date, 
                   reader, 1, 1, user_id 
            FROM books
        """))
        conn.execute(text("DROP TABLE books"))
        conn.execute(text("ALTER TABLE books_new RENAME TO books"))