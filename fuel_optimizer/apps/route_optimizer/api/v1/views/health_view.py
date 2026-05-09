from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HealthView(APIView):
    """Health check endpoint."""

    def get(self, request):
        """Return health status."""
        return Response(
            {
                "status": "healthy",
                "service": "fuel-route-optimizer",
            },
            status=status.HTTP_200_OK,
        )
