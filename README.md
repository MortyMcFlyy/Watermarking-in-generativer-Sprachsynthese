# Bachelor_Arbeit
Im Rahmen meines Studiums an der Hochschule Osnabrück. 



## Quick Start mit Docker:
### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert und gestartet
- Git (optional, zum Klonen)

### Installation & Start

```bash
# 1. Repository klonen
git clone <repository-url>
cd Bachelor_Arbeit

# 2. Container bauen und starten (dauert beim ersten Mal einige Minuten je nach Hardware auch länger(ohne GPU deutlich länger)

docker-compose up --build

# 3. App im Browser öffnen
# → http://localhost:5000
```

### Hinweis
Bei langsamer Hardware und begrenzten Docker-Ressourcen kann es zu Timeouts kommen. In diesem Fall:
- Docker-Ressourcen in Docker Desktop erhöhen (Settings → Resources)
- Oder als Fallback die VS-Code-Variante mit venv nutzen (siehe unten)

## Quick Start mit VS-Code:
### Voraussetzungen

- Python 3.8 oder höher installiert
- VS Code installiert
- Git (optional, zum Klonen)

### Installation & Start

```bash
# 1. Repository klonen
git clone <repository-url>
cd Bachelor_Arbeit

# 2. Virtuelles Environment erstellen
python -m venv .venv

# 3. Virtual Environment aktivieren
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 4. Requirements installieren
pip install -r requirements.txt

# 5. In den API-Ordner wechseln
cd src/watermark_testing/api

# 6. App starten
python app.py

# 7. App im Browser öffnen
# → http://localhost:5000
```