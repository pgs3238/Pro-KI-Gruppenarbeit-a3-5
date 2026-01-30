# FastAPI REST API für Transaktionsverwaltung (App-Bootstrap & Router-Registrierung)

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..database import init_db, Transaktion
from ..categories.auto_categorizer_service import get_auto_categorizer_service
from .dependencies import get_db
from . import transactions_routes
from . import auto_categorization_routes
try:
    from . import chatbot_routes
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    print("⚠️ Chatbot nicht verfügbar (Gemini SDK fehlt)")

try:
    from . import category_routes
    CATEGORY_ROUTES_AVAILABLE = True
except ImportError:
    CATEGORY_ROUTES_AVAILABLE = False
    print("⚠️ Category Routes nicht verfügbar")

from . import zinsrechner_routes
from . import settings_routes
from . import konten_routes

# Globale Service-Instanz
auto_categorizer = get_auto_categorizer_service()


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modernes Lifespan Pattern für Startup/Shutdown Events."""
    # Startup
    init_db()
    print("[OK] API gestartet")

    # Auto-Kategorisierung beim Start
    state = auto_categorizer.get_categorization_state()

    # Kategorisieren wenn:
    # - Transaktionen vorhanden sind UND
    # - entweder has_new_transactions > 0 ODER has_new_transactions ist None (noch nie kategorisiert)
    with next(get_db()) as db:
        transaction_count = db.query(Transaktion).count()

    if transaction_count > 0 and (
        state["has_new_transactions"] is None or state["has_new_transactions"] > 0
    ):
        auto_categorizer.run_full_categorization_cycle()

    yield  # App läuft

    # Shutdown (bei Bedarf Cleanup hier hinzufügen)
    print("[OK] API beendet")


# ==================== SETUP ====================

app = FastAPI(
    title="Ausgabenverwaltung API",
    description="REST API für die Verwaltung von Finanztransaktionen",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== STATIC FILES & ROUTER ====================

# Finde das Root-Verzeichnis (2 Ebenen über dem src/api Ordner)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount templates (für direkten Zugriff auf HTML)
if TEMPLATES_DIR.exists():
    app.mount("/templates", StaticFiles(directory=str(TEMPLATES_DIR)), name="templates")


# ==================== ROOT & ROUTER ====================

from fastapi.responses import FileResponse

@app.get("/")
def root():
    """Startseite (Dashboard)"""
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/index.html")
def index_page():
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/transactions.html")
def transactions_page():
    return FileResponse(TEMPLATES_DIR / "transactions.html")

@app.get("/kategorien.html")
def kategorien_page():
    return FileResponse(TEMPLATES_DIR / "kategorien.html")

@app.get("/konten.html")
def konten_page():
    return FileResponse(TEMPLATES_DIR / "konten.html")

@app.get("/zinsrechner.html")
def zinsrechner_page():
    return FileResponse(TEMPLATES_DIR / "zinsrechner.html")

@app.get("/finanz-buddy.html")
def chatbot_page():
    return FileResponse(TEMPLATES_DIR / "finanz-buddy.html")


# Router registrieren - alle mit /api Prefix (Prefixes sind in den Routern selbst definiert)
app.include_router(transactions_routes.router, prefix="/api")
app.include_router(konten_routes.router, prefix="/api")
app.include_router(auto_categorization_routes.router, prefix="/api")
if CHATBOT_AVAILABLE:
    app.include_router(chatbot_routes.router, prefix="/api")
app.include_router(zinsrechner_routes.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")

# Category-Router registrieren
if CATEGORY_ROUTES_AVAILABLE:
    app.include_router(category_routes.router, prefix="/api")
