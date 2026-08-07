from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_db
from app.models.domain import Domain, DomainStatus
from app.models.import_record import ImportRecord
from app.models.user import User
from app.services.bind_service import BindService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.domain_service import DomainService

    domain_service = DomainService(db)
    stats = await domain_service.get_stats()

    imports_result = await db.execute(select(func.count(ImportRecord.id)))
    total_imports = imports_result.scalar()

    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar()

    return {
        **stats,
        "total_imports": total_imports,
        "total_users": total_users,
    }


@router.get("/recent-imports")
async def get_recent_imports(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ImportRecord).order_by(ImportRecord.created_at.desc()).limit(limit)
    )
    imports = result.scalars().all()

    return [
        {
            "id": imp.id,
            "filename": imp.filename,
            "total_domains": imp.total_domains,
            "new_domains": imp.new_domains,
            "status": imp.status.value,
            "created_at": imp.created_at.isoformat(),
        }
        for imp in imports
    ]


@router.get("/dns-status")
async def get_dns_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bind_service = BindService(db)
    status_list = await bind_service.get_dns_status()
    return status_list
