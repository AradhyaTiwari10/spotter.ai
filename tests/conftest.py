"""Pytest configuration and fixtures for tests."""
import os
import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings before running tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_optimizer.config.settings.local')
    
    if not settings.configured:
        django.setup()
