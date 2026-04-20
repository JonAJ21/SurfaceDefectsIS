import json
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Header, Path, Query, UploadFile as UF, status
from pydantic import Field, WithJsonSchema

from application.usecases.defects.get_by_user_id import BaseDefectGetByUserIdUseCase
from application.usecases.defects.get_in_vieport import BaseDefectGetInViewPortUseCase
from domain.exceptions.base import DomainException
from application.dtos.user import UserAuthRequestDTO
from application.usecases.user.auth import BaseUserAuthUseCase
from application.usecases.defects.delete import BaseDefectDeleteUseCase, DefectDeleteUseCase
from application.usecases.defects.update import BaseDefectUpdateUseCase
from application.usecases.defects.moderate import BaseDefectModerateUseCase, DefectModerateUseCase
from application.usecases.defects.get_pending import BaseDefectGetPendingUseCase
from application.usecases.defects.get_nearby import BaseDefectGetNearbyUseCase
from application.usecases.defects.get import BaseDefectGetUseCase, BaseDefectsGetUseCase, DefectGetUseCase
from application.dtos.defect import DefectCreateRequestDTO, DefectCreateResponseDTO, DefectDeleteRequestDTO, DefectDeleteResponseDTO, DefectGetByUserIdRequestDTO, DefectGetByUserIdResponseDTO, DefectGetInViewPortRequestDTO, DefectGetInViewPortResponseDTO, DefectGetNearbyRequestDTO, DefectGetNearbyResponseDTO, DefectGetPendingRequestDTO, DefectGetPendingResponseDTO, DefectGetRequestDTO, DefectGetResponseDTO, DefectModerateRequestDTO, DefectModerateResponseDTO, DefectUpdateRequestDTO, DefectUpdateResponseDTO, DefectsGetRequestDTO, PhotoUploadDTO
from application.usecases.defects.create import BaseDefectCreateUseCase
from domain.values.defect_types import DefectStatus, DefectType, GeometryType, SeverityLevel
from presentation.api.v1.schemas.defect import DefectResponse, ErrorResponse
from presentation.api.v1.security.security import security_scheme

UploadFile = Annotated[UF, WithJsonSchema({"type": "string", "format": "binary"})]

router = APIRouter(
    prefix="/v1",
    tags=["defects"]
)


@router.post(
    "/defects/create",
    response_model=DefectCreateResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def create_defect(
    defect_type: DefectType = Form(...),
    severity: SeverityLevel = Form(...),
    geometry_type: GeometryType = Form(...),
    coordinates: str = Form(..., description="JSON string of coordinates"),
    description: Optional[str] = Form(None),
    max_distance_meters: int = Form(15),
    photos: List[UploadFile] = File(..., description="At least one photo required"),
    create_usecase: BaseDefectCreateUseCase = Depends(),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    credentials: str = Depends(security_scheme),
):
    """
    Создание нового дефекта с фотографиями.
    Поддерживает точечные и линейные дефекты.
    """
    access_token = credentials.credentials
    # Проверяем доступ пользователя
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        # needed_permission_codes=['defects.create']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
    except DomainException as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    if auth_result.is_verified == False:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )
    user_id = auth_result.user_oid
    
    # Парсим координаты из JSON строки
    try:
        coords = json.loads(coordinates)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid coordinates format. Expected JSON array."
        )
    
    # Проверяем, что есть хотя бы одно фото
    if not photos or len(photos) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one photo is required"
        )
    
    # Читаем фото
    photo_dtos = []
    for photo in photos:
        if not photo.filename:
            continue
            
        content = await photo.read()
        
        if len(content) == 0:
            continue
            
        if len(content) > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(
                status_code=400,
                detail=f"Photo {photo.filename} exceeds 10MB limit"
            )
        
        photo_dtos.append(
            PhotoUploadDTO(
                filename=photo.filename,
                data=content,
                content_type=photo.content_type or "image/jpeg"
            )
        )
    
    if not photo_dtos:
        raise HTTPException(
            status_code=400,
            detail="No valid photos provided"
        )
    
    # Создаём DTO
    request_dto = DefectCreateRequestDTO(
        defect_type=defect_type,
        severity=severity,
        geometry_type=geometry_type,
        coordinates=coords,
        description=description,
        created_by=user_id,
        photos=photo_dtos,
        max_distance_meters=max_distance_meters
    )
    
    try:
        result = await create_usecase.execute(request_dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

@router.get(
    "/defects/{defect_id}",
    response_model=DefectGetResponseDTO,
    responses={404: {"model": ErrorResponse}}
)
async def get_defect(
    defect_id: UUID,
    get_usecase: BaseDefectGetUseCase = Depends()
):
    """Получение дефекта по ID"""
    request_dto = DefectGetRequestDTO(defect_id=defect_id)
    
    try:
        result = await get_usecase.execute(request_dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get(
    "/users/{user_id}/defects",
    response_model=list[DefectGetByUserIdResponseDTO],
    responses={404: {"model": ErrorResponse}}
)
async def get_defects_by_user_id(
    user_id: str = Path(...),
    limit: int = Query(100, ge=1, description="Количество дефектов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    get_usecase: BaseDefectGetByUserIdUseCase = Depends()
):
    """Получение дефекта по ID"""
    request_dto = DefectGetByUserIdRequestDTO(
        user_id=user_id,
        limit=limit,
        offset=offset
    )  
    try:
        result = await get_usecase.execute(request_dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get(
    "/defects/nearby/",
    response_model=List[DefectGetNearbyResponseDTO]
)
async def get_defects_nearby(
    longitude: float = Query(..., ge=-180, le=180, description="Долгота"),
    latitude: float = Query(..., ge=-90, le=90, description="Широта"),
    radius_meters: float = Query(100, ge=10, le=5000, description="Радиус поиска в метрах"),
    defect_types: Optional[List[DefectType]] = Query(None, description="Фильтр по типам дефектов"),
    min_severity: Optional[SeverityLevel] = Query(None, description="Минимальный уровень опасности"),
    get_usecase: BaseDefectGetNearbyUseCase = Depends()
):
    """
    Получение дефектов в радиусе.
    Возвращает только подтверждённые дефекты.
    """
    request_dto = DefectGetNearbyRequestDTO(
        longitude=longitude,
        latitude=latitude,
        radius_meters=radius_meters,
        defect_types=defect_types,
        min_severity=min_severity
    )
    
    return await get_usecase.execute(request_dto)


@router.get(
    "/defects",
    response_model=List[DefectGetResponseDTO]
)
async def get_defects(
    defect_statuses: Optional[List[DefectStatus]] = Query(None, description="Фильтр по статусу дефекта"),
    defect_types: Optional[List[DefectType]] = Query(None, description="Фильтр по типам дефектов"),
    min_severity: Optional[SeverityLevel] = Query(None, description="Минимальный уровень опасности"),
    limit: int = Query(100, ge=1, description="Количество дефектов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    get_usecase: BaseDefectsGetUseCase = Depends()
):
    """
    Получение дефектов
    """
    request_dto = DefectsGetRequestDTO(
        defect_statuses=defect_statuses,
        defect_types=defect_types,
        min_severity=min_severity,
        limit=limit,
        offset=offset
    )
    
    return await get_usecase.execute(request_dto)

@router.get(
    "/defects/viewport/",
    response_model=List[DefectGetInViewPortResponseDTO]
)
async def get_defects_in_viewport(
    min_longitude: float = Query(..., ge=-180, le=180, description="Долгота"),
    min_latitude: float = Query(..., ge=-90, le=90, description="Широта"),
    max_longitude: float = Query(..., ge=-180, le=180, description="Долгота"),
    max_latitude: float = Query(..., ge=-90, le=90, description="Широта"),
    defect_types: Optional[List[DefectType]] = Query(None, description="Фильтр по типам дефектов"),
    min_severity: Optional[SeverityLevel] = Query(None, description="Минимальный уровень опасности"),
    limit: int = Query(100, ge=1, description="Количество дефектов"),
    get_usecase: BaseDefectGetInViewPortUseCase = Depends()
):
    """
    Получение дефектов внутри прямоугольника (viewport/bounding box).
    Возвращает только подтверждённые дефекты.
    """
    request_dto = DefectGetInViewPortRequestDTO(
        min_lon=min_longitude,
        min_lat=min_latitude,
        max_lon=max_longitude,
        max_lat=max_latitude,
        defect_types=defect_types,
        min_severity=min_severity,
        limit=limit
    )
    
    return await get_usecase.execute(request_dto)


@router.get(
    "/defects/pending/",
    response_model=List[DefectGetPendingResponseDTO]
)
async def get_pending_defects(
    limit: int = Query(100, ge=1, le=500, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    get_usecase: BaseDefectGetPendingUseCase = Depends(),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    credentials: str = Depends(security_scheme),
):
    """
    Получение дефектов на модерацию.
    Только для модераторов.
    """
    
    access_token = credentials.credentials
    # Проверяем доступ пользователя
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        # needed_permission_codes=['defects.create']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
    except DomainException as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    if auth_result.is_verified == False:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )
    moderator_id = auth_result.user_oid
    
    
    request_dto = DefectGetPendingRequestDTO(limit=limit, offset=offset)
    
    return await get_usecase.execute(request_dto)


@router.patch(
    "/defects/{defect_id}/moderate",
    response_model=DefectModerateResponseDTO,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def moderate_defect(
    defect_id: UUID,
    status: DefectStatus = Query(..., description="Новый статус (approved, rejected)"),
    rejection_reason: Optional[str] = Query(None, description="Причина отклонения (обязательно для rejected)"),
    moderate_usecase: BaseDefectModerateUseCase = Depends(),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    credentials: str = Depends(security_scheme),
):
    """
    Модерация дефекта.
    Только для модераторов.
    
    - **status**: Новый статус (approved, rejected)
    - **rejection_reason**: Причина отклонения (обязательно для rejected)
    """
    access_token = credentials.credentials
    # Проверяем доступ пользователя
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        # needed_permission_codes=['defects.create']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
    except DomainException as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    if auth_result.is_verified == False:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )
    moderator_id = auth_result.user_oid
    
    if status == DefectStatus.REJECTED and not rejection_reason:
        raise HTTPException(
            status_code=400,
            detail="rejection_reason is required when rejecting a defect"
        )
    
    request_dto = DefectModerateRequestDTO(
        defect_id=defect_id,
        status=status,
        moderated_by=moderator_id,
        rejection_reason=rejection_reason
    )
    
    try:
        result = await moderate_usecase.execute(request_dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.patch(
    "/defects/{defect_id}/update",
    response_model=DefectUpdateResponseDTO,
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def update_defect(
    defect_id: UUID,
    defect_type: Optional[DefectType] = None,
    severity: Optional[SeverityLevel] = None,
    fixed: Optional[bool] = None,
    description: Optional[str] = None,
    update_usecase: BaseDefectUpdateUseCase = Depends(),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    credentials: str = Depends(security_scheme),
):
    """Обновление дефекта (только для создателя)"""
    access_token = credentials.credentials
    # Проверяем доступ пользователя
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        # needed_permission_codes=['defects.update']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
    except DomainException as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    if auth_result.is_verified == False:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )
    user_id = auth_result.user_oid
    
    request_dto = DefectUpdateRequestDTO(
        defect_id=defect_id,
        defect_type=defect_type,
        severity=severity,
        description=description,
        updated_by=user_id,
        fixed=fixed
    )
    
    try:
        result = await update_usecase.execute(request_dto)
        return result
    except ValueError as e:
        if "can only update your own" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.delete(
    "/defects/{defect_id}",
    response_model=DefectDeleteResponseDTO,
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def delete_defect(
    defect_id: UUID,
    delete_usecase: BaseDefectDeleteUseCase = Depends(),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    credentials: str = Depends(security_scheme),
):
    """Удаление дефекта (только для создателя)"""
    access_token = credentials.credentials
    # Проверяем доступ пользователя
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        # needed_permission_codes=['defects.create']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
    except DomainException as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    if auth_result.is_verified == False:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )
    user_id = auth_result.user_oid
    
    request_dto = DefectDeleteRequestDTO(
        defect_id=defect_id,
        deleted_by=user_id
    )
    
    result = await delete_usecase.execute(request_dto)
    
    if not result.success:
        if "only delete your own" in result.message.lower():
            raise HTTPException(status_code=403, detail=result.message)
        raise HTTPException(status_code=404, detail=result.message)
    
    return result