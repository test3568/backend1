from enum import Enum

from pydantic import UUID4, BaseModel


class AddOrEditPolygonCeleryTaskData(BaseModel):
    request_uuid: UUID4
    user_id: int
    name: str | None
    polygon: dict  # GeoJson geometry
    editing_polygon_id: int | None = None


class DeletePolygonCeleryTaskData(BaseModel):
    request_uuid: UUID4
    polygon_id: int


class PolygonKafkaTaskData(AddOrEditPolygonCeleryTaskData):
    antimeridian_crossing: bool


class PolygonChannelMessage(BaseModel):
    class Types(str, Enum):
        # ToDo
        new_polygon_status = 'new_polygon_status'
        delete_polygon_status = 'delete_polygon_status'
        edit_polygon_status = 'edit_polygon_status'

    class Statuses(int, Enum):
        pass_base_checks = 1
        no_intersections = 2

        success = 0

        error_base_checks = -1
        error_send_for_intersection = -2
        error_intersections_check = -3
        error_intersections_exist = -4
        error_commit = -5
        error_nothing_deleted = -6
        error_delete = -7

    type: Types
    uuid: UUID4
    status: Statuses
    intersection_polygon_ids: list[int] | None = None
    polygon: dict | None = None
    polygon_intersection: dict | None = None
    polygon_id: int | None = None
    editing_polygon_id: int | None = None
