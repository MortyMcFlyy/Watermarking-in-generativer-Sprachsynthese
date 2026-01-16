from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from contextlib import contextmanager
from .models import Base

# ==========================================
# DATENBANK-KONFIGURATION
# ==========================================

# Absoluter Pfad zur DB-Datei (im database-Ordner)
DB_DIR = Path(__file__).parent
DATABASE_URL = f"sqlite:///{DB_DIR}/watermark_testing.db"

# Für PostgreSQL: "postgresql://user:password@localhost/dbname"

# ==========================================
# ENGINE - Verbindung zur Datenbank
# ==========================================


# echo=True -> Zeigt alle SQL-Befehle im Terminal (für Debugging)
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialisiert die Datenbank (erstellt alle Tabellen)"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Datenbank initialisiert: {DATABASE_URL}")


@contextmanager
def get_db():
    """
    Context Manager für DB-Sessions.
    Stellt sicher, dass Sessions korrekt geschlossen werden.
    
    Usage:
        with get_db() as db:
            user_repo = UserRepository(db)
            user = user_repo.get_by_id(1)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()