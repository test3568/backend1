import uuid

from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import serializers, generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from app.tasks import add_or_edit_polygon_task, AddOrEditPolygonCeleryTaskData, delete_polygon_task
from app.typing_models import DeletePolygonCeleryTaskData
from logger import logger
from polygons.models import Polygon, PolygonIntersection

uuid_parameter = OpenApiParameter(
    name='uuid', description='UUID for websocket callbacks with task progress',
    examples=[OpenApiExample('Example', value=uuid.uuid4(), request_only=True)]
)

class PolygonSerializerMeta:
    model = Polygon
    geo_field = "polygon"
    fields = ()


class PolygonSerializer(GeoFeatureModelSerializer):
    class Meta(PolygonSerializerMeta):
        pass


class DbPolygonSerializer(PolygonSerializer):
    class Meta(PolygonSerializerMeta):
        fields = ('id', "name", "antimeridian_crossing")


class DeletePolygonSerializer(serializers.Serializer):
    polygon_id = serializers.IntegerField(required=True)
    uuid = serializers.UUIDField(required=True)


class AddPolygonSerializer(serializers.Serializer):
    polygon = PolygonSerializer()
    uuid = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, min_length=2, max_length=512)


class EditPolygonSerializer(AddPolygonSerializer):
    editing_polygon_id = serializers.IntegerField(required=False)


class PolygonViewSet(generics.GenericAPIView):
    serializer_class = DbPolygonSerializer

    @extend_schema(
        description='Get all polygons in GeoJson format',
        responses=DbPolygonSerializer(many=True)
    )
    def get(self, request: Request):
        cached_data = cache.get(settings.CACHE_POLYGONS_GET_KEY)
        if cached_data:
            return JsonResponse(cached_data)
        polygons = Polygon.objects.order_by("-created").all()
        serializer = DbPolygonSerializer(polygons, many=True)
        cache.set(settings.CACHE_POLYGONS_GET_KEY, serializer.data, timeout=None)
        return JsonResponse(serializer.data)

    @extend_schema(
        description='Delete polygon by ID',
        parameters=[
            DeletePolygonSerializer,
            OpenApiParameter(name='polygon_id', description='Polygon ID to delete', type=int),
            uuid_parameter
        ]
    )
    def delete(self, request: Request):
        serializer = DeletePolygonSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f'Delete polygon serializer error: {serializer.errors}')
            return Response(status=400)
        data = DeletePolygonCeleryTaskData(
            request_uuid=serializer.data['uuid'],
            polygon_id=serializer.data['polygon_id'],
        )
        delete_polygon_task.delay(
            data.model_dump_json()
        )
        return Response(status=200)

    @extend_schema(
        description='Create new polygon',
        request=AddPolygonSerializer
    )
    def post(self, request: Request):
        serializer = AddPolygonSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f'Create polygon serializer error: {serializer.errors}')
            return Response(status=400)
        # ToDo user id
        data = AddOrEditPolygonCeleryTaskData(
            request_uuid=str(serializer.data['uuid']),
            user_id=1,
            name=serializer.data['name'],
            polygon=serializer.data['polygon'],
            editing_polygon_id=None
        )
        add_or_edit_polygon_task.delay(
            data.model_dump_json()
        )
        return Response(status=200)

    @extend_schema(
        description='Edit polygon',
        request=EditPolygonSerializer
    )
    def put(self, request: Request):
        serializer = EditPolygonSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f'Edit polygon serializer error: {serializer.errors}')
            return Response(status=400)
        # ToDo user id
        data = AddOrEditPolygonCeleryTaskData(
            request_uuid=str(serializer.data['uuid']),
            user_id=1,
            name=serializer.data['name'],
            polygon=serializer.data['polygon'],
            editing_polygon_id=serializer.data.get('editing_polygon_id')
        )
        add_or_edit_polygon_task.delay(
            data.model_dump_json()
        )
        return Response(status=200)


class IntersectionSerializer(PolygonSerializer):
    class Meta:
        model = PolygonIntersection
        geo_field = "polygon"
        fields = ('id', "name", "antimeridian_crossing", "edited_polygon_id", "intersection_polygon_ids")


class IntersectionsViewSet(generics.GenericAPIView):
    serializer_class = IntersectionSerializer

    @extend_schema(
        description='Get all polygons with an intersection error in GeoJson format',
        responses=IntersectionSerializer(many=True)
    )
    def get(self, request: Request):
        cached_data = cache.get(settings.CACHE_INTERSECTIONS_GET_KEY)
        if cached_data:
            return JsonResponse(cached_data)
        polygons = PolygonIntersection.objects.order_by("-created").all()[:30]
        serializer = IntersectionSerializer(polygons, many=True)
        cache.set(settings.CACHE_INTERSECTIONS_GET_KEY, serializer.data, timeout=None)
        return JsonResponse(serializer.data)


class HealthCheckViewSet(generics.GenericAPIView):
    serializer_class = None

    @extend_schema(
        description='Healthcheck route that just returns code 200'
    )
    def get(self, request: Request):
        return Response(status=200)
