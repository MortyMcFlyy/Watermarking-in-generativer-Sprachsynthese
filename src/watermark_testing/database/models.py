from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey, Float, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship zu Audio-Dateien
    audio_files = relationship("AudioFile", back_populates="user", cascade="all, delete-orphan")


class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in Bytes
    sample_rate = Column(Integer)
    duration = Column(Float)  # in Sekunden
    has_watermark = Column(Boolean, default=False)
    watermark_type = Column(String(50))  # z.B. "AudioSeal", "PerTh"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship zu User
    user = relationship("User", back_populates="audio_files")