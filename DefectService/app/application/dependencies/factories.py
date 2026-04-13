
from functools import cache

from fastapi import Depends

from application.usecases.defects.get_by_user_id import BaseDefectGetByUserIdUseCase, DefectGetByUserIdUseCase
from application.usecases.defects.get_in_vieport import BaseDefectGetInViewPortUseCase, DefectGetInViewPortUseCase
from domain.services.token import BaseTokenService
from infrastructure.services.token import JSONWebTokenService
from application.usecases.user.auth import BaseUserAuthUseCase, UserAuthUseCase
from application.usecases.road.snap_point import BaseSnapPointUseCase, SnapPointUseCase
from application.usecases.road.snap_linestring import BaseSnapLinestringUseCase, SnapLinestringUseCase
from application.usecases.defects.delete import BaseDefectDeleteUseCase, DefectDeleteUseCase
from application.usecases.defects.get_pending import BaseDefectGetPendingUseCase, DefectGetPendingUseCase
from application.usecases.defects.moderate import BaseDefectModerateUseCase, DefectModerateUseCase
from application.usecases.defects.update import BaseDefectUpdateUseCase, DefectUpdateUseCase
from application.usecases.defects.get_nearby import BaseDefectGetNearbyUseCase, DefectGetNearbyUseCase
from application.usecases.defects.get import BaseDefectGetUseCase, DefectGetUseCase
from application.usecases.defects.create import BaseDefectCreateUseCase, DefectCreateUseCase
from application.dependencies.registrator import add_factory_to_mapper
from infrastructure.services.road import OSMRoadSnappingService
from domain.services.road import BaseRoadSnappingService
from infrastructure.repositories.uow import SQLAlchemyUnitOfWork
from domain.repositories.uow import BaseUnitOfWork
from infrastructure.database.session import async_session_maker

def uow_factory() -> BaseUnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory=async_session_maker)

@cache 
def token_service_factory() -> BaseTokenService:
    return JSONWebTokenService()

def get_road_snapping_service(uow: BaseUnitOfWork) -> BaseRoadSnappingService:
    return OSMRoadSnappingService(uow)

@add_factory_to_mapper(BaseDefectCreateUseCase)
@cache
def defect_create_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectCreateUseCase:
    return DefectCreateUseCase(uow)

@add_factory_to_mapper(BaseDefectGetUseCase)
@cache
def defect_get_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectGetUseCase:
    return DefectGetUseCase(uow)

@add_factory_to_mapper(BaseDefectGetNearbyUseCase)
@cache
def defect_get_nearby_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectGetNearbyUseCase:
    return DefectGetNearbyUseCase(uow)

@add_factory_to_mapper(BaseDefectGetInViewPortUseCase)
@cache
def defect_get_in_viewport_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectGetInViewPortUseCase:
    return DefectGetInViewPortUseCase(uow)

@add_factory_to_mapper(BaseDefectGetByUserIdUseCase)
@cache
def defect_get_by_user_id_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectGetByUserIdUseCase:
    return DefectGetByUserIdUseCase(uow)

@add_factory_to_mapper(BaseDefectGetPendingUseCase)
@cache
def defect_get_pending_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectGetPendingUseCase:
    return DefectGetPendingUseCase(uow)

@add_factory_to_mapper(BaseDefectModerateUseCase)
@cache
def defect_moderate_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectModerateUseCase:
    return DefectModerateUseCase(uow)

@add_factory_to_mapper(BaseDefectUpdateUseCase)
@cache
def defect_update_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectUpdateUseCase:
    return DefectUpdateUseCase(uow)

@add_factory_to_mapper(BaseDefectDeleteUseCase)
@cache
def defect_delete_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseDefectDeleteUseCase:
    return DefectDeleteUseCase(uow)

@add_factory_to_mapper(BaseSnapLinestringUseCase)
@cache
def snap_linestring_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseSnapLinestringUseCase:
    return SnapLinestringUseCase(uow)

@add_factory_to_mapper(BaseSnapPointUseCase)
@cache
async def get_snap_point_use_case(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseSnapPointUseCase:
    return SnapPointUseCase(uow)

@add_factory_to_mapper(BaseUserAuthUseCase)
@cache
def user_auth_usecase_factory(
    jwt_service: BaseTokenService = Depends(token_service_factory)
) -> BaseUserAuthUseCase:
    return UserAuthUseCase(jwt_service)