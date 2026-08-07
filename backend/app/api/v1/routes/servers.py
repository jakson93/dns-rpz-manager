from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.dns_server import DNSServerCreate, DNSServerUpdate, DNSServerResponse
from app.services.bind_service import BindService
from app.services.dns_server_service import DNSServerService

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/", response_model=List[DNSServerResponse])
async def list_servers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DNSServerService(db)
    servers = await service.list_all()
    return [DNSServerResponse.model_validate(s) for s in servers]


@router.post("/", response_model=DNSServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: DNSServerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DNSServerService(db)
    server = await service.create(server_data)
    return DNSServerResponse.model_validate(server)


@router.get("/{server_id}", response_model=DNSServerResponse)
async def get_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DNSServerService(db)
    server = await service.get_by_id(server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS server not found",
        )
    return DNSServerResponse.model_validate(server)


@router.put("/{server_id}", response_model=DNSServerResponse)
async def update_server(
    server_id: int,
    server_data: DNSServerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DNSServerService(db)
    server = await service.update(server_id, server_data)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS server not found",
        )
    return DNSServerResponse.model_validate(server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DNSServerService(db)
    deleted = await service.delete(server_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS server not found",
        )


@router.post("/{server_id}/reload")
async def reload_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bind_service = BindService(db)
    results = await bind_service.reload_dns(server_id=server_id)
    return {"results": results}


@router.post("/reload-all")
async def reload_all_servers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bind_service = BindService(db)
    results = await bind_service.reload_dns()
    return {"results": results}
