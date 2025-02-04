from django.urls import path

from . import views, ws_consumer

urlpatterns = [
    path("polygons", views.PolygonViewSet.as_view(), name="polygons"),
    path("intersections", views.IntersectionsViewSet.as_view(), name="intersections"),
]

websocket_urlpatterns = [
    path("ws", ws_consumer.WsConsumer.as_asgi())
]
