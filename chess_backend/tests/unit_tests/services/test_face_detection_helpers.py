import io

import imageio
import pytest
from PIL import Image

from libs.services.face_detection_helpers import detect_faces_and_draw, process_frame


@pytest.fixture
def sample_frame_with_face():
    video_path = "tests/unit_tests/sample_video/Untitled.mov"
    reader = imageio.get_reader(video_path, "ffmpeg")
    frame = reader.get_data(0)
    reader.close()

    frame_image = Image.fromarray(frame)
    buffer = io.BytesIO()
    frame_image.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def sample_frame_without_face():
    img = Image.new("RGB", (100, 100), color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_detect_faces_and_draw_with_face(sample_frame_with_face):
    frame_image = Image.open(io.BytesIO(sample_frame_with_face))
    frame_rgb, roi_data = detect_faces_and_draw(frame_image)

    assert isinstance(frame_rgb, Image.Image)
    assert isinstance(roi_data, list)
    assert len(roi_data) > 0
    assert "left" in roi_data[0]
    assert "top" in roi_data[0]
    assert "right" in roi_data[0]
    assert "bottom" in roi_data[0]


def test_detect_faces_and_draw_without_face(sample_frame_without_face):
    frame_image = Image.open(io.BytesIO(sample_frame_without_face))
    frame_rgb, roi_data = detect_faces_and_draw(frame_image)

    assert isinstance(frame_rgb, Image.Image)
    assert isinstance(roi_data, list)
    assert len(roi_data) == 0


def test_process_frame_with_face(sample_frame_with_face):
    frame_rgb, roi_data = process_frame(sample_frame_with_face)

    assert isinstance(frame_rgb, Image.Image)
    assert isinstance(roi_data, list)
    assert len(roi_data) > 0
    assert "left" in roi_data[0]
    assert "top" in roi_data[0]
    assert "right" in roi_data[0]
    assert "bottom" in roi_data[0]


def test_process_frame_without_face(sample_frame_without_face):
    frame_rgb, roi_data = process_frame(sample_frame_without_face)

    assert isinstance(frame_rgb, Image.Image)
    assert isinstance(roi_data, list)
    assert len(roi_data) == 0
