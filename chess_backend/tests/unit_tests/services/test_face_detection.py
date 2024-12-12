import os
from unittest.mock import MagicMock, create_autospec, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from libs.services.face_detection import models, process_video
from libs.services.main import app

client = TestClient(app)


@pytest.fixture
def video_file_path():
    return "tests/unit_tests/sample_video/Untitled.mov"


@pytest.fixture
def mock_session():
    return Session()


@pytest.mark.usefixtures("mock_session")
def test_process_video(video_file_path, mock_session):
    output_file_path = "tests/unit_tests/sample_video/processed_Untitled.mp4"

    with patch.object(mock_session, "add") as mock_add, patch.object(
        mock_session, "commit"
    ) as mock_commit, patch.object(mock_session, "refresh") as mock_refresh:
        video_id, roi_data = process_video(
            video_file_path, output_file_path, mock_session
        )

    # Assertions
    assert os.path.exists(output_file_path)
    assert os.path.getsize(output_file_path) > 0

    mock_add.assert_called()
    mock_commit.assert_called()
    mock_refresh.assert_called()

    assert video_id is not None
    assert isinstance(roi_data, list)


@pytest.mark.usefixtures("mock_session")
def test_process_video_invalid_file(mock_session):
    invalid_file_path = "tests/unit_tests/sample_video/invalid_file.mov"
    output_file_path = "tests/unit_tests/sample_video/processed_invalid.mp4"

    with pytest.raises(Exception):
        process_video(invalid_file_path, output_file_path, mock_session)

    assert not os.path.exists(output_file_path)
