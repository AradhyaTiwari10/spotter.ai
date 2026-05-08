from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def health(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'fuel-route-optimizer'
    })
