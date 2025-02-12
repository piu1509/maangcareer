from django.contrib.auth import login
from django.contrib.auth.models import User
from userManagement.models import *
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework.serializers import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from knox.views import LoginView as KnoxLoginView
from django_otp.oath import TOTP
from django.core.mail import send_mail
from django_otp.plugins.otp_totp.models import TOTPDevice
import hashlib
from rest_framework.response import Response
from django.contrib.auth import authenticate
from knox.models import AuthToken
import time
from knox.auth import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from courseManagement.models import *
from testsManagement.models import *
from freeCourseManagement.models import *
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from courseManagement.helpers import send_mail_for_otp, send_mail_for_welcome, send_mail_for_reset_password
from rest_framework.exceptions import APIException
from django.db.models import Q
from .serializers import *
from collections import defaultdict
from dateutil import parser
from django.db.models import Max, FloatField, OuterRef, Subquery, Count


class GeneratingOTP:
    def __init__(self, email, extra_key, user=None):
        if not user:
            user = User.objects.get(email__iexact=email)
        self.user = user
        hex_email = self.generate_hex(
            self.user.email or self.user.phone_number.as_e164, 20
        )
        hex_extra_key = self.generate_hex(extra_key, 20)
        self.key = f"{hex_email}{hex_extra_key}"
        self.number_of_digits = 6
        # validity period of a token. Default is 30 second.
        self.token_validity_period = 3 * 60

    @staticmethod
    def generate_hex(value, length):
        sha256_hash = hashlib.sha256(value.encode()).hexdigest()
        hex_string = sha256_hash[:length]
        return hex_string

    def totp_device(self):
        totp_device, created = TOTPDevice.objects.update_or_create(
            key=self.key,
            user=self.user,
            defaults={
                "step": self.token_validity_period,
                "digits": self.number_of_digits,
                "tolerance": 0,
            },
        )
        return totp_device

    def totp_obj(self):
        totp_device = self.totp_device()
        # create a TOTP object
        totp = TOTP(
            key=totp_device.bin_key,
            step=totp_device.step,
            t0=totp_device.t0,
            digits=totp_device.digits,
            drift=totp_device.drift,
        )
        return totp

    def generate_otp(self):
        # get the TOTP object and use that to create token
        totp = self.totp_obj()
        token = totp.token()
        return str(token).zfill(self.number_of_digits)

    def verify_otp(self, token):
        # verify otp using totp device
        totp_device = self.totp_device()
        is_verified = totp_device.verify_token(token)
        if is_verified:
            totp_device.delete()
        return is_verified


def generate_otp_for_mail(
        email: str,
        extra_key: str,
) -> bool:
    """Generate OTP for Phone Number"""
    generate_otp_service = GeneratingOTP(email, extra_key)

    return generate_otp_service.generate_otp()


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A validation error occurred.'
    default_code = 'invalid'

    def __init__(self, detail, code=None):
        self.detail = detail
        self.code = code


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CustomValidationError({"status": "400", "message": "User Does not exist"})
        
        if not user.check_password(password):
            raise CustomValidationError({"status": "400", "message": "Incorrect Credentials"})
        
        if not user.is_active:
            otp = generate_otp_for_mail(user.email, "login")
            send_mail_for_otp(user.email, otp)
            raise CustomValidationError({"status": "400", "message": "User Not Verified"})
        
        otp = generate_otp_for_mail(user.email, "login")
        send_mail_for_otp(user.email, otp)

        sub_admin = SubAdmin.objects.filter(user=user).first()
        if sub_admin:
            sub_admin.otp = otp
            sub_admin.otp_validation_time = timezone.now() + timedelta(minutes=5)
            sub_admin.save()
        
        return {
            "username": username,
            "otp_sent": True,
            "message": "OTP sent successfully."
        }


class SubAdminOTPVerificationView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def post(self, request):
        otp = request.data.get('otp')
        username = request.data.get('username')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})
        
        sub_admin = SubAdmin.objects.filter(user=user).first()
        if sub_admin:
            if sub_admin.otp == int(otp) and sub_admin.otp_validation_time >= timezone.now():
                # OTP is valid, generate token
                login(request, user)
                return super().post(request)
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP or OTP expired."})
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User is not Sub Admin."})
               

class SubAdminLoginView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        
        username = request.data.get('username')
        password = request.data.get('password')        
       
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Return response indicating OTP has been sent
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OTP sent to your email.",
            "otp_sent": validated_data.get("otp_sent")
        })


class SubAdminResendOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})

        if not user.is_active:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User is not verified."})
       
        otp = generate_otp_for_mail(user.email, "login")
        send_mail_for_otp(user.email, otp)

        sub_admin = SubAdmin.objects.filter(user=user).first()
        if sub_admin:
            sub_admin.otp = otp
            sub_admin.otp_validation_time = timezone.now() + timedelta(minutes=5)
            sub_admin.save()

            return Response({
                "status": status.HTTP_200_OK,
                "message": "OTP has been resent successfully."
            })
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "User is not a Sub Admin."
            })


class PaidCourseList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Course.objects.filter(archive=False)
        serializer = CustomCourseSerializer(queryset, many=True)
        return Response(serializer.data)


class PaidBatchList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        course_id = request.GET.get('course_id', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)  
        completed = request.GET.get('completed', None)  
        page = request.GET.get('page', 1)  
        page_size = request.GET.get('page_size', 5)

        try:
            page_size = int(page_size)
            if page_size <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({"message": "Invalid page size. It must be a positive integer.", "status": status.HTTP_400_BAD_REQUEST})

        queryset = Batch.objects.filter(course__archive=False)

        if course_id:
            queryset = queryset.filter(course_id=int(course_id))

        if start_date and not end_date:
            try:
                start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date=start_date_parsed)
            except ValueError:
                return Response({"message": "Invalid start date format. Use YYYY-MM-DD.", "status": status.HTTP_400_BAD_REQUEST})

        if start_date and end_date:
            try:
                start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__range=[start_date_parsed, end_date_parsed])
            except ValueError:
                return Response({"message": "Invalid date range format. Use YYYY-MM-DD.", "status": status.HTTP_400_BAD_REQUEST})

        if completed is not None:
            if completed.lower() in ['true', 'false']:
                queryset = queryset.filter(completed=completed.lower() == 'true')
            else:
                return Response({"message": "Invalid value for 'completed' filter. Use 'true' or 'false'.", "status": status.HTTP_400_BAD_REQUEST})

        queryset = queryset.order_by('-id')

        paginator = PageNumberPagination()
        paginator.page_size = page_size  
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = CustomBatchSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)


class InstructorList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        instructors = Instructor.objects.all()
        serializer = InstructorSerializer(instructors, many=True)
        return Response(serializer.data)


class ProjectList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        projects = ProjectTopic.objects.all()
        serializer = ProjectTopicSerializer(projects, many=True)
        return Response(serializer.data)


class AddBatch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        course_id = request.data.get('course_id')
        project_ids = request.data.getlist('project_ids')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        revoke_date = request.data.get('revoke_date')
        max_participants = request.data.get('max_perticipants')
        url_link = request.data.get('url_link')
        instructor_id = request.data.get('instructor_id')

        if not course_id:
            return Response({'message': 'Course ID is required.', 'status':status.HTTP_400_BAD_REQUEST})       
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'message': 'Course not found.', 'status':status.HTTP_404_NOT_FOUND})
        
        instructor = None
        if instructor_id:
            try:
                instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                return Response({'message': 'Instructor not found.', 'status':status.HTTP_404_NOT_FOUND})
        
        revoke_days = None
        if end_date and revoke_date:
            try:                
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                revoke_date_dt = datetime.strptime(revoke_date, '%Y-%m-%d').date()
                
                if revoke_date_dt >= end_date_dt:
                    revoke_days = (revoke_date_dt - end_date_dt).days
                else:
                    return Response({'message': 'Revoke date must be after or on the end date.', 'status':status.HTTP_400_BAD_REQUEST})

            except ValueError:
                return Response({'message': 'Invalid date format. Use YYYY-MM-DD.', 'status':status.HTTP_400_BAD_REQUEST})
       
        batch = Batch.objects.create(
            course=course,
            start_date=start_date,
            end_date=end_date,
            revoke_date=revoke_date,
            max_participants=max_participants if max_participants else 30,  
            link=url_link,
            instructor=instructor,
            revoke_days=revoke_days 
        )
        for project_id in project_ids:
            project_topic = ProjectTopic.objects.filter(id=project_id).first()
            if project_topic:
                batch.project_topics.add(project_topic)

        return Response({'message': 'Batch created successfully.', 'batch_id': batch.id, 'status':status.HTTP_200_OK})


class PreviewAddBatch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        
        course_id = request.data.get('course_id')
        project_ids = request.data.getlist('project_ids') 
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        revoke_date = request.data.get('revoke_date')
        max_participants = request.data.get('max_participants')
        url_link = request.data.get('url_link')
        instructor_id = request.data.get('instructor_id')

        if not course_id:
            return Response({'message': 'Course ID is required.', 'status':status.HTTP_400_BAD_REQUEST})

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'message': 'Course not found.', 'status':status.HTTP_404_NOT_FOUND})

        instructor = None
        if instructor_id:
            try:
                instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                return Response({'message': 'Instructor not found.', 'status':status.HTTP_404_NOT_FOUND})

        project_topics = ProjectTopic.objects.filter(id__in=project_ids)
        if len(project_topics) != len(project_ids):
            return Response({'message': 'One or more project topics not found.', 'status':status.HTTP_404_NOT_FOUND})

        revoke_days = None
        if end_date and revoke_date:
            try:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                revoke_date_dt = datetime.strptime(revoke_date, '%Y-%m-%d').date()

                if revoke_date_dt >= end_date_dt:
                    revoke_days = (revoke_date_dt - end_date_dt).days
                else:
                    return Response({'message': 'Revoke date must be after or on the end date.', 'status':status.HTTP_400_BAD_REQUEST})
            except ValueError:
                return Response({'message': 'Invalid date format. Use YYYY-MM-DD.', 'status':status.HTTP_400_BAD_REQUEST})

        batch_preview = {
            'course_name': course.name,
            'project_topics': [project.project_topic for project in project_topics],
            'start_date': start_date,
            'end_date': end_date,
            'revoke_date': revoke_date,
            'max_participants': max_participants if max_participants else 30, 
            'link': url_link,
            'instructor_name': instructor.id,
            'revoke_days': revoke_days  
        }

        return Response({
            'message': 'Preview of the batch data:',
            'batch_preview': batch_preview,
            'status':status.HTTP_200_OK})


class BatchDetailsView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        batch_id = request.GET.get('batch_id')        
        batch = Batch.objects.filter(id=batch_id).first()
        serializer = BatchDetailsSerializer(batch)
        return Response(serializer.data)


class BatchTimeTableList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        batch_id = request.GET.get('batch_id')
        search_name = request.GET.get('search_name', '')
        page = request.GET.get('page', 1)  
        page_size = request.GET.get('page_size', 5) 
        batch = Batch.objects.filter(id=batch_id).first()
        time_tables = TimeTable.objects.filter(batch=batch)
        if search_name:
            filters = (
                Q(topic__icontains=search_name) |
                Q(start_date__icontains=search_name) |
                Q(start_time__icontains=search_name) |
                Q(end_time__icontains=search_name)
            )
            time_tables = time_tables.filter(filters) 
        time_tables = time_tables.order_by('-id')       
        paginator = PageNumberPagination()
        paginator.page_size = page_size  
        paginated_queryset = paginator.paginate_queryset(time_tables, request)
        serializer = TimeTableSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)


class BatchStudentList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        batch_id = request.GET.get('batch_id')
        page = request.GET.get('page', 1)  
        page_size = request.GET.get('page_size', 5) 
        search_name = request.GET.get('search_name', '') 
        batch = Batch.objects.filter(id=batch_id).first()
        batch_joined_list = BatchJoined.objects.filter(batch=batch)
        if search_name:
            batch_joined_list = batch_joined_list.filter(
                Q(student__user__username__icontains=search_name) |
                Q(student__user__first_name__icontains=search_name) |
                Q(student__user__last_name__icontains=search_name) |
                Q(batch__id__icontains=search_name)
            )
        batch_joined_list = batch_joined_list.order_by('-id')
        paginator = PageNumberPagination()
        paginator.page_size = page_size  
        paginated_queryset = paginator.paginate_queryset(batch_joined_list, request)
        serializer = BatchJoinedSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)


class AddClass(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        batch_id = request.data.get('batch_id')
        topic = request.data.get('topic')
        start_date = request.data.get('start_date')
        week = request.data.get('week')
        day = request.data.get('day')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        link = request.data.get('link')

        batch = get_object_or_404(Batch, id=batch_id)
        
        timetable = TimeTable.objects.create(
            batch=batch,
            topic=topic,
            start_date=start_date,
            week=week,
            day=day,
            start_time=start_time,
            end_time=end_time,
            link=link
        )

        return Response({"message": "Class added successfully", "timetable_id": timetable.id, "status":status.HTTP_201_CREATED})


class UpdateBatch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        batch_id = request.data.get('batch_id')
        batch = get_object_or_404(Batch, id=batch_id)
        course_id = request.data.get('course_id')
        project_ids = request.data.getlist('project_ids', [])  # Default to empty list
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        max_participants = request.data.get('max_participants')
        url_link = request.data.get('url_link')
        instructor_id = request.data.get('instructor_id')
        completed_status = request.data.get('completed_status')
        certificate_status = request.data.get('certificate_status')

        if course_id:
            course = Course.objects.filter(id=int(course_id)).first()
            if course:
                batch.course = course

        if start_date:
            batch.start_date = start_date

        if end_date:
            batch.end_date = end_date

        if max_participants:
            batch.max_participants = max_participants

        if url_link:
            batch.link = url_link

        if instructor_id:
            try:
                instructor = Instructor.objects.get(id=instructor_id)
                batch.instructor = instructor
            except Instructor.DoesNotExist:
                return Response({'message': 'Instructor not found.', 'status': status.HTTP_404_NOT_FOUND})
  
        if completed_status is not None:
            batch.completed = completed_status
  
        if certificate_status is not None:
            batch.b_certificate = certificate_status

        batch.save()

        if project_ids:
            batch.project_topics.clear()
            for project_id in project_ids:
                project_topic = ProjectTopic.objects.filter(id=project_id).first()
                if project_topic:
                    batch.project_topics.add(project_topic)

        return Response({'message': 'Batch updated successfully.', 'status': status.HTTP_200_OK})


class ClassDetails(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print("000000")
        time_table_id = request.GET.get('time_table_id')
        _class = get_object_or_404(TimeTable, id=time_table_id)
        print(_class)
        serializer = TimeTableSerializer(_class)
        return Response(serializer.data)


class UpdateClass(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        time_table_id = request.data.get('time_table_id')
        
        _class = get_object_or_404(TimeTable, id=time_table_id)

        topic = request.data.get('topic')
        if topic:
            _class.topic = topic

        start_date = request.data.get('start_date')
        if start_date:
            _class.start_date = start_date

        week = request.data.get('week')
        if week:
            _class.week = week

        day = request.data.get('day')
        if day:
            _class.day = day

        start_time = request.data.get('start_time')
        if start_time:
            _class.start_time = start_time

        end_time = request.data.get('end_time')
        if end_time:
            _class.end_time = end_time

        link = request.data.get('link')
        if link:
            _class.link = link

        _class.save()

        return Response({'message': 'Class updated successfully.', 'status': status.HTTP_200_OK})


class DeleteBatch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        batch_id = request.data.get('batch_id')

        batch = get_object_or_404(Batch, id=batch_id)
        students = batch.students.all()
        if len(students) > 0 and batch.completed == False:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "message":"This batch has students enrolled and is not completed yet."})
        batch.delete()
        return Response({"status":status.HTTP_200_OK, "message":"Batch is deleted successfully."})


class DeleteClass(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        time_table_id = request.data.get('time_table_id')
        time_table = get_object_or_404(TimeTable, id=time_table_id)

        time_table.delete()
        return Response({"status":status.HTTP_200_OK, "message":"Class is deleted successfully."})


class BatchStudentDelete(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)     

    def post(self, request):
        batch_joined_id = request.data.get('batch_joined_id') 
        check_batch_joined = BatchJoined.objects.filter(id=batch_joined_id)
        if check_batch_joined:
            batch_joined = check_batch_joined.first()
            batch = batch_joined.batch
            student = batch_joined.student
            batch.students.remove(student)
            batch_joined.delete()
            return Response({"status":status.HTTP_200_OK, "message":" The Student is successfully removed from the batch."})
        else:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "message":"Batch joined object not found.."})


class StudentList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        page = request.GET.get('page', 1)  
        page_size = request.GET.get('page_size', 5) 
        joining_date = request.GET.get('joining_date')  
        start_date = request.GET.get('start_date')  
        end_date = request.GET.get('end_date')  
        current_enrollment_status = request.GET.get('current_enrollment_status')

        queryset = Student.objects.all()

        if joining_date:
            try:
                joining_date_parsed = datetime.strptime(joining_date, '%Y-%m-%d')
                queryset = queryset.filter(joined_date=joining_date_parsed)
            except ValueError:
                return Response({'message': 'Invalid date format. Use YYYY-MM-DD.', "status": status.HTTP_400_BAD_REQUEST})

        if start_date and end_date:
            try:
                start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(joined_date__range=[start_date_parsed, end_date_parsed])
            except ValueError:
                return Response({'message': 'Invalid date range format. Use YYYY-MM-DD.', "status": status.HTTP_400_BAD_REQUEST})

        if current_enrollment_status is not None:
            if current_enrollment_status.lower() == 'true':
                queryset = queryset.filter(batches__completed=False).distinct()
            elif current_enrollment_status.lower() == 'false':
                queryset = queryset.filter(~Q(batches__completed=False)).distinct()

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = StudentSerializer(paginated_queryset, many=True)

        if joining_date:
            total_students = Student.objects.filter(joined_date=joining_date_parsed).count()
        elif start_date and end_date:
            total_students = Student.objects.filter(joined_date__range=[start_date_parsed, end_date_parsed]).count()
        else:
            total_students = Student.objects.count()

        if start_date and end_date:
            total_batches = Batch.objects.filter(start_date__range=[start_date_parsed, end_date_parsed]).count()
        else:
            total_batches = Batch.objects.count()

        total_courses = Course.objects.count()

        response_data = {
            'students': serializer.data,
            'total_students': total_students,
            'total_batches': total_batches,
            'total_courses': total_courses,
            'page': int(page),
            'page_size': int(page_size),
        }

        return paginator.get_paginated_response(response_data)


class StudentDetails(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')       

        student = Student.objects.filter(id=int(student_id)).first()
        details = StudentDetailsSerializer(student).data

        batch_joined = BatchJoined.objects.filter(student=student).order_by('-id')        
        batch_joined_details = StudentBatchJoinedSerializer(batch_joined, many=True).data

        free_course_joined = FreeCourseJoinee.objects.filter(student=student)
        free_course_details = FreeCourseJoineeSerializer(free_course_joined, many=True).data

        return Response({"details":details, "batch_details":batch_joined_details, "free_course_details":free_course_details})


class StudentPaidQuizProgress(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)

        student = Student.objects.filter(id=int(student_id)).first()

        quiz_attempts = QuizAttempt.objects.filter(student=student).order_by('id')

        week_data = defaultdict(lambda: {
            "score": 0,
            "max_attempt": 0,
            "data": [],
            "course_name": None,
            "max_num_of_attempts": None
        })

        for attempt in quiz_attempts:
            course = attempt.quiz.course.name
            week = attempt.quiz.week
            key = f"{course}_{week}"

            week_data[key]["max_attempt"] = max(week_data[key]["max_attempt"], attempt.attempts)
            week_data[key]["score"] = max(week_data[key]["score"], int(attempt.score) if attempt.score else 0)
            week_data[key]["data"].append(QuizAttemptSerializer(attempt).data)

            question_timer = QuestionTimer.objects.filter(course=attempt.quiz.course, week=week).first()
            if question_timer:
                week_data[key]["course_name"] = question_timer.course.name if question_timer.course else "No Course"
                week_data[key]["max_num_of_attempts"] = question_timer.max_num_of_attempts

        final_response = []
        for key, data in week_data.items():
            course_name, week = key.split('_')
            final_response.append({
                "course_name": course_name,
                "week": int(week),
                "score": data["score"],
                "max_attempt": data["max_attempt"],
                "max_num_of_attempts": data["max_num_of_attempts"],
                "data": data["data"]
            })

        final_response.sort(key=lambda x: x['week'])

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_response = paginator.paginate_queryset(final_response, request)

        return paginator.get_paginated_response(paginated_response)


class StudentPaidMockProgress(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)

        student = Student.objects.filter(id=int(student_id)).first()

        mock_results = MockResult.objects.filter(student=student, question__practice_mock=True).order_by('-id')

        question_timers = QuestionTimer.objects.filter(
            course__in=Course.objects.filter(
                id__in=mock_results.values_list('question__course_id', flat=True)
            )
        )
        week_data = defaultdict(lambda: {
            "max_attempt": 0,
            "course_name": "",
            "data": []
        })
        for result in mock_results:
            week = result.question.week
            attempt = result.attempt
            course_name = result.question.course.name

            key = f"{course_name}_{week}"
            week_entry = week_data[key]

            week_entry["max_attempt"] = max(week_entry["max_attempt"], attempt)
            week_entry["course_name"] = course_name

            week_entry["data"].append({
                "attempts": attempt,
                "score": result.score,
                "passed": result.correct
            })

        final_response = []
        for key, data in week_data.items():
            course_name, week = key.split('_')

            scores_by_attempt = defaultdict(list)
            for entry in data["data"]:
                scores_by_attempt[entry["attempts"]].append(entry["score"])

            attempt_wise_scores = []
            for attempt, scores in scores_by_attempt.items():
                average_score = sum(scores) / len(scores) if scores else 0
                attempt_wise_scores.append({
                    "passed": any(score == 100 for score in scores), 
                    "score": f"{average_score:.3f}",
                    "attempts": attempt
                })

            question_timer = question_timers.filter(course=result.question.course, week=week).first()
            max_attempt = question_timer.max_num_of_attempts if question_timer else None

            final_response.append({
                "week": int(week),
                "score": 100,  
                "total_attempt": data["max_attempt"],
                "max_attempt": max_attempt,
                "course_name": course_name,
                "data": sorted(attempt_wise_scores, key=lambda x: x["attempts"])
            })
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_response = paginator.paginate_queryset(final_response, request)

        return paginator.get_paginated_response(paginated_response)
  

class StudentPaidPracticeProgress(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')
        page_size = request.GET.get('page_size', 5)

        student = Student.objects.filter(id=int(student_id)).first()

        practice_results = CompilerQuestionAtempt.objects.filter(
            student=student, question__practice_mock=False
        ).order_by('-id')

        question_timers = QuestionTimer.objects.filter(
            course__in=Course.objects.filter(
                id__in=practice_results.values_list('question__course_id', flat=True)
            )
        )
        week_data = defaultdict(lambda: {
            "max_attempt": 0,
            "course_name": "",
            "data": []
        })

        for result in practice_results:
            week = result.question.week 
            attempt = result.attepmt_number
            course_name = result.question.course.name

            key = f"{course_name}_{week}"
            week_entry = week_data[key]

            week_entry["max_attempt"] = max(week_entry["max_attempt"], attempt)
            week_entry["course_name"] = course_name

            week_entry["data"].append({
                "attempts": attempt,
                "score": result.score,
                "passed": result.status
            })
        final_response = []
        for key, data in week_data.items():
            course_name, week = key.split('_')

            scores_by_attempt = defaultdict(list)
            for entry in data["data"]:
                scores_by_attempt[entry["attempts"]].append(entry["score"])

            attempt_wise_scores = []
            for attempt, scores in scores_by_attempt.items():
                average_score = sum(scores) / len(scores) if scores else 0
                attempt_wise_scores.append({
                    "passed": any(score == 100 for score in scores),
                    "score": f"{average_score:.3f}",
                    "attempts": attempt
                })

            question_timer = question_timers.filter(course__name=course_name, week=week).first()
            max_attempt = question_timer.max_num_of_attempts if question_timer else None

            final_response.append({
                "week": int(week),
                "score": 100,  
                "total_attempt": data["max_attempt"],
                "max_attempt": max_attempt,
                "course_name": course_name,
                "data": sorted(attempt_wise_scores, key=lambda x: x["attempts"]) 
            })


        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_response = paginator.paginate_queryset(final_response, request)

        return paginator.get_paginated_response(paginated_response)


class StudentFreeQuizProgress(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)

        student = Student.objects.filter(id=int(student_id)).first()

        free_quiz_attempts = QuizQuestionAttempts.objects.filter(student=student).order_by('id')

        syllabus_data = defaultdict(lambda: {
            "max_score": 0,
            "data": [],
            "course_name": None,
            "total_attempts": 0,
            "max_no_of_attempts": None
        })

        for attempt in free_quiz_attempts:
            syllabus = attempt.syllabus
            course_name = attempt.course.name
            key = f"{course_name}_{syllabus.id}"  

            syllabus_data[key]["max_score"] = max(syllabus_data[key]["max_score"], int(attempt.attempt_score) if attempt.attempt_score else 0)
            syllabus_data[key]["data"].append(QuizQuestionAttemptsSerializer(attempt).data)
            syllabus_data[key]["course_name"] = course_name
            syllabus_data[key]["total_attempts"] += 1
            syllabus_data[key]["max_no_of_attempts"] = syllabus.max_attempts

        final_response = []
        for key, data in syllabus_data.items():
            course_name, syllabus_id = key.split('_') 
            final_response.append({
                "syllabus_id": int(syllabus_id),  
                "course_name": course_name,
                "max_score": data["max_score"],
                "total_attempts": data["total_attempts"],
                "max_no_of_attempts": data["max_no_of_attempts"],
                "data": data["data"]
            })

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_response = paginator.paginate_queryset(final_response, request)

        return paginator.get_paginated_response(paginated_response)


class StudentFreePracticeProgress(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')
        page_size = request.GET.get('page_size', 5)

        student = Student.objects.filter(id=int(student_id)).first()

        paginator = PageNumberPagination()
        paginator.page_size = page_size

        free_practice_attempts = FreeCourseCompilerQuestionAttempt.objects.filter(
            student=student, question__practice_mock=False
        ).order_by('-id')

        practice_data = defaultdict(lambda: {
            "max_score": 0,
            "data": [],
            "course_name": None,
            "total_attempts": 0,
        })

        for attempt in free_practice_attempts:
            course_name = attempt.course.name 
            syllabus_id = attempt.syllabus.id  
            key = f"{course_name}_{syllabus_id}" 

            practice_data[key]["max_score"] = max(practice_data[key]["max_score"], int(attempt.score) if attempt.score else 0)
            practice_data[key]["data"].append(FreeCoursePracticeQuestionAttemtSerializer(attempt).data)
            practice_data[key]["course_name"] = course_name
            practice_data[key]["total_attempts"] += 1

        final_response = []
        for key, data in practice_data.items():
            course_name, syllabus_id = key.split('_') 
            final_response.append({
                "syllabus_id": int(syllabus_id),  
                "course_name": course_name,
                "max_score": data["max_score"],
                "total_attempts": data["total_attempts"],
                "data": data["data"]
            })

        paginated_response = paginator.paginate_queryset(final_response, request)

        return paginator.get_paginated_response(paginated_response)


class StudentFreeMockProgress(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        student_id = request.GET.get('student_id')
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)

        student = Student.objects.filter(id=int(student_id)).first()

        free_mock_attempts = MockCompilerQuestionResult.objects.filter(student=student).order_by('id')

        syllabus_data = defaultdict(lambda: {
            "max_score": 0,
            "data": [],
            "course_name": None,
            "total_attempts": 0,
            "max_no_of_attempts": None
        })

        for attempt in free_mock_attempts:
            syllabus = attempt.course_section
            course_name = attempt.course.name
            key = f"{course_name}_{syllabus.id}" 

            syllabus_data[key]["max_score"] = max(syllabus_data[key]["max_score"], int(attempt.score) if attempt.score else 0)
            syllabus_data[key]["data"].append(FreeCourseMockAttemptSerializer(attempt).data)
            syllabus_data[key]["course_name"] = course_name
            syllabus_data[key]["total_attempts"] += 1
            syllabus_data[key]["max_no_of_attempts"] = syllabus.max_attempts_mock

        final_response = []
        for key, data in syllabus_data.items():
            course_name, syllabus_id = key.split('_')
            final_response.append({
                "syllabus_id": int(syllabus_id), 
                "course_name": course_name,
                "max_score": data["max_score"],
                "total_attempts": data["total_attempts"],
                "max_no_of_attempts": data["max_no_of_attempts"],
                "data": data["data"]
            })

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_response = paginator.paginate_queryset(final_response, request)

        return paginator.get_paginated_response(paginated_response)


class UserList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AddOrUpdateStudent(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.data.get('user_id')

        email = request.data.get('email')
        phone_num = request.data.get('phone_num')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        course_id = request.data.get('course_id')
        batch_id = request.data.get('batch_id')

        if not all([email, phone_num, first_name, last_name, course_id, batch_id]):
            return Response({'message': 'Email, phone number, first name, last name, course ID, and batch ID are required.', 'status': status.HTTP_400_BAD_REQUEST})

        if not user_id:        
            username = request.data.get('username')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')

            if not username or not password:
                return Response({'message': 'Username and password are required.', 'status': status.HTTP_400_BAD_REQUEST})

            if password != confirm_password:
                return Response({'message': 'Passwords do not match.', 'status': status.HTTP_400_BAD_REQUEST})

            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        else:
            user = get_object_or_404(User, id=user_id)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        student, created = Student.objects.update_or_create(
            user=user,
            defaults={
                'phone_num': phone_num,
                'profile_img': request.FILES.get('profile_img'),
                'terms_condition': request.data.get('terms_condition', False)  
            }
        )

        personal_details_data = {
            'location': request.data.get('location'),
            'university': request.data.get('university'),
            'role': request.data.get('role')
        }
        
        student_details, created = StudentPersonalDetails.objects.update_or_create(
            student=student,
            defaults=personal_details_data
        )

        if course_id and batch_id:
            try:
                course = Course.objects.get(id=int(course_id))
                batch = Batch.objects.get(course=course, id=int(batch_id))
                batch.students.add(student)
            except Course.DoesNotExist:
                return Response({'message': 'Course not found.', 'status': status.HTTP_404_NOT_FOUND})
            except Batch.DoesNotExist:
                return Response({'message': 'Batch not found.', 'status': status.HTTP_404_NOT_FOUND})

        return Response({'message': 'Student created/updated successfully.', 'status': status.HTTP_200_OK})


class ChangePassword(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.user.id
        obj_user = User.objects.get(id=user_id)
        old_password = request.data.get("old_password")
        password1 = request.data.get("password")
        password2 = request.data.get("confirm_password")
        if len(old_password) != 0 and len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
            if obj_user.check_password(old_password) :
                password = make_password(password1)
                obj_user.password = password
                obj_user.save()
                check_subadmin = SubAdmin.objects.filter(user=obj_user)
                if check_subadmin:
                    subadmin = check_subadmin.first()
                    subadmin.password_raw = password1
                    subadmin.save()
                return Response({"message":"Password updated successfully.", "status":status.HTTP_200_OK})
            else:
                return Response({"message":"Old password does not match.", "status":status.HTTP_400_BAD_REQUEST})
        else:
            return Response({"message":"Password and Confirm password does not match.", "status":status.HTTP_400_BAD_REQUEST})


class AddStaff(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.data.get('user_id')

        email = request.data.get('email')
        phone_num = request.data.get('phone_num')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        photo = request.FILES.get('photo')
        location = request.data.get('location')
        gender = request.data.get('gender')
        team = request.data.get('team')

        state = request.data.get('state')
        city = request.data.get('city')
        area = request.data.get('area')
        branch = request.data.get('branch')
        country = request.data.get('country')
        mode = request.data.get('mode')

        present_company = request.data.get('present_company')
        resume = request.FILES.get('resume')
        terms_condition = request.data.get('terms_condition')
        signature = request.FILES.get('signature')
        current_salary = request.data.get('current_salary')

        if not all([email, phone_num, first_name, last_name]):
            return Response({
                'message': 'Email, phone number, first name, and last name are required.',
                'status': status.HTTP_400_BAD_REQUEST
            })
        if not user_id:
            # Creating a new user
            username = request.data.get('username')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')

            if not username or not password:
                return Response({
                    'message': 'Username and password are required.',
                    'status': status.HTTP_400_BAD_REQUEST
                })

            if password != confirm_password:
                return Response({
                    'message': 'Passwords do not match.',
                    'status': status.HTTP_400_BAD_REQUEST
                })

            # Create new user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        else:
            user = get_object_or_404(User, id=user_id)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        if team == "Sales Person":
            sales_person, created = SalesPerson.objects.update_or_create(
                user=user,
                defaults={
                    'email': email,
                    'phone_num': phone_num,
                    'photo': photo,
                    'gender':gender,
                    'location': location,
                    'state': state,
                    'city': city,
                    'area': area,
                    'branch': branch,
                    'country':country,
                    'mode': mode,
                    'password_raw':password,
                    'current_salary':current_salary
                }
            )
        elif team == "Data Entry User":
            data_entry_user, created = DataEntryUser.objects.update_or_create(
                user=user,
                defaults={
                    'email': email,
                    'phone_num': phone_num,
                    'photo': photo,
                    'gender':gender,
                    'location': location,
                    'password_raw':password,
                    'current_salary':current_salary
                }
            )
        elif team == "Mentor":
            mentor, created = Instructor.objects.update_or_create(
                user=user,
                defaults={
                    'email': email,
                    'phone_num': phone_num,
                    'photo': photo,
                    'gender':gender,
                    'location': location,
                    'password_raw':password,
                    'terms_condition': terms_condition,
                    'resume':resume,
                    'signature':signature,
                    'present_company':present_company,
                    'current_salary':current_salary
                }
            )
        return Response({
            'message': 'Staff member has been successfully added or updated.',
            'status': status.HTTP_200_OK
        })


class AllStaffList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)
        filter_type = request.GET.get('filter_type', 'All')

        combined_data = []

        if filter_type == 'Mentor':
            instructors = Instructor.objects.filter(is_active=True)
            instructor_serializer = MentorSerializer(instructors, many=True)
            combined_data = instructor_serializer.data

        elif filter_type == 'Sales Caller':
            sales_people = SalesPerson.objects.filter(is_active=True)
            sales_person_serializer = SalesPersonSerializer(sales_people, many=True)
            combined_data = sales_person_serializer.data

        elif filter_type == 'Data Entry User':
            data_entry_users = DataEntryUser.objects.filter(is_active=True)
            data_entry_user_serializer = DataEntryUserSerializer(data_entry_users, many=True)
            combined_data = data_entry_user_serializer.data

        elif filter_type == 'All' or not filter_type:
           
            instructors = Instructor.objects.filter(is_active=True)
            sales_people = SalesPerson.objects.filter(is_active=True)
            data_entry_users = DataEntryUser.objects.filter(is_active=True)

            instructor_serializer = MentorSerializer(instructors, many=True)
            sales_person_serializer = SalesPersonSerializer(sales_people, many=True)
            data_entry_user_serializer = DataEntryUserSerializer(data_entry_users, many=True)

            combined_data = (
                instructor_serializer.data + 
                sales_person_serializer.data + 
                data_entry_user_serializer.data
            )

        else:
            return Response({'error': 'Invalid filter_type'}, status=400)

        # Pagination
        total_items = len(combined_data)
        start_index = (page - 1) * int(page_size)
        end_index = start_index + int(page_size)
        paginated_data = combined_data[start_index:end_index]

        response_data = {
            'page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': (total_items + int(page_size) - 1) // int(page_size),
            'results': paginated_data
        }

        return Response(response_data)


class StaffDetails(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        res = {}
        user_id = request.GET.get('user_id')
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)
        user = User.objects.filter(id=int(user_id)).first()

        if not user:
            res["user"] = {}
            res["leave_data"] = []
            res["payment_data"] = []
            res["status"] = status.HTTP_404_NOT_FOUND
            res["message"] = "USER NOT FOUND"
            return Response(res)

        if Instructor.objects.filter(user=user).exists():
            get_user_details = Instructor.objects.filter(user=user).first()
            user_details = InstructorSerializer(get_user_details).data
            user_type = "Instructor"
        
        elif SalesPerson.objects.filter(user=user).exists():
            get_user_details = SalesPerson.objects.filter(user=user).first()
            user_details = SalesPersonSerializer(get_user_details).data
            user_type = "Sales Person"
        
        elif DataEntryUser.objects.filter(user=user).exists():
            get_user_details = DataEntryUser.objects.filter(user=user).first()
            user_details = DataEntryUserSerializer(get_user_details).data
            user_type = "Data Entry User"
        
        else:
            res["user"] = {}
            res["leave_data"] = []
            res["payment_data"] = []
            res["status"] = status.HTTP_401_UNAUTHORIZED
            res["message"] = "UNAUTHORIZED USER"
            return Response(res)
        
        leave_record = LeaveRecord.objects.filter(user=user)
        leave_record_data = LeaveRecordSerializer(leave_record, many=True).data

        expense_type = ExpenseType.objects.filter(type="Salary").first()
        salary_list = Expense.objects.filter(to_user=user, expense_type=expense_type,status=True)

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(salary_list, request)

        expenses = ExpenseSerializer(paginated_queryset, many=True)

        response_data = {
            "user": user_details,
            "user_type": user_type,  
            "leave_data": leave_record_data,
            "payment_data": expenses.data,
            "page": int(page),
            "page_size": int(page_size)
        }

        return paginator.get_paginated_response(response_data)


class DeleteStaff(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        res = {}
        user_id = request.data.get('user_id')        
        user = User.objects.filter(id=user_id).first()
        if not user:
            res["status"] = status.HTTP_404_NOT_FOUND
            res["message"] = "User not found"
            return Response(res, status=status.HTTP_404_NOT_FOUND)

        staff_types = [Instructor, SalesPerson, DataEntryUser]
        for staff_model in staff_types:
            staff_user = staff_model.objects.filter(user=user).first()
            if staff_user:
                staff_user.is_active = False
                staff_user.save()
                res["status"] = status.HTTP_200_OK
                res["message"] = f'{staff_model.__name__} user deactivated successfully'
                return Response(res, status=status.HTTP_200_OK)

        res["status"] = status.HTTP_401_UNAUTHORIZED
        res["message"] = "Unauthorized user"
        return Response(res, status=status.HTTP_401_UNAUTHORIZED)


class DeletedStaffList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 5))

        instructors = Instructor.objects.filter(is_active=False)
        sales_people = SalesPerson.objects.filter(is_active=False)
        data_entry_users = DataEntryUser.objects.filter(is_active=False)

        instructor_serializer = MentorSerializer(instructors, many=True)
        sales_person_serializer = SalesPersonSerializer(sales_people, many=True)
        data_entry_user_serializer = DataEntryUserSerializer(data_entry_users, many=True)

        combined_data = instructor_serializer.data + sales_person_serializer.data + data_entry_user_serializer.data

        total_items = len(combined_data)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_data = combined_data[start_index:end_index]

        response_data = {
            'page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': (total_items + page_size - 1) // page_size,  
            'results': paginated_data
        }

        return Response(response_data)
    

class ExpenseList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        page = int(request.GET.get('page', 1))  
        page_size = int(request.GET.get('page_size', 5))  
        start_date = request.GET.get('start_date')  
        end_date = request.GET.get('end_date')  
        sort_order = request.GET.get('sort_order') 

        queryset = Expense.objects.all()

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(date_time__date__range=[start_date, end_date])
            except ValueError:
                return Response({"message": "Invalid date format. Use YYYY-MM-DD.", "status": status.HTTP_400_BAD_REQUEST})

        elif start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(date_time__date=start_date)
            except ValueError:
                return Response({"message": "Invalid date format. Use YYYY-MM-DD.", "status": status.HTTP_400_BAD_REQUEST})

        if sort_order == 'low_to_high':
            queryset = queryset.order_by('amount')
        elif sort_order == 'high_to_low':
            queryset = queryset.order_by('-amount')
        else:
            queryset = queryset.order_by('-id') 

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = CustomExpenseSerializer(paginated_queryset, many=True)

        total_per_type = Expense.objects.values('expense_type__type').annotate(total_amount=Sum('amount'))
        total_expenses_count = queryset.count()

        # Response data
        response_data = {
            "expenses": serializer.data,
            "total_per_expense_type": list(total_per_type),
            "total_expenses_count": total_expenses_count,
            "page": page,
            "page_size": page_size,
        }

        return paginator.get_paginated_response(response_data)


class ExpenseTypeList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) 

    def get(self, request):
        expense_types = ExpenseType.objects.all()
        serializer = ExpenseTypeSerializer(expense_types, many=True)
        return Response(serializer.data)


class AddExpense(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) 

    def post(self, request):
        try:
            from_user= request.user
            expense_type_id = request.data.get('expense_type_id')
            to_user_id = request.data.get('to_user_id')            
            to_user_details = request.data.get('to_user_details')
            to_user_type = request.data.get('to_user_type')
            amount = request.data.get('amount')
            transaction_no = request.data.get('transaction_no')
            transaction_mode = request.data.get('transaction_mode')
            status_value = request.data.get('status', False)
            receipt = request.FILES.get('receipt')

            if not expense_type_id or not amount:
                    return Response({'message': 'Missing required fields.', 'status':status.HTTP_400_BAD_REQUEST})

            expense_type = ExpenseType.objects.filter(id=expense_type_id).first()
            if not expense_type:
                return Response({'message': 'Expense type not found.', 'status':status.HTTP_400_BAD_REQUEST})
            
            to_user = User.objects.get(id=to_user_id)
            amount_decimal = Decimal(amount)

            expense = Expense(
                expense_type=expense_type,
                to_user=to_user,
                from_user=from_user,
                to_user_details=to_user_details,
                to_user_type=to_user_type,
                amount=amount_decimal,
                transaction_no=transaction_no,
                transaction_mode=transaction_mode,
                status=status_value,
                receipt=receipt
            )
            expense.save()

            return Response({'message': 'Expense added successfully', 'status':status.HTTP_201_CREATED})
    
        except User.DoesNotExist:
            return Response({'message': 'User not found', 'status':status.HTTP_404_NOT_FOUND})
        except ExpenseType.DoesNotExist:
            return Response({'message': 'ExpenseType not found', 'status':status.HTTP_404_NOT_FOUND})
        except Exception as e:
            return Response({'message': str(e), 'status':status.HTTP_400_BAD_REQUEST})
        

