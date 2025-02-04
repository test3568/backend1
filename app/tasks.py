from typing import Any

from celery.app.task import Task
import shapely
from pydantic import BaseModel
from celery import shared_task

from app.kafka import Kafka
from app.typing_models import AddOrEditPolygonCeleryTaskData, PolygonKafkaTaskData, PolygonChannelMessage, \
    DeletePolygonCeleryTaskData
from app.utils import send_message_to_all
from logger import logger
from polygons.models import Polygon


class NormalizePolygonRet(BaseModel):
    coordinates: list[list[tuple[float, float]]]
    antimeridian_crossing: bool


class WrapCoordinatesRet(BaseModel):
    coordinates: list[list[float | int]]
    antimeridian_crossing: bool


def wrap_coordinates(coords) -> WrapCoordinatesRet:
    ret = []
    antimeridian_crossing = False
    for (lon, lat) in coords[0]:
        if lat > 90:
            lat = 90
        elif lat < -90:
            lat = -90
        new_lon = ((lon + 180) % 360) - 180
        if not antimeridian_crossing and lon != new_lon:
            antimeridian_crossing = True
        ret.append([lon, lat])
    return NormalizePolygonRet(
        coordinates=ret,
        antimeridian_crossing=antimeridian_crossing
    )


def normalize_polygon(coords: list[list[float | int]]) -> NormalizePolygonRet:
    wrapped_coords: WrapCoordinatesRet = wrap_coordinates(coords)
    polygon = shapely.Polygon(wrapped_coords.coordinates)
    normalized_polygon = polygon.normalize()
    if not normalized_polygon.exterior.is_ccw:
        normalized_polygon.reverse()
    normalized_polygon_coords: list[list[tuple[float, float] | tuple[Any]]] = [
        list(zip(*normalized_polygon.exterior.coords.xy))
    ]
    return NormalizePolygonRet(
        coordinates=normalized_polygon_coords,
        antimeridian_crossing=wrapped_coords.antimeridian_crossing
    )


def _add_or_edit_polygon_task(data: str) -> None:
    try:
        data = AddOrEditPolygonCeleryTaskData.model_validate_json(data)

        geometry = data.polygon['geometry']
        new_coordinates = normalize_polygon(geometry['coordinates'])
        geometry['coordinates'] = new_coordinates.coordinates

        kafka_data = PolygonKafkaTaskData(
            request_uuid=data.request_uuid,
            user_id=data.user_id,
            name=data.name,
            polygon=geometry,
            editing_polygon_id=data.editing_polygon_id,
            antimeridian_crossing=new_coordinates.antimeridian_crossing
        )
        send_message_to_all(PolygonChannelMessage(
            type=PolygonChannelMessage.Types.new_polygon_status,
            uuid=data.request_uuid,
            status=PolygonChannelMessage.Statuses.pass_base_checks
        ))
        Kafka().add_polygon(kafka_data)
    except Exception:
        logger.exception(f'Unknown error while adding/editing polygon: {data}')
        if not isinstance(data, str):
            send_message_to_all(PolygonChannelMessage(
                type=PolygonChannelMessage.Types.new_polygon_status,
                uuid=data.request_uuid,
                status=PolygonChannelMessage.Statuses.error_base_checks
            ))


def _delete_polygon_task(data: str) -> None:
    try:
        data = DeletePolygonCeleryTaskData.model_validate_json(data)
        # Set env OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES if you got billiard.exceptions.WorkerLostError on Apple Silicon
        count = Polygon.objects.filter(id=data.polygon_id).delete()
        if count:
            send_message_to_all(PolygonChannelMessage(
                type=PolygonChannelMessage.Types.delete_polygon_status,
                uuid=data.request_uuid,
                status=PolygonChannelMessage.Statuses.success,
                polygon_id=data.polygon_id
            ))
        else:
            send_message_to_all(PolygonChannelMessage(
                type=PolygonChannelMessage.Types.delete_polygon_status,
                uuid=data.request_uuid,
                status=PolygonChannelMessage.Statuses.error_nothing_deleted
            ))
    except Exception:
        logger.exception(f'Unknown error while deleting polygon: {data}')
        if not isinstance(data, str):
            send_message_to_all(PolygonChannelMessage(
                type=PolygonChannelMessage.Types.delete_polygon_status,
                uuid=data.request_uuid,
                status=PolygonChannelMessage.Statuses.error_delete
            ))


# For IDE typing
add_or_edit_polygon_task: Task = shared_task(_add_or_edit_polygon_task)
delete_polygon_task: Task = shared_task(_delete_polygon_task)
