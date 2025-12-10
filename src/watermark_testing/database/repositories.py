from typing import List, Optional
from sqlalchemy.orm import Session
from .models import User, AudioFile
from datetime import datetime


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    

# ==========================================
# CREATE - Neuen User anlegen
# ==========================================
    def create(self, username: str, email: str, password_hash: str) -> User:
        """Erstellt einen neuen User"""
        user = User(username=username, email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    

# ==========================================
# GET - User abrufen
# ==========================================


    def get_by_id(self, user_id: int) -> Optional[User]:
        """Findet User nach ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Findet User nach Username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Findet User nach Email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self) -> List[User]:
        """Gibt alle User zurück"""
        return self.db.query(User).all()
    

# ==========================================
# UPDATE - User aktualisieren
# =========================================    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Aktualisiert User-Daten"""
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
# ==========================================
# DELETE - User löschen
# ==========================================
    def delete(self, user_id: int) -> bool:
        """Löscht einen User"""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False


class AudioFileRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, filename: str, file_path: str, 
               file_size: int, sample_rate: int, duration: float,
               has_watermark: bool = False, watermark_type: str = None) -> AudioFile:
        """Erstellt einen neuen AudioFile-Eintrag"""
        audio = AudioFile(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            sample_rate=sample_rate,
            duration=duration,
            has_watermark=has_watermark,
            watermark_type=watermark_type
        )
        self.db.add(audio)
        self.db.commit()
        self.db.refresh(audio)
        return audio
    
    def get_by_id(self, audio_id: int) -> Optional[AudioFile]:
        """Findet AudioFile nach ID"""
        return self.db.query(AudioFile).filter(AudioFile.id == audio_id).first()
    
    def get_by_user(self, user_id: int) -> List[AudioFile]:
        """Gibt alle AudioFiles eines Users zurück"""
        return self.db.query(AudioFile).filter(AudioFile.user_id == user_id).all()
    
    def get_all(self) -> List[AudioFile]:
        """Gibt alle AudioFiles zurück"""
        return self.db.query(AudioFile).all()
    
    def update(self, audio_id: int, **kwargs) -> Optional[AudioFile]:
        """Aktualisiert AudioFile-Daten"""
        audio = self.get_by_id(audio_id)
        if audio:
            for key, value in kwargs.items():
                setattr(audio, key, value)
            self.db.commit()
            self.db.refresh(audio)
        return audio
    
    def delete(self, audio_id: int) -> bool:
        """Löscht eine AudioFile"""
        audio = self.get_by_id(audio_id)
        if audio:
            self.db.delete(audio)
            self.db.commit()
            return True
        return False