from django.urls import path
from . import api

urlpatterns = [
    # ... your existing patterns
    path('api/search/', api.api_search, name='api_search'),
]