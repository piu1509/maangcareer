from .viewsimport CourseViewSet, TimeTableViewSet, UserBatchViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register('list-courses', CourseViewSet, basename='list-courses')
urlpatterns = [
    # path('list-courses/', CourseViewSet.as_view(), name='list-courses'),
    path('timetable/', TimeTableViewSet.as_view(), name='timetable'),
    path('user-batch/', UserBatchViewSet.as_view(), name='user-batch'),
] + router.urls