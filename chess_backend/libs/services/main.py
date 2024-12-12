import io
import logging
import os
import uuid
from datetime import datetime

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
from sqlalchemy.orm import Session

from libs.database import get_db
from libs.models import Video
from libs.services import face_detection
from libs.services.face_detection_helpers import (
    process_frame,
    stream_video_feed_from_movie,
)

# Configure logging
# TODO: set logging level via environment variable
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow CORS for the frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///:memory:"
)  # Use in-memory SQLite for testing


@app.websocket("/ws/process_stream_feed/")
async def process_stream_feed(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    video_id = uuid.uuid4()
    file_location = f"./videos/feeds/{video_id}.mp4"
    processed_file_location = f"./videos/processed_{video_id}.mp4"
    roi_data = []

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    # Open a file to write the incoming frames
    with open(file_location, "wb") as video_file:
        try:
            while True:
                frame = await websocket.receive_bytes()
                video_file.write(frame)

                try:
                    processed_frame, rois = process_frame(frame)
                    roi_data.extend(rois)
                    if isinstance(processed_frame, Image.Image):
                        buffer = io.BytesIO()
                        processed_frame.save(buffer, format="JPEG")
                        processed_frame_bytes = buffer.getvalue()
                        logger.info(
                            f"Sending processed frame of size: {len(processed_frame_bytes)} bytes"
                        )
                        await websocket.send_bytes(processed_frame_bytes)
                    else:
                        logger.error("Processed frame is not bytes-like")
                        logger.debug(f"Processed frame: {processed_frame}")
                        await websocket.send_json({"message": "Error processing frame"})
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
                    await websocket.send_json({"message": "Error processing frame"})

        except WebSocketDisconnect:
            pass

    video_id = face_detection.store_video(
        file_location, processed_file_location, roi_data, db, video_id
    )
    face_detection.store_roi_data(roi_data, video_id, db)
    logger.info(f"Webcam feed processed successfully: {video_id}")
    await websocket.send_json(
        {"message": "Webcam feed processed successfully", "video_id": str(video_id)}
    )
    await websocket.close()


@app.get("/video_feed/")
async def video_feed(video_id: uuid.UUID, db: Session = Depends(get_db)):
    logger.info(f"Video feed requested for video: {video_id}")
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    logger.info(f"Video feed retrieved for video: {video.processed_file_path}")
    return StreamingResponse(
        stream_video_feed_from_movie(video.processed_file_path),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/roi_data/")
async def roi_data(video_id: uuid.UUID, db: Session = Depends(get_db)):
    logger.info(f"ROI data requested for video: {video_id}")
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    logger.info(f"ROI data retrieved for video: {video_id}")
    return {"roi_data": video.roi_data}


@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_location = f"./videos/uploads/uploaded_file_{timestamp}_{file.filename}"
    processed_file_location = f"./videos/processed_video_{timestamp}.mp4"

    with open(file_location, "wb") as f:
        f.write(file.file.read())

    video_id, roi_data = face_detection.process_video(
        file_location, processed_file_location, db
    )
    face_detection.store_roi_data(roi_data, video_id, db)
    logger.info(
        f"Video processed successfully: {video_id}, processed_file_location: {processed_file_location}"
    )
    return {"message": "Video processed successfully", "video_id": video_id}
