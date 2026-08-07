import math
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain import Domain, DomainOrigin, DomainStatus
from app.models.log import Log
from app.services.notification_service import notify_all
from app.utils.validators import normalize_domain


class DomainService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_domains(
        self,
        domains: List[str],
        origin: DomainOrigin,
        user_id: Optional[int] = None,
        source_file: Optional[str] = None,
        import_id: Optional[int] = None,
    ) -> Tuple[int, int]:
        new_count = 0
        skipped_count = 0
        now = datetime.utcnow()

        for domain_str in domains:
            normalized = normalize_domain(domain_str)
            if not normalized:
                continue

            existing = await self.db.execute(
                select(Domain).where(Domain.domain == normalized)
            )
            existing_domain = existing.scalar_one_or_none()

            if existing_domain:
                if existing_domain.status == DomainStatus.removed:
                    existing_domain.status = DomainStatus.active
                    existing_domain.origin = origin
                    existing_domain.source_file = source_file
                    existing_domain.import_id = import_id
                    existing_domain.added_by_user_id = user_id
                    existing_domain.imported_at = now
                    existing_domain.updated_at = now
                    new_count += 1
                else:
                    skipped_count += 1
            else:
                domain = Domain(
                    domain=normalized,
                    origin=origin,
                    source_file=source_file,
                    import_id=import_id,
                    status=DomainStatus.active,
                    added_by_user_id=user_id,
                    imported_at=now,
                )
                self.db.add(domain)
                new_count += 1

        await self.db.flush()

        if new_count > 0:
            log_entry = Log(
                event="domains_added",
                description=f"Added {new_count} domains",
                details={"count": new_count, "origin": origin.value},
                user_id=user_id,
            )
            self.db.add(log_entry)
            await self.db.flush()

        return new_count, skipped_count

    async def remove_domains(
        self,
        domain_ids: Optional[List[int]] = None,
        user_id: Optional[int] = None,
    ) -> int:
        now = datetime.utcnow()
        removed_count = 0

        if domain_ids:
            result = await self.db.execute(
                select(Domain).where(
                    and_(Domain.id.in_(domain_ids), Domain.status == DomainStatus.active)
                )
            )
            domains = result.scalars().all()
            for domain in domains:
                domain.status = DomainStatus.removed
                domain.updated_at = now
                removed_count += 1
        else:
            result = await self.db.execute(
                select(Domain).where(Domain.status == DomainStatus.active)
            )
            domains = result.scalars().all()
            for domain in domains:
                domain.status = DomainStatus.removed
                domain.updated_at = now
                removed_count += 1

        await self.db.flush()

        if removed_count > 0:
            log_entry = Log(
                event="domains_removed",
                description=f"Removed {removed_count} domains",
                details={"count": removed_count},
                user_id=user_id,
            )
            self.db.add(log_entry)
            await self.db.flush()

        return removed_count

    async def list_domains(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[DomainStatus] = None,
        origin: Optional[DomainOrigin] = None,
    ) -> dict:
        query = select(Domain)
        count_query = select(func.count(Domain.id))

        filters = []
        if search:
            filters.append(Domain.domain.ilike(f"%{search}%"))
        if status:
            filters.append(Domain.status == status)
        if origin:
            filters.append(Domain.origin == origin)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        total_pages = math.ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size

        query = query.order_by(Domain.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_stats(self) -> dict:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        active_result = await self.db.execute(
            select(func.count(Domain.id)).where(Domain.status == DomainStatus.active)
        )
        total_active = active_result.scalar()

        removed_result = await self.db.execute(
            select(func.count(Domain.id)).where(Domain.status == DomainStatus.removed)
        )
        total_removed = removed_result.scalar()

        today_added_result = await self.db.execute(
            select(func.count(Domain.id)).where(
                and_(
                    Domain.status == DomainStatus.active,
                    Domain.created_at >= today_start,
                )
            )
        )
        today_added = today_added_result.scalar()

        today_removed_result = await self.db.execute(
            select(func.count(Domain.id)).where(
                and_(
                    Domain.status == DomainStatus.removed,
                    Domain.updated_at >= today_start,
                )
            )
        )
        today_removed = today_removed_result.scalar()

        return {
            "total_active": total_active,
            "total_removed": total_removed,
            "total_domains": total_active + total_removed,
            "today_added": today_added,
            "today_removed": today_removed,
        }

    async def get_active_domains(self) -> List[str]:
        result = await self.db.execute(
            select(Domain.domain).where(Domain.status == DomainStatus.active).order_by(Domain.domain)
        )
        return [row[0] for row in result.all()]

    async def sync_domains_to_rpz(self) -> str:
        from app.services.rpz_service import RPZService
        from app.core.config import settings

        domains = await self.get_active_domains()
        rpz_service = RPZService()
        rpz_service.generate_rpz_file(domains, settings.BIND_RPZ_PATH)

        log_entry = Log(
            event="rpz_sync",
            description=f"Synced {len(domains)} domains to RPZ file",
            details={"domains_count": len(domains), "path": settings.BIND_RPZ_PATH},
        )
        self.db.add(log_entry)
        await self.db.flush()

        return settings.BIND_RPZ_PATH
