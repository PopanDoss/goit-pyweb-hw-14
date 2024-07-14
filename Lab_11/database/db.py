from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db(is_test: bool = False):
    
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
