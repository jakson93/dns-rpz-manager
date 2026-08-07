from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dns_server import DNSServer
from app.schemas.dns_server import DNSServerCreate, DNSServerUpdate


class DNSServerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: DNSServerCreate) -> DNSServer:
        server = DNSServer(
            name=data.name,
            hostname=data.hostname,
            port=data.port,
            rndc_key=data.rndc_key,
            is_active=data.is_active,
        )
        self.db.add(server)
        await self.db.flush()
        await self.db.refresh(server)
        return server

    async def get_by_id(self, server_id: int) -> Optional[DNSServer]:
        result = await self.db.execute(select(DNSServer).where(DNSServer.id == server_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> List[DNSServer]:
        result = await self.db.execute(select(DNSServer).order_by(DNSServer.created_at.desc()))
        return result.scalars().all()

    async def update(self, server_id: int, data: DNSServerUpdate) -> Optional[DNSServer]:
        server = await self.get_by_id(server_id)
        if not server:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(server, field, value)

        await self.db.flush()
        await self.db.refresh(server)
        return server

    async def delete(self, server_id: int) -> bool:
        server = await self.get_by_id(server_id)
        if not server:
            return False

        await self.db.delete(server)
        await self.db.flush()
        return True
