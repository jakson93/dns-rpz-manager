from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_db
from app.models.domain import DomainOrigin, DomainStatus
from app.models.user import User
from app.schemas.domain import (
    DomainCreate,
    DomainListResponse,
    DomainResponse,
    DomainStats,
)
from app.services.domain_service import DomainService

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("/", response_model=DomainListResponse)
async def list_domains(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[DomainStatus] = None,
    origin: Optional[DomainOrigin] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain_service = DomainService(db)
    result = await domain_service.list_domains(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        origin=origin,
    )

    return DomainListResponse(
        items=[DomainResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.post("/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def add_domain(
    domain_data: DomainCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain_service = DomainService(db)
    new_count, _ = await domain_service.add_domains(
        domains=[domain_data.domain],
        origin=DomainOrigin.manual,
        user_id=current_user.id,
    )

    if new_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain already exists or is invalid",
        )

    from app.models.domain import Domain
    from sqlalchemy import select

    result = await db.execute(
        select(Domain).where(Domain.domain == domain_data.domain.lower().strip())
    )
    domain = result.scalar_one()

    return DomainResponse.model_validate(domain)


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.domain import Domain
    from sqlalchemy import select

    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    domain_service = DomainService(db)
    await domain_service.remove_domains(
        domain_ids=[domain_id],
        user_id=current_user.id,
    )


@router.patch("/{domain_id}/status", response_model=DomainResponse)
async def update_domain_status(
    domain_id: int,
    new_status: DomainStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.domain import Domain
    from sqlalchemy import select
    from datetime import datetime

    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    domain.status = new_status
    domain.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(domain)

    return DomainResponse.model_validate(domain)


@router.get("/stats", response_model=DomainStats)
async def get_domain_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain_service = DomainService(db)
    stats = await domain_service.get_stats()
    return DomainStats(**stats)


@router.post("/sync-rpz")
async def sync_domains_to_rpz(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain_service = DomainService(db)
    rpz_path = await domain_service.sync_domains_to_rpz()
    return {"message": "Domains synced to RPZ file", "path": rpz_path}
