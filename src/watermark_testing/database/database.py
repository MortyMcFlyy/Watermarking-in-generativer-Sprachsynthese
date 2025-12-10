from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# ==========================================
# DATENBANK-KONFIGURATION
# ==========================================

# SQLite für lokale Entwicklung (ändere zu PostgreSQL für Produktion)
DATABASE_URL = "sqlite:///./watermark_testing.db"
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
    print(" Datenbank initialisiert")


def get_db():
    """Dependency für DB-Sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()