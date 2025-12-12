import sys
from pathlib import Path

# Füge das watermark_testing Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

# WICHTIG: Jetzt absolute Imports vom watermark_testing aus
from database.database import init_db, SessionLocal
from database.repositories import UserRepository
from werkzeug.security import generate_password_hash

def create_dummy_user():
    """Erstellt Test-User für Entwicklung"""
    init_db()
    db = SessionLocal()
    
    try:
        user_repo = UserRepository(db)
        
        # Prüfen ob User bereits existiert
        existing = user_repo.get_by_username("testuser")
        if existing:
            print("✓ Test-User existiert bereits")
            return
        
        # User erstellen
        user = user_repo.create(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("test123")
        )
        
        print(f"✓ Test-User erstellt: {user.username} (ID: {user.id})")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_user()