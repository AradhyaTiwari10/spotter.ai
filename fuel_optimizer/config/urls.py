from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path('api/v1/', include('fuel_optimizer.apps.route_optimizer.api.urls')),
]
