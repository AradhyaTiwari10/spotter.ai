from rest_framework import serializers

class OptimizeRouteRequestSerializer(serializers.Serializer):
    start = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)

    def validate(self, attrs):
        start = attrs.get('start','').strip()
        dest = attrs.get('destination','').strip()
        if not start or not dest:
            raise serializers.ValidationError('start and destination must be non-empty strings')
        if start == dest:
            raise serializers.ValidationError('start and destination must be different')
        return attrs
