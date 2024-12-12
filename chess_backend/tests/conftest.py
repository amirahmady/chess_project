from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def mock_engine():
    with patch("sqlalchemy.create_engine") as mock_create_engine:
        mock_engine_instance = mock_create_engine.return_value
        yield mock_engine_instance


@pytest.fixture(scope="session")
def mock_session(mock_engine):
    engine = create_engine(
        "sqlite:///:memory:",
        creator=lambda: mock_engine,
        connect_args={"check_same_thread": False},
    )
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    yield session
    session.close()
