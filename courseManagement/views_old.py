# from django.shortcuts import render
from django.db.models import Q
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView

from rest_framework.serializers import ModelSerializer
from .models import Course, Week, TimeTable, Batch

from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from datetime import date

class WeekSerializer(ModelSerializer):
    class Meta:
        model = Week
        fields = (
            "name",
            # "course",
            "lock",
            "lessons"
        )
        depth=1
class CourseSerializer(ModelSerializer):
    syllabi = WeekSerializer(many=True)
    class Meta:
        model = Course
        fields = (
            "author_message",
            "author_name",
            "author_photo",
            "caption",
            "certificate",
            "class_duration",
            "course_duration",
            "demo_video",
            "description",
            "discount_percentage",
            "id",
            "lectures",
            "mobile_computer",
            "name",
            "popular",
            "pre_recorded",
            "premium",
            "price",
            "projects",
            "requirements",
            "short_description",
            "thumbnail",
            "payment_id",
            "syllabi",
        )
class CourseListSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "course_duration",
            "discount_percentage",
            "id",
            "lectures",
            "name",
            "popular",
            "premium",
            "price",
            "projects",
            "short_description",
            "thumbnail",
            "payment_id"
        )

class CourseViewSet(ViewSet):
    """
    A simple ViewSet for listing Courses.
    """
    def list(self, request):
        queryset = Course.objects.filter(archive=False)
        serializer = CourseListSerializer(queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        queryset = Course.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = CourseSerializer(user)
        return Response(serializer.data)
    
class TimeTableSerializer(ModelSerializer):
    class Meta:
        model = TimeTable
        fields = '__all__'
class TimeTableViewSet(ListAPIView):
    queryset = TimeTable.objects.filter(Q(start_date__lte=date.today()))
    serializer_class = TimeTableSerializer

class NewCourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('id','name')
class UserBatchSerializer(ModelSerializer):
    timetable = TimeTableSerializer(many=True)
    course = NewCourseSerializer()
    class Meta:
        model = Batch
        fields = (
            'id',
            'name',
            'course',
            # 'instructor',
            'timetable'
        )
        depth = 1
class UserBatchViewSet(ListAPIView):
    queryset = Batch.objects.all()
    serializer_class = UserBatchSerializer

    def get(self, request, *args, **kwargs):
        batches = self.request.user.student.batches.all()
        self.queryset = batches.filter(Q(end_date=None) | Q(end_date__gte=date.today()))
        return super().get(request, *args, **kwargs)