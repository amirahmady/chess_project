from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from libs.services.main import app

client = TestClient(app)


@pytest.fixture
def mock_db():
    with patch("libs.services.main.get_db") as mock_get_db:
        mock_session = MagicMock(spec=Session)
        mock_get_db.return_value = mock_session
        yield mock_session


def test_upload_video(mock_db):
    video_path = "tests/unit_tests/sample_video/Untitled.mov"
    with open(video_path, "rb") as video_file:
        response = client.post("/upload_video/", files={"file": video_file})

    assert response.status_code == 200
    assert "video_id" in response.json()


# TODO: Add test_video_feed and test_roi_data functions , mock database and files
