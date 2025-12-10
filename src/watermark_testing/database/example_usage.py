from database.database import init_db, SessionLocal
from database.repositories import UserRepository, AudioFileRepository
from werkzeug.security import generate_password_hash


def main():
    # Datenbank initialisieren
    init_db()
    
    # Session erstellen
    db = SessionLocal()
    
    try:
        # Repositories erstellen
        user_repo = UserRepository(db)
        audio_repo = AudioFileRepository(db)
        
        # User erstellen
        print("\n--- User erstellen ---")
        user = user_repo.create(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("secure_password123")
        )
        print(f"✓ User erstellt: {user.username} (ID: {user.id})")
        
        # AudioFile erstellen
        print("\n--- AudioFile hinzufügen ---")
        audio = audio_repo.create(
            user_id=user.id,
            filename="test_audio.wav",
            file_path="/uploads/test_audio.wav",
            file_size=1024000,
            sample_rate=44100,
            duration=30.5,
            has_watermark=True,
            watermark_type="AudioSeal"
        )
        print(f"✓ AudioFile hinzugefügt: {audio.filename} (ID: {audio.id})")
        
        # User suchen
        print("\n--- User suchen ---")
        found_user = user_repo.get_by_username("testuser")
        print(f"✓ User gefunden: {found_user.email}")
        
        # Alle AudioFiles eines Users abrufen
        print("\n--- AudioFiles abrufen ---")
        user_audios = audio_repo.get_by_user(user.id)
        for a in user_audios:
            print(f"  - {a.filename} ({a.watermark_type})")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()