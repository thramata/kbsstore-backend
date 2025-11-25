from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI(title="KBS Store API")


# CORS
origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
CORSMiddleware,
allow_origins=[origins] if origins != "*" else [
"*"
],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


app.include_router(auth_router)