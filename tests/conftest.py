
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


from Lab_11.main import app
from Lab_11.repository.auth import Hash, create_access_token
from Lab_11.database.models import Base, User
from Lab_11.database.db import get_db

from Lab_11.settings import SQLALCHEMY_TEST_DATABASE_URL


engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

username = "test_user@example.com"
password = "testpassword"

@pytest.fixture(scope="module", autouse=True)
def init_models_wraper():
    hash = Hash()

    def init_models():
        
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine) 

        with TestingSessionLocal() as session:
            hash_password = hash.get_password_hash(password)
            current_user = User(
                email=username,
                password=hash_password,
                confirmed=True,
            )
            session.add(current_user)
            session.commit()  

    init_models()


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            session.rollback()
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)



@pytest.fixture()
def get_token():
    token = create_access_token(data={"sub": username})
    return token