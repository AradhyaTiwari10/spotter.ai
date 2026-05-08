from django.contrib import admin
from .models import FuelStation


@admin.register(FuelStation)
class FuelStationAdmin(admin.ModelAdmin):
    list_display = ('truckstop_name', 'city', 'state', 'retail_price', 'is_geocoded')
    search_fields = ('truckstop_name', 'city', 'state', 'address')

