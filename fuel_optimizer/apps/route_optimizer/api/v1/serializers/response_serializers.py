from rest_framework import serializers

class RouteSummarySerializer(serializers.Serializer):
    distance_miles = serializers.FloatField()
    duration_hours = serializers.FloatField()
    sampled_points = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))

class FuelStopSerializer(serializers.Serializer):
    station_id = serializers.IntegerField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    price_per_gallon = serializers.DecimalField(max_digits=6, decimal_places=3)
    distance_from_start_miles = serializers.DecimalField(max_digits=9, decimal_places=4)
    gallons_purchased = serializers.DecimalField(max_digits=6, decimal_places=4)
    cost = serializers.DecimalField(max_digits=9, decimal_places=2)

class OptimizationSerializer(serializers.Serializer):
    total_cost = serializers.DecimalField(max_digits=9, decimal_places=2)
    total_gallons = serializers.DecimalField(max_digits=9, decimal_places=4)
    stops = FuelStopSerializer(many=True)

class MetadataSerializer(serializers.Serializer):
    candidate_stations = serializers.IntegerField()
    selected_stops = serializers.IntegerField()
    optimization_runtime_ms = serializers.FloatField()
    routing_runtime_ms = serializers.FloatField()
    total_runtime_ms = serializers.FloatField()

class OptimizeRouteResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    route = RouteSummarySerializer()
    optimization = OptimizationSerializer()
    metadata = MetadataSerializer()
    message = serializers.CharField(allow_blank=True, required=False)
