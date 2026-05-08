from django.urls import path
from .v1.views.optimization_view import OptimizeRouteView

urlpatterns = [
    path('optimize-route/', OptimizeRouteView.as_view(), name='optimize-route'),
]
