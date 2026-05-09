from django.urls import path
from .v1.views.optimization_view import OptimizeRouteView
from .v1.views.health_view import HealthView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('optimize-route/', OptimizeRouteView.as_view(), name='optimize-route'),
]
