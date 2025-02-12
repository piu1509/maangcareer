# from django.shortcuts import render
from django.db.models import Q
from rest_framework.viewsets import ViewSet
from rest_framework.generics import ListAPIView
from knox.auth import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Course, Week, TimeTable, Batch, Note ,BatchJoined
from testsManagement.models import *
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import date 
from django.db.models import F
from django.shortcuts import redirect
from rest_framework.views import APIView
import razorpay, uuid
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


####
class WeekSerializer(ModelSerializer):
    class Meta:
        model = Week
        fields = (
            "name",
            "lock",
            "lessons"
        )
        depth = 1

class InstamentDetailsSerializer(ModelSerializer):
    class Meta:
        model = InstamentDetails
        fields = (
            "emi_type",
            "instalment",
            "amount"
        )
        depth = 0

class EmiDetailsSerializer(ModelSerializer):
    emi_variation = InstamentDetailsSerializer(many=True, read_only=True)
    class Meta:
        model = EmiDetails
        fields = (
            "emi_type",
            "instament_number",
            "total_payment",
            "emi_variation"
        )
        depth = 0

class CourseAdvantageSerializer(ModelSerializer):
    class Meta:
        model = CourseAdvantage
        fields = ("point",)
        depth = 1
        
    def to_representation(self, instance):
        return instance.point
    
class CourseIncludeSerializer(ModelSerializer):
    class Meta:
        model = CourseInclude
        fields = ("include",)
        depth = 1
        
    def to_representation(self, instance):
        return instance.include
    
class CourseIncludeTopicSerializer(ModelSerializer):
    class Meta:
        model = CourseIncludeTopic
        fields = ("topic",)
        depth = 1
        
    def to_representation(self, instance):
        return instance.topic

class CourseCaptionSerializer(ModelSerializer):
    class Meta:
        model = CourseCaption
        fields = ("caption",)
        depth = 1
        
    def to_representation(self, instance):
        return instance.caption
    
class CourseSerializer(ModelSerializer):
    syllabi = WeekSerializer(many=True, read_only=True)
    advantages = CourseAdvantageSerializer(many=True, read_only=True)
    includes = CourseIncludeSerializer(many=True, read_only=True)
    course_topics = CourseIncludeTopicSerializer(many=True, read_only=True)
    course_caption = CourseCaptionSerializer(many=True, read_only=True)
    emi_details = EmiDetailsSerializer(many=True, read_only=True)
    is_registered = SerializerMethodField()
    full_payment_status = SerializerMethodField()
    next_instalment_number = SerializerMethodField()
    

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
            "course_duration_in_months",
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
            "advantages",
            "includes",
            "course_topics",
            "course_caption",
            "emi_details",
            "eligibility",
            "is_registered",
            "full_payment_status",
            "next_instalment_number",
            "certificate_count",
            "certificate_no"
            
        )

    def get_is_registered(self, obj):
        """Check if the user is enrolled in the course."""
        user = self.context['request'].user
        if user.is_authenticated:
            return BatchJoined.objects.filter(student__user=user, batch__course=obj).exists()
        return False

    def get_full_payment_status(self, obj):
        """Check if the user has completed full payment."""
        user = self.context['request'].user
        if user.is_authenticated:
            batch_joined = BatchJoined.objects.filter(student__user=user, batch__course=obj).first()
            return batch_joined.full_payment_status if batch_joined else False
        return False

    def get_next_instalment_number(self, obj):
        """Get the next unpaid installment number for the student."""
        user = self.context['request'].user
        if user.is_authenticated:
            batch_joined = BatchJoined.objects.filter(student__user=user, batch__course=obj).first()
            if batch_joined:
                next_unpaid_instalment = StudentEmi.objects.filter(
                    batch=batch_joined.batch,
                    student=batch_joined.student,
                    payment_status=False
                ).order_by('emi_number').first()
                
                if next_unpaid_instalment:
                    return next_unpaid_instalment.emi_number
        return None


class CourseListSerializer(ModelSerializer): 
    is_registered = SerializerMethodField()
    full_payment_status = SerializerMethodField() 
    next_instalment_number = SerializerMethodField()  
    
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
            "payment_id",
            "eligibility", 
            "is_registered",
            "full_payment_status",
            "next_instalment_number",
            "certificate_count",
            "certificate_no"
            
        )
    def get_is_registered(self, obj):
        """Check if the user is enrolled in the course."""
        user = self.context['request'].user
        if user.is_authenticated:
            return BatchJoined.objects.filter(student__user=user, batch__course=obj).exists()
        return False

    def get_full_payment_status(self, obj):
        """Check if the user has completed full payment."""
        user = self.context['request'].user
        if user.is_authenticated:
            batch_joined = BatchJoined.objects.filter(student__user=user, batch__course=obj).first()
            return batch_joined.full_payment_status if batch_joined else False
        return False
    
    def get_next_instalment_number(self, obj):
        """Get the next unpaid installment number for the student."""
        user = self.context['request'].user
        if user.is_authenticated:
            batch_joined = BatchJoined.objects.filter(student__user=user, batch__course=obj).first()
            if batch_joined:
                next_unpaid_instalment = StudentEmi.objects.filter(
                    batch=batch_joined.batch,
                    student=batch_joined.student,
                    payment_status=False
                ).order_by('emi_number').first()
                
                if next_unpaid_instalment:
                    return next_unpaid_instalment.emi_number
        return None

class CourseViewSet(ViewSet):
    """
    A simple ViewSet for listing Courses.
    """
    def list(self, request):
        queryset = Course.objects.filter(archive=False)
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        queryset = Course.objects.all()
        course = get_object_or_404(queryset, pk=pk)
        serializer = CourseSerializer(course, context={'request': request})
        return Response(serializer.data)


class CourseSerializer_(ModelSerializer):
    includes = CourseIncludeSerializer(many=True, read_only=True)
    course_topics = CourseIncludeTopicSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = [
            'id','name', 'caption', 'price', 'discount_percentage', 'archive',
            'popular', 'premium', 'pre_recorded', 'lectures', 'class_duration',
            'course_duration', 'projects', 'mobile_computer', 'certificate',
            'short_description', 'requirements', 'author_name', 'course_duration_in_months',
            'author_message', 'author_photo', 'thumbnail', 'demo_video', 'includes', 
            'course_topics','eligibility', 'certificate_count', 'certificate_no'
        ]

class CourseTopicSerializer(ModelSerializer):
    courses = CourseSerializer_(many=True, read_only=True, source='course')

    class Meta:
        model = CourseTopic
        fields = ['name', 'courses']

class CourseTopicListView(ListAPIView):
    queryset = CourseTopic.objects.all()
    serializer_class = CourseTopicSerializer

#####        

class TimeTableSerializer(ModelSerializer):
    class Meta:
        model = TimeTable
        fields = '__all__'

class TimeTableViewSet(ListAPIView):
    queryset = TimeTable.objects.filter(Q(start_date__lte=date.today()))
    serializer_class = TimeTableSerializer

class UserCourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('id','name')

class UserBatchSerializer(ModelSerializer):
    timetable = TimeTableSerializer(many=True)
    course = UserCourseSerializer()
    this_course_access = SerializerMethodField()
    class Meta:
        model = Batch
        fields = (
            'id',
            'name',
            'course',
            'start_date',
            'end_date',
            # 'instructor',
            'timetable',
            'this_course_access'
        )
        depth = 1

    def get_this_course_access(self, obj):
        """Check if the user still has access based on the revoke date."""
        if obj.revoke_date:
            return date.today() <= obj.revoke_date
        return True

class UserBatchViewSet(ListAPIView):
    queryset = Batch.objects.all()
    serializer_class = UserBatchSerializer

    def get(self, request, *args, **kwargs):
        batches = self.request.user.student.batches.all()
        self.queryset = batches.filter(Q(revoke_date=None) | Q(revoke_date__gte=date.today()))
        return super().get(request, *args, **kwargs)
    
class PaymentViewSet(ViewSet):
    def create(self, request):
        course_id = request.data['course_id']
        batch = Course.objects.get(id=course_id).batches.filter(start_date__gte=date.today()).order_by('start_date')
        for b in batch:
            if b.students.count() < b.max_participants:
                batch = b
                break
        else:batch = Batch.objects.create(course = Course.objects.get(id=course_id))
        # if not batch or batch.students.count() >= batch.max_participants:batch = Batch.objects.create(course = Course.objects.get(id=course_id))
        batch.students.add(request.user.student)
        batch.joined.filter(student=request.user.student).update(payment_id=request.data['payment_id'])
        return Response({'message':'Payment Successful'})
        
class NoteListSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = (
            "topic",
            # "course",
            "week",
            "file"
        )

class NoteViewSet(ListAPIView):
    """
    A simple ViewSet for listing Notes.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication,]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course',]
    queryset = Note.objects.all()
    serializer_class = NoteListSerializer
    pagination_class = None

class InstructorSerializer(ModelSerializer):
    name = SerializerMethodField()
    class Meta:
        model = Instructor
        fields = (
            "name",
            "signature"
        )
    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}' if obj.user.first_name else obj.user.username

class CertificateListSerializer(ModelSerializer):
    course_name = SerializerMethodField()
    instructor = InstructorSerializer()
    certificate_count = SerializerMethodField()
    certificate_no = SerializerMethodField()

    class Meta:
        model = Batch
        fields = (
            "id",
            "course_name",
            "start_date",
            "end_date",
            "instructor",
            "certificate_count",
            "certificate_no"
        )
    def get_course_name(self,obj) -> str:return obj.course.name

    def get_certificate_count(self, obj):
        return obj.course.certificate_count
    
    def get_certificate_no(self, obj):
        return obj.course.certificate_no

class CertificateViewSet(ListAPIView):
    """
    A simple ViewSet for listing Certificates.
    """

    authentication_classes = [TokenAuthentication,]
    serializer_class = CertificateListSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = self.request.user.student.batches.filter(completed=True)
        return queryset

#29/12/2023
class StudentClassTimeTableViewSet(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
   
    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            course_ids = [i["batch__course_id"] for i in get_batch]
            all_times = TimeTable.objects.filter(batch__course_id__in=course_ids, batch_id__in=batch_ids).values(
                "batch__course__name", "start_date", "week"
            ).order_by("batch__course__name", "week", "start_date")
            result_data = {}
            for entry in all_times:
                date_key = entry["start_date"]
                course_name = entry["batch__course__name"]
                if date_key in result_data:
                    result_data[date_key]["course_names"].append(course_name)
                else:
                    result_data[date_key] = {
                        "date": entry["start_date"],
                        "course_names": [course_name],
                        "week": entry["week"],
                    }
            result_list = list(result_data.values())
            return Response({"message": 1, "all_data": result_list}, status=status.HTTP_200_OK)
        except:
            return Response({"message": 0}, status=status.HTTP_400_BAD_REQUEST)

#05/01/2024      
class StudentClassesRoutineViewSet(ListAPIView): # code update
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            course_ids = [i["batch__course_id"] for i in get_batch]
            all_times_week = TimeTable.objects.filter(
                batch__course_id__in=course_ids,
                batch_id__in=batch_ids 
            ).values(
                "id",
                "batch__course__name",
                "batch__course__id",
                "topic",
                "start_date",
                "start_time",
                "week",
                "day",
                "link"
            ).order_by("week", "start_date", F("start_time"),F("week").asc(nulls_last=True))

            if not all_times_week:
                return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
            grouped_data = {}
            for entry in all_times_week:
                date = entry["start_date"]
                if date not in grouped_data:
                    grouped_data[date] = []
                day_topic_list =Topic.objects.filter(week__course = entry["batch__course__id"],week__week=entry["week"],day = entry["day"]).values("name")
                if len(day_topic_list) != 0:
                    day_topic = day_topic_list[0]["name"]
                else:
                    day_topic = None
                entry_info = {
                    "id":entry["id"],
                    "batch__course__name": entry["batch__course__name"],
                    "topic": entry["topic"],
                    "start_time": entry["start_time"],
                    "week": entry["week"],
                    "day": entry["day"],
                    "day_topic": day_topic,
                    "link": entry["link"],
                }
                grouped_data[date].append(entry_info)
            # Sort courses within each date by start_time
            for courses in grouped_data.values():
                courses.sort(key=lambda x: x["start_time"])
            result = [{"date": date, "courses": courses} for date, courses in grouped_data.items()]
            return Response({"message": 1, "week_data": result}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"}) 

class StudentProjectAssign(ListAPIView):
    def get_queryset(self):
        return BatchJoined.objects.all()
    
    def get(self, request, b_id):
        try:
            if b_id == 0:
                return redirect('../../admin/courseManagement/batch/')
            
            batch_id = b_id
            batch = Batch.objects.prefetch_related('project_topics__project_name').get(id=batch_id)
            students_in_batch = BatchJoined.objects.filter(batch=batch)
            
            # Get all topics and projects in the batch
            project_topics = list(batch.project_topics.all())
            
            # For each topic, get associated projects
            topic_project_map = {}
            for topic in project_topics:
                topic_project_map[topic] = list(topic.project_name.all())

            # Assign projects to students in a round-robin fashion per topic
            for join in students_in_batch:
                assigned_projects = []
                for topic in project_topics:
                    projects = topic_project_map[topic]
                    if projects:
                        # Assign one project from the list of projects for this topic
                        project = projects.pop(0)
                        if join.assign_projects != projects:
                            assigned_projects.append(project)
                        # Append the project back to the end of the list for round-robin
                        projects.append(project)
    
                # Assign the collected projects to the student
                join.assign_projects.set(assigned_projects)
                join.assign_topics.set(project_topics)
                join.save()
                
            return redirect(f'../../admin/courseManagement/batch/{b_id}')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

####################
#######RijuDjango #task13
class InstamentDetailsSerializer(ModelSerializer):
    class Meta:
        model = InstamentDetails
        fields = ['id','instalment','payment_id', 'amount']

class EmiDetailsSerializer(ModelSerializer):
    emi_variation = InstamentDetailsSerializer(many=True)

    class Meta:
        model = EmiDetails
        fields = ['id','emi_type', 'instament_number', 'total_payment', 'course', 'emi_variation']

class CourseEmiDetailsListView(ListAPIView):
    serializer_class = EmiDetailsSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return EmiDetails.objects.filter(course_id=course_id)
    
class EmiDetailsView(APIView):
    serializer_class = EmiDetailsSerializer

    def get(self, request):
        emi_id = request.GET.get('emi_id')
        check_emi = EmiDetails.objects.get(id=emi_id)
        serializer = self.serializer_class(check_emi)
        return Response(serializer.data)
    
class InstamentPaymentSerializer(ModelSerializer):
    is_paid = SerializerMethodField()

    class Meta:
        model = InstamentDetails
        fields = ['id','instalment','payment_id', 'amount', 'is_paid']

    def get_is_paid(self, obj):
        request = self.context.get('request')
        user = request.user
        student = Student.objects.filter(user=user).first()

        # Check if there's a payment record for this installment
        if student:
            batch = Batch.objects.filter(course=obj.emi_type.course, students=student).first()
            if batch:
                payment_record = StudentEmi.objects.filter(
                    batch=batch,
                    student=student,
                    emi_number=obj.instalment
                ).first()
                return payment_record is not None

        return False
    
class EmiPaymentSerializer(ModelSerializer):
    emi_variation = InstamentPaymentSerializer(many=True)
    full_payment_status = SerializerMethodField()

    class Meta:
        model = EmiDetails
        fields = ['id', 'emi_type', 'instament_number', 'total_payment', 'course', 'emi_variation', 'full_payment_status']

    def get_full_payment_status(self, obj):
        request = self.context.get('request')
        user = request.user
        student = Student.objects.filter(user=user).first()

        if student:
            # Get the batch related to the course and student
            batch = Batch.objects.filter(course=obj.course, students=student).last()
            if batch:
                batch_joined = BatchJoined.objects.filter(student=student, batch=batch).first()
                if batch_joined:
                    return batch_joined.full_payment_status
        
        return False


from datetime import datetime, timedelta
class UpcomingDatesView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = {'status': '', 'data': [], 'message': ''}
        course_id = request.GET.get('course_id')
        check_course = Course.objects.filter(id=course_id)
        
        if check_course.exists():
            course = check_course.first()
            today = datetime.today()
            last_batch = Batch.objects.filter(course=course, start_date__lt=today).order_by('-start_date').first()

            if last_batch and last_batch.start_date:
                last_batch_day = last_batch.start_date.weekday() 
            else:
                last_batch_day = 1 

            if last_batch_day == 0:  
                start_day = 1  
            else:  
                start_day = 0  
            
            days_of_week = {0: 0, 1: 1} 

            if today.weekday() == start_day:
                current_day = today + timedelta(days=7)
            else:
                days_until_next_start_day = (start_day - today.weekday() + 7) % 7
                current_day = today + timedelta(days=days_until_next_start_day)

            dates = []
            for _ in range(5):
                dates.append(current_day.strftime('%Y-%m-%d'))
                current_day += timedelta(days=7)
                
                if current_day.weekday() == 0: 
                    current_day += timedelta(days=1) 
                else:  
                    current_day -= timedelta(days=1)  

            data['status'] = status.HTTP_200_OK
            data['data'] = dates
            data['message'] = 'Dates fetched successfully.'
        else:
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['message'] = 'Course not found.'

        return Response(data)


class StudentInstallmentPayment(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        course_id = request.GET.get('course_id')
        check_student = Student.objects.filter(user=user)
        check_course = Course.objects.filter(id=course_id)
        if check_student and check_course:
            get_student = check_student.first()
            course = check_course.first()
            batch = Batch.objects.filter(course=course, students=get_student).last()
            check_batch_joined = BatchJoined.objects.filter(student=get_student, batch=batch)
            if check_batch_joined:
                batch_emi = check_batch_joined.last().choice_emi_type
                serializer = EmiPaymentSerializer(batch_emi, context={'request': request})
                return Response({'status':status.HTTP_200_OK, 'data': serializer.data, 'message':'Data fetched successfully'})
            else:
                return Response({'status':status.HTTP_200_OK, 'data': [], 'message':'No batch joined available.'})
        else:
            return Response({'status':status.HTTP_200_OK, 'data': [], 'message':'Student or Course not found'})
        
    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')
        payment_mode = request.data.get('payment_mode')
        payment_id = request.data.get('payment_id')
        payment_status = request.data.get('payment_status')
        payment_url = request.data.get('payment_url')
        json_response = request.data.get('json_response')
        emi_number = request.data.get('emi_number')
        razorpay_order_id = request.data.get('razorpay_order_id')

        if json_response:
            response = json.loads(json_response)
        else:
            response = None
        if payment_url:
            url = payment_url
        else:
            url = None
        check_student = Student.objects.filter(user=user)
        check_course = Course.objects.filter(id=course_id)
        if check_student and check_course:
            get_student = check_student.first()
            course = check_course.first()
            batch = Batch.objects.filter(course=course, students__id=get_student.id).last()
            
            # Check if the payment for this EMI has already been made
            emi_paid = StudentEmi.objects.filter(batch=batch, student=get_student, emi_number=emi_number, payment_status=True).exists()
            if emi_paid:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Payment for this EMI has already been made.'})

            payment_create = StudentEmi.objects.create(
                batch=batch,
                student=get_student,
                amount=amount,
                emi_number=int(emi_number),
                payment_mode=payment_mode,
                payment_id=payment_id,
                payment_status=payment_status,
                payment_url=url,
                json_response=response, 
                razorpay_order_id=razorpay_order_id
            )
            return Response({'status':status.HTTP_200_OK, 'message':'Payment Successful.'})
        else:
            return Response({'status':status.HTTP_200_OK, 'message':'Student or Course not found'})


class EnrollStudentToBatch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = {'status': '', 'message': ''}
        user = request.user
        course_id = request.data.get('course_id')
        chosen_date = request.data.get('chosen_date')
        emi_id = request.data.get('emi_id')

        check_student = Student.objects.filter(user=user)
        check_course = Course.objects.filter(id=course_id)
        
        if check_student and check_course:
            get_student = check_student.first()
            course = check_course.first()

            # Check if the student is already enrolled in any batch of this course
            ongoing_enrollment = BatchJoined.objects.filter(
                student=get_student, 
                batch__course=course, 
                batch__revoke_date__gte=datetime.now()
            ).exists()

            if ongoing_enrollment:
                data['message'] = f'You are already enrolled in an ongoing batch for {course.name}. You cannot enroll in a new batch until the current one ends.'
                data['status'] = status.HTTP_400_BAD_REQUEST
                return Response(data)

            check_batch = Batch.objects.filter(course=course, start_date=chosen_date)
            if check_batch.exists():
                batch = check_batch.first()
                if batch.students.all().count() >= batch.max_participants:
                    data['message'] = 'Batch is full. Choose another date.'
                    data['status'] = status.HTTP_400_BAD_REQUEST
                    return Response(data)
                else:
                    batch.students.add(get_student)
            else:
                batch = Batch.objects.create(course=course, start_date=chosen_date)
                batch.students.add(get_student)

            batch_joined = BatchJoined.objects.filter(student=get_student, batch=batch).first()
            get_emi = EmiDetails.objects.filter(id=int(emi_id)).first()
            batch_joined.choice_emi_type = get_emi
            batch_joined.save()

            data['status'] = status.HTTP_200_OK
            data['batch_id'] = batch.id
            data['batch_joined_id'] = batch_joined.id
            data['message'] = f'You are successfully enrolled in Batch {batch.id} of {course.name}.'
        else:
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['batch_id'] = None
            data['batch_joined_id'] = None
            data['message'] = 'Student or Course not found.'
        
        return Response(data)


class DeleteBatch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user=request.user

        data = {'status': '', 'message':''}
        batch_id = request.data.get('batch_id')
        batch_joined_id = request.data.get('batch_joined_id')
        get_student = Student.objects.filter(user=user).first()
        check_batch = Batch.objects.filter(id=batch_id, students__id=get_student.id)
        check_batch_joined = BatchJoined.objects.filter(id=batch_joined_id, student=get_student)
        if check_batch and check_batch_joined:
            batch = check_batch.first()
            batch_joined = check_batch_joined.first()
            if batch.students.all().count() == 1:
                batch.delete()
                batch_joined.delete()
            else:
                batch_joined.delete()
                batch.students.remove(get_student)
            data['status'] = status.HTTP_200_OK
            data['message'] = 'Batch and Batch Joined deleted successfully.'
        else:
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['message'] = 'Batch not found.'
        return Response(data)

RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET


def generate_receipt_number():
    receipt_number = f"receipt_{uuid.uuid4().hex[:10].upper()}"
    return receipt_number

@method_decorator(csrf_exempt, name='dispatch')
class CreateRazorpayOrder(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    currency_list = ['INR', 'USD', 'EUR', 'GBP', 'AUD', 'CAD', 'JPY', 'CNY', 'NZD', 'SGD', 'MYR', 'HKD', 'AED', 'SAR', 'KWD', 'BHD', 'OMR', 'PKR', 'LKR', 'Taka', 'RMB']


    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        # currency = 'INR'
        currency = request.data.get('currency')
        if currency not in self.currency_list:
            response = {
                    'status': 'failed',
                    'message': 'Currency not accepted.'
                }

            return Response(response)
        receipt = generate_receipt_number()  
        
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        order_data = {
            'amount': int(float(amount)) * 100,  
            'currency': currency,
            'receipt': receipt,
            'payment_capture': 1  # Auto capture
        }

        try:
            order = client.order.create(data=order_data)
            razorpay_order_id = order['id']
            order_status = order['status']

            if order_status == 'created':
                response = {
                    'razorpay_order_id': razorpay_order_id,
                    'amount': amount,
                    'currency': currency,
                    'status': 'success',
                    'message': 'Order created successfully'
                }
            else:
                response = {
                    'status': 'failed',
                    'message': 'Order creation failed'
                }

            return Response(response)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            })
