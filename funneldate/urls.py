from django.urls import path
from .views import FunnelDateViewSet
# Add other URL patterns as needed

urlpatterns = [
    path('funneldates/',  FunnelDateViewSet.as_view(), name='funneldates'),
    
]