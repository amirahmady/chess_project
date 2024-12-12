import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    file_path = Column(String, index=True)
    processed_file_path = Column(String, unique=True, index=True, nullable=True)
    rois = relationship("ROI", back_populates="video")


class ROI(Base):
    __tablename__ = "rois"
    id = Column(Integer, primary_key=True, index=True)
    left = Column(Integer, nullable=False)
    top = Column(Integer, nullable=False)
    right = Column(Integer, nullable=False)
    bottom = Column(Integer, nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"))
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    video = relationship("Video", back_populates="rois")
