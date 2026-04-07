


from fastapi import APIRouter, Depends, HTTPException, status

from application.dtos.road import SnapPointRequestDTO, SnapPointResponseDTO
from application.usecases.road.snap_point import BaseSnapPointUseCase
from presentation.api.v1.schemas.road import ErrorResponseSchema, SnapPointRequestSchema, SnapPointResponseSchema

router = APIRouter(
    prefix="/v1",
    tags=["roads"]
)

@router.post(
    "/snap-point",
    response_model=SnapPointResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponseSchema},
        404: {"model": ErrorResponseSchema},
        500: {"model": ErrorResponseSchema}
    }
)
async def snap_point(
    request: SnapPointRequestSchema,
    snap_usecase: BaseSnapPointUseCase = Depends()
):
    try:
        dto = SnapPointRequestDTO(
            longitude=request.longitude,
            latitude=request.latitude,
            max_distance_meters=request.max_distance_meters
        )
        
        result: SnapPointResponseDTO = await snap_usecase.execute(dto)
        
        return SnapPointResponseSchema(
            snapped_longitude=result.snapped_longitude,
            snapped_latitude=result.snapped_latitude,
            original_longitude=result.original_longitude,
            original_latitude=result.original_latitude,
            distance_meters=result.distance_meters,
            road_info=result.road_info
        )
    except ValueError as e:
        if "No road found" in str(e):
            raise HTTPException(
                status_code=404,
                detail=ErrorResponseSchema(error="Road not found", detail=str(e)).dict()
            )
        raise HTTPException(
            status_code=400,
            detail=ErrorResponseSchema(error="Invalid request", detail=str(e)).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseSchema(error="Internal error", detail=str(e)).dict()
        )