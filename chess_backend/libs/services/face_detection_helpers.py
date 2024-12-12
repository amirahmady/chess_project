import io
import logging

import dlib
import imageio
import numpy as np
from PIL import Image, ImageDraw

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize dlib's face detector
detector = dlib.get_frontal_face_detector()


def detect_faces_and_draw(frame_rgb):
    frame_np = np.array(frame_rgb)
    gray = np.dot(frame_np[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    faces = detector(gray)
    roi_data_list = []

    if faces:
        logger.info("Face detected")
        for face in faces:
            left, top, right, bottom = (
                face.left(),
                face.top(),
                face.right(),
                face.bottom(),
            )

            # Draw rectangle
            draw = ImageDraw.Draw(frame_rgb)
            draw.rectangle([left, top, right, bottom], outline="red", width=2)
            logger.info(
                f"Rectangle drawn: left={left}, top={top}, right={right}, bottom={bottom}"
            )

            # Store ROI data
            roi_data = {"left": left, "top": top, "right": right, "bottom": bottom}
            roi_data_list.append(roi_data)
    return frame_rgb, roi_data_list


def process_frame(frame: bytes):
    try:
        logger.debug(f"Received frame of size: {len(frame)} bytes")
        logger.debug(f"First 100 bytes of frame: {frame[:100]}")

        # Decode the frame using imageio
        frame_image = imageio.imread(io.BytesIO(frame))

        if frame_image is None:
            raise ValueError("Could not decode frame")

        # Convert the frame to RGB format
        frame_pil = Image.fromarray(frame_image)

        # Process the frame
        frame_rgb, roi_data = detect_faces_and_draw(frame_pil)
        return frame_rgb, roi_data
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return []


def stream_video_feed_from_movie(file_path: str):
    def generate():
        reader = imageio.get_reader(file_path, "ffmpeg")
        for frame in reader:
            frame_rgb = Image.fromarray(frame)
            buffer = io.BytesIO()
            frame_rgb.save(buffer, format="JPEG")
            frame_bytes = buffer.getvalue()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
        reader.close()

    return generate()
