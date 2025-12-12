from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
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


def get_db():
    """Dependency für DB-Sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()