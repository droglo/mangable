from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import generate_api_key, hash_api_key
from app.models.models import User, ApiKey
from app.schemas.schemas import ApiKeyCreate, ApiKeyOut, ApiKeyCreated

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Limit to 10 active keys per user
    result = await db.execute(
        select(ApiKey).where(ApiKey.user_id == current_user.id, ApiKey.is_active == True)
    )
    active_keys = result.scalars().all()
    if len(active_keys) >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 active API keys per user")

    full_key = generate_api_key()
    key_hash = hash_api_key(full_key)

    api_key = ApiKey(
        user_id=current_user.id,
        name=payload.name,
        key_hash=key_hash,
        key_prefix=full_key[:10],
        expires_at=payload.expires_at,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreated(
        **ApiKeyOut.model_validate(api_key).model_dump(),
        full_key=full_key,
    )


@router.get("", response_model=List[ApiKeyOut])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.user_id == current_user.id).order_by(ApiKey.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.is_active = False
    await db.commit()
