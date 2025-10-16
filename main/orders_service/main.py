# orders_service/main.py
import sys
import uvicorn
from fastapi import FastAPI, Request
from routes.orders import router as orders_router
from config.database import connect_to_mongo, close_mongo
import time

app = FastAPI(title="orders_service")

# Protección rápida: evitar ejecutar con Python 3.13 que puede romper Pydantic/FastAPI
if sys.version_info.major == 3 and sys.version_info.minor >= 13:
    raise RuntimeError(
        "Python 3.13 detected: esta aplicación es incompatible con Python 3.13. "
        "Usa Python 3.11 o ejecuta con Docker (imagen usa python:3.11-slim)."
    )

@app.on_event("startup")
async def startup():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown():
    await close_mongo()

@app.middleware("http")
async def log_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    print(f"[orders_service] {request.method} {request.url.path} completed in {ms:.2f}ms")
    response.headers["X-Process-Time-ms"] = str(ms)
    return response

app.include_router(orders_router, prefix="/orders", tags=["orders"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 8000)), reload=True)
