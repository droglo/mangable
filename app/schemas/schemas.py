import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── API Key Schemas ───────────────────────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    expires_at: Optional[datetime] = None


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ApiKeyCreated(ApiKeyOut):
    """Returned only once upon creation - contains the full key."""
    full_key: str


# ─── Comic Schemas ─────────────────────────────────────────────────────────────

class ComicBase(BaseModel):
    title: str = Field(..., max_length=500)
    series: Optional[str] = Field(None, max_length=500)
    alternate_series: Optional[str] = None
    number: Optional[str] = None
    count: Optional[int] = None
    volume: Optional[int] = None
    alternate_number: Optional[str] = None
    alternate_count: Optional[int] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    year: Optional[int] = Field(None, ge=1800, le=2100)
    month: Optional[int] = Field(None, ge=1, le=12)
    day: Optional[int] = Field(None, ge=1, le=31)
    publisher: Optional[str] = Field(None, max_length=255)
    imprint: Optional[str] = None
    writer: Optional[str] = None
    penciller: Optional[str] = None
    inker: Optional[str] = None
    colorist: Optional[str] = None
    letterer: Optional[str] = None
    cover_artist: Optional[str] = None
    editor: Optional[str] = None
    translator: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[str] = None
    web: Optional[str] = None
    age_rating: Optional[str] = None
    language_iso: Optional[str] = Field(None, max_length=10)
    format: Optional[str] = None
    is_bw: Optional[bool] = None
    manga: Optional[str] = None
    community_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    review: Optional[str] = None
    page_count: Optional[int] = Field(None, ge=0)
    cover_url: Optional[str] = Field(None, max_length=1000)
    isbn: Optional[str] = None
    barcode: Optional[str] = None
    series_group: Optional[str] = None


class ComicCreate(ComicBase):
    pass


class ComicUpdate(BaseModel):
    """All fields optional for PATCH."""
    title: Optional[str] = Field(None, max_length=500)
    series: Optional[str] = None
    alternate_series: Optional[str] = None
    number: Optional[str] = None
    count: Optional[int] = None
    volume: Optional[int] = None
    alternate_number: Optional[str] = None
    alternate_count: Optional[int] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    publisher: Optional[str] = None
    imprint: Optional[str] = None
    writer: Optional[str] = None
    penciller: Optional[str] = None
    inker: Optional[str] = None
    colorist: Optional[str] = None
    letterer: Optional[str] = None
    cover_artist: Optional[str] = None
    editor: Optional[str] = None
    translator: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[str] = None
    web: Optional[str] = None
    age_rating: Optional[str] = None
    language_iso: Optional[str] = None
    format: Optional[str] = None
    is_bw: Optional[bool] = None
    manga: Optional[str] = None
    community_rating: Optional[float] = None
    review: Optional[str] = None
    page_count: Optional[int] = None
    cover_url: Optional[str] = None
    isbn: Optional[str] = None
    barcode: Optional[str] = None
    series_group: Optional[str] = None


class ComicOut(ComicBase):
    id: uuid.UUID
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComicListOut(BaseModel):
    id: uuid.UUID
    title: str
    series: Optional[str]
    number: Optional[str]
    year: Optional[int]
    publisher: Optional[str]
    cover_url: Optional[str]
    community_rating: Optional[float]

    model_config = {"from_attributes": True}


class PaginatedComics(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[ComicListOut]


# ─── Search Schema ─────────────────────────────────────────────────────────────

class SearchParams(BaseModel):
    q: Optional[str] = None
    series: Optional[str] = None
    publisher: Optional[str] = None
    writer: Optional[str] = None
    genre: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    language: Optional[str] = None
    manga: Optional[str] = None
    age_rating: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("title", pattern=r"^(title|year|publisher|community_rating|created_at)$")
    sort_order: str = Field("asc", pattern=r"^(asc|desc)$")
