from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router  # <- ajouté

app = FastAPI(
    title="KBS Store API",
    description="API E-commerce pour KBS Store",
    version="1.0.0"
)

# -------------------------
# CORS (production + local)
# -------------------------
origins = [
    "http://localhost:5173",
    "https://kbsstore.vercel.app",  # frontend production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Routes
# -------------------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# -------------------------
# Static uploads (images)
# -------------------------
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def home():
    return {"message": "KBS Store API is running 🚀"}


# Render nécessite un port spécifique, mais uvicorn le gère automatiquement
# Commande de démarrage : uvicorn main:app --host 0.0.0.0 --port 10000
