from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import SQLALCHEMY_DATABASE_URL, SQLALCHEMY_TEST_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)

Test_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Dependency
def get_db(is_test: bool = False):
    if is_test:
        db= Test_SessionLocal
    else:
        db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
