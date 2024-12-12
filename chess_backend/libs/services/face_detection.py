import logging
import uuid

import imageio
import numpy as np
from PIL import Image
from sqlalchemy.orm import Session

from libs.models import models
from libs.services.face_detection_helpers import detect_faces_and_draw

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_video(file_path: str, output_file_path: str, db: Session):
    reader = imageio.get_reader(file_path, "ffmpeg")
    writer = imageio.get_writer(output_file_path, fps=30)
    roi_data_list = []

    for frame in reader:
        frame_rgb = Image.fromarray(frame)
        frame_rgb, roi_data = detect_faces_and_draw(frame_rgb)
        roi_data_list.extend(roi_data)
        writer.append_data(np.array(frame_rgb))

    reader.close()
    writer.close()

    # Store the video and ROI data in the database
    video_id = store_video(file_path, output_file_path, roi_data_list, db)

    return video_id, roi_data_list


def store_video(
    file_location: str,
    processed_file_location: str,
    roi_data,
    db: Session,
    video_id: uuid.UUID = None,
):
    if video_id is None:
        video_id = uuid.uuid4()

    video = models.Video(
        id=video_id,
        file_path=file_location,
        processed_file_path=processed_file_location,
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return video.id


def store_roi_data(roi_data, video_id: uuid.UUID, db: Session):
    for roi in roi_data:
        roi_entry = models.ROI(
            left=roi["left"],
            top=roi["top"],
            right=roi["right"],
            bottom=roi["bottom"],
            video_id=video_id,
        )
        db.add(roi_entry)
    db.commit()
