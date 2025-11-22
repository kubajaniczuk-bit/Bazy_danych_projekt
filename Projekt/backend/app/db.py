from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite w pliku kino.db w folderze backend
SQLALCHEMY_DATABASE_URL = "sqlite:///./kino.db"

# connect_args jest wymagane dla SQLite przy pracy wielowątkowej (FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)
# Dependency dla FastAPI - sesja bazy danych na żądanie
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
