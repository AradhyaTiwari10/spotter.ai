from django.urls import path
from .views import health

app_name = 'route_optimizer_api'

urlpatterns = [
    path('health/', health, name='health'),
    # future: path('routes/', include(...))
]
