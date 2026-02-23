from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, api_keys, comics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    await create_tables()
    yield
    # Shutdown: nothing needed


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
**Mangable** – A metadata-focused comic book library API.

Features:
- 📚 Full ComicInfo standard metadata support
- 🔐 JWT bearer token + API key authentication
- 🔍 Advanced search with filters
- 📄 ComicInfo.xml download per comic
- 🖼 Cover image URL management
- ❌ No comic content stored (metadata only)
    """,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/v1")
app.include_router(api_keys.router, prefix="/v1")
app.include_router(comics.router, prefix="/v1")


@app.get("/", tags=["Health"])
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "ok"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
