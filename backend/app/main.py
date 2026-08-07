from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import auth, imports, domains, servers, dashboard, logs
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="DNS RPZ Manager API",
    description="API for managing DNS Response Policy Zones",
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

app.include_router(auth.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")
app.include_router(domains.router, prefix="/api/v1")
app.include_router(servers.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dns-rpz-manager"}


@app.get("/")
async def root():
    return {
        "message": "DNS RPZ Manager API",
        "version": "1.0.0",
        "docs": "/docs",
    }
