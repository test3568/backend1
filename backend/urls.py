from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from app import views


urlpatterns = [
    path("app/", include("app.urls"), name="polygons"),
    path("healthcheck", views.HealthCheckViewSet.as_view(), name="healthcheck"),
    path('oa3-schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('admin/', admin.site.urls),
]
