import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey,
    Float, ARRAY, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    api_keys: Mapped[List["ApiKey"]] = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # first 10 chars for identification
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="api_keys")


class Comic(Base):
    __tablename__ = "comics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core identification
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    series: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    alternate_series: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # issue number
    count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # total issues
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alternate_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    alternate_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Publication info
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    imprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Creators
    writer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    penciller: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    inker: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    colorist: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    letterer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_artist: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    editor: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    translator: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Classification
    genre: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    web: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    age_rating: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language_iso: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    format: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_bw: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    manga: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Yes/No/YesAndRightToLeft

    # Ratings
    community_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Page info (no actual content stored)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Cover
    cover_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    cover_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # relative path

    # Identifiers
    isbn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    series_group: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_comics_title_series", "title", "series"),
        Index("ix_comics_year_publisher", "year", "publisher"),
    )
