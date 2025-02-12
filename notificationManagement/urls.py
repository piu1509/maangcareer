from django.urls import path
from .views import *

urlpatterns = [
    path('mark-notification-as-read/', MarkNotificationAsRead.as_view(), name='mark-notification-as-read'),
    
]
