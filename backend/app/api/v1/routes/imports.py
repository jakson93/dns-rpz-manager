import os
import tempfile
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_db
from app.models.domain import DomainOrigin
from app.models.import_record import ImportRecord, ImportStatus
from app.models.log import Log
from app.models.user import User
from app.schemas.import_record import ImportResponse, ImportListResponse, ImportPreview
from app.services.domain_service import DomainService
from app.services.excel_service import ExcelService
from app.utils.validators import validate_file_extension

router = APIRouter(prefix="/imports", tags=["imports"])

ALLOWED_EXTENSIONS = [".xlsx", ".xls", ".csv"]


@router.post("/preview", response_model=ImportPreview)
async def preview_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not validate_file_extension(file.filename, ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        domains = ExcelService.read_excel(tmp_path)
        return ImportPreview(
            filename=file.filename,
            domains=domains,
            total_count=len(domains),
            new_domains=len(domains),
            existing_domains=0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}",
        )
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def create_import(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not validate_file_extension(file.filename, ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        domains = ExcelService.read_excel(tmp_path)
        if not domains:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid domains found in the file",
            )

        import_record = ImportRecord(
            filename=file.filename,
            total_domains=len(domains),
            user_id=current_user.id,
            status=ImportStatus.processing,
        )
        db.add(import_record)
        await db.flush()
        await db.refresh(import_record)

        domain_service = DomainService(db)
        new_count, skipped_count = await domain_service.add_domains(
            domains=domains,
            origin=DomainOrigin.excel,
            user_id=current_user.id,
            source_file=file.filename,
            import_id=import_record.id,
        )

        import_record.new_domains = new_count
        import_record.removed_domains = skipped_count
        import_record.status = ImportStatus.completed
        await db.flush()

        return ImportResponse.model_validate(import_record)

    except HTTPException:
        raise
    except Exception as e:
        if import_record:
            import_record.status = ImportStatus.error
            import_record.error_message = str(e)
            await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing import: {str(e)}",
        )
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/", response_model=ImportListResponse)
async def list_imports(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func

    query = select(ImportRecord).where(ImportRecord.user_id == current_user.id)
    count_query = select(func.count(ImportRecord.id)).where(ImportRecord.user_id == current_user.id)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size

    query = query.order_by(ImportRecord.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return ImportListResponse(
        items=[ImportResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{import_id}", response_model=ImportResponse)
async def get_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ImportRecord).where(
            ImportRecord.id == import_id,
            ImportRecord.user_id == current_user.id,
        )
    )
    import_record = result.scalar_one_or_none()

    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found",
        )

    return ImportResponse.model_validate(import_record)


@router.post("/{import_id}/preview", response_model=ImportPreview)
async def preview_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ImportRecord).where(
            ImportRecord.id == import_id,
            ImportRecord.user_id == current_user.id,
        )
    )
    import_record = result.scalar_one_or_none()

    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found",
        )

    from app.models.domain import Domain
    domains_result = await db.execute(
        select(Domain.domain).where(Domain.import_id == import_id)
    )
    domains = [row[0] for row in domains_result.all()]

    return ImportPreview(
        filename=import_record.filename,
        domains=domains,
        total_count=len(domains),
    )


@router.post("/{import_id}/apply")
async def apply_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ImportRecord).where(
            ImportRecord.id == import_id,
            ImportRecord.user_id == current_user.id,
        )
    )
    import_record = result.scalar_one_or_none()

    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found",
        )

    if import_record.status != ImportStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Import must be completed before applying",
        )

    domain_service = DomainService(db)

    rpz_path = await domain_service.sync_domains_to_rpz()

    from app.services.bind_service import BindService
    bind_service = BindService(db)
    check_result = await bind_service.check_zone()

    if not check_result["success"]:
        log_entry = Log(
            event="rpz_validation_failed",
            description=f"named-checkzone failed: {check_result['stderr']}",
            details=check_result,
            user_id=current_user.id,
        )
        db.add(log_entry)
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RPZ validation failed: {check_result['stderr']}",
        )

    reload_results = await bind_service.reload_dns()

    from app.services.notification_service import notify_all
    await notify_all(
        f"BLOQUEIO DNS ATUALIZADO\n"
        f"Arquivo: {import_record.filename}\n"
        f"Domínios no arquivo: {import_record.total_domains}\n"
        f"Novos bloqueios: {import_record.new_domains}\n"
        f"RPZ: OK\n"
        f"BIND: Reload realizado em {len(reload_results)} servidor(es)"
    )

    return {
        "success": True,
        "rpz_path": rpz_path,
        "check_zone": check_result,
        "reload_results": reload_results,
        "message": "Import applied successfully",
    }
