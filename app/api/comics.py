import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, asc, desc

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Comic
from app.schemas.schemas import (
    ComicCreate, ComicUpdate, ComicOut, ComicListOut, PaginatedComics, SearchParams
)
from app.services.comicinfo import generate_comicinfo_xml

router = APIRouter(prefix="/comics", tags=["Comics"])


def build_search_query(params: SearchParams):
    filters = []

    if params.q:
        q = f"%{params.q}%"
        filters.append(
            or_(
                Comic.title.ilike(q),
                Comic.series.ilike(q),
                Comic.summary.ilike(q),
                Comic.writer.ilike(q),
                Comic.publisher.ilike(q),
            )
        )
    if params.series:
        filters.append(Comic.series.ilike(f"%{params.series}%"))
    if params.publisher:
        filters.append(Comic.publisher.ilike(f"%{params.publisher}%"))
    if params.writer:
        filters.append(Comic.writer.ilike(f"%{params.writer}%"))
    if params.genre:
        filters.append(Comic.genre.ilike(f"%{params.genre}%"))
    if params.year_from:
        filters.append(Comic.year >= params.year_from)
    if params.year_to:
        filters.append(Comic.year <= params.year_to)
    if params.language:
        filters.append(Comic.language_iso == params.language)
    if params.manga:
        filters.append(Comic.manga == params.manga)
    if params.age_rating:
        filters.append(Comic.age_rating == params.age_rating)

    return filters


@router.get("", response_model=PaginatedComics)
async def list_comics(
    q: Optional[str] = Query(None, description="Full-text search"),
    series: Optional[str] = Query(None),
    publisher: Optional[str] = Query(None),
    writer: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    language: Optional[str] = Query(None),
    manga: Optional[str] = Query(None),
    age_rating: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("title", pattern=r"^(title|year|publisher|community_rating|created_at)$"),
    sort_order: str = Query("asc", pattern=r"^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    params = SearchParams(
        q=q, series=series, publisher=publisher, writer=writer, genre=genre,
        year_from=year_from, year_to=year_to, language=language, manga=manga,
        age_rating=age_rating, page=page, page_size=page_size,
        sort_by=sort_by, sort_order=sort_order,
    )
    filters = build_search_query(params)

    sort_col = getattr(Comic, params.sort_by)
    order_fn = asc if params.sort_order == "asc" else desc

    # Count
    count_q = select(func.count(Comic.id))
    if filters:
        count_q = count_q.where(and_(*filters))
    total = (await db.execute(count_q)).scalar_one()

    # Fetch
    offset = (params.page - 1) * params.page_size
    data_q = select(Comic).order_by(order_fn(sort_col)).offset(offset).limit(params.page_size)
    if filters:
        data_q = data_q.where(and_(*filters))

    result = await db.execute(data_q)
    comics = result.scalars().all()

    return PaginatedComics(
        total=total,
        page=params.page,
        page_size=params.page_size,
        results=[ComicListOut.model_validate(c) for c in comics],
    )


@router.post("", response_model=ComicOut, status_code=status.HTTP_201_CREATED)
async def create_comic(
    payload: ComicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    comic = Comic(**payload.model_dump(), created_by=current_user.id)
    db.add(comic)
    await db.commit()
    await db.refresh(comic)
    return comic


@router.get("/{comic_id}", response_model=ComicOut)
async def get_comic(
    comic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Comic).where(Comic.id == comic_id))
    comic = result.scalar_one_or_none()
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    return comic


@router.patch("/{comic_id}", response_model=ComicOut)
async def update_comic(
    comic_id: uuid.UUID,
    payload: ComicUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comic).where(Comic.id == comic_id))
    comic = result.scalar_one_or_none()
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    if comic.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed to edit this comic")

    update_data = payload.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(comic, key, value)

    await db.commit()
    await db.refresh(comic)
    return comic


@router.delete("/{comic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comic(
    comic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comic).where(Comic.id == comic_id))
    comic = result.scalar_one_or_none()
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    if comic.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed to delete this comic")
    await db.delete(comic)
    await db.commit()


# ─── ComicInfo.xml Download ────────────────────────────────────────────────────

@router.get("/{comic_id}/comicinfo.xml", response_class=Response)
async def download_comicinfo(
    comic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Download ComicInfo.xml for a comic."""
    result = await db.execute(select(Comic).where(Comic.id == comic_id))
    comic = result.scalar_one_or_none()
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")

    xml_content = generate_comicinfo_xml(comic)
    filename = f"ComicInfo-{comic.id}.xml"

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─── Cover URL ─────────────────────────────────────────────────────────────────

@router.get("/{comic_id}/cover")
async def get_cover_url(
    comic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return the cover image URL for a comic."""
    result = await db.execute(select(Comic).where(Comic.id == comic_id))
    comic = result.scalar_one_or_none()
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    if not comic.cover_url:
        raise HTTPException(status_code=404, detail="No cover image set for this comic")
    return {"comic_id": str(comic_id), "cover_url": comic.cover_url}
