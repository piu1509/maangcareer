# from django.shortcuts import render

# from .models import Notice, Student
from .models import *
from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.serializers import ModelSerializer
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from courseManagement.models import *
from testsManagement.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from freeCourseManagement.models import *



# class NoticeSerializer(ModelSerializer):
#     class Meta:
#         model = Notice
#         fields = '__all__'

# class NoticeViewSet(ListAPIView):
#     queryset = Notice.objects.all()
#     serializer_class = NoticeSerializer

class ProfileUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email'
        )

class ProfileSerializer(ModelSerializer):
    user = ProfileUserSerializer()
    class Meta:
        model = Student
        fields = (
            'phone_num',
            'user'
        )

class ProfileViewSet(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Student.objects.all()
    serializer_class = ProfileSerializer

class ProfilePasswordUpdate(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Student.objects.all()
    serializer_class = ProfileSerializer
    def post(self, request):
        user_id = request.user.id
        obj_user = User.objects.get(id=user_id)
        old_password = request.POST.get("old_password")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if len(old_password) != 0 and len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
            if obj_user.check_password(old_password) :
                password = make_password(password1)
                obj_user.password = password
                obj_user.save()
                return Response({"message":1}, status=status.HTTP_200_OK)
            else:
                return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)
        
# class StudentProfileInfo(RetrieveAPIView):
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = (IsAuthenticated,)
#     queryset = Student.objects.all()
#     serializer_class = ProfileSerializer

#     def get(self, request):
#         user_id = request.user.id      
#         std_obj = Student.objects.get(user_id=user_id)
#         ph = std_obj.phone_num
#         profile_pic = std_obj.profile_img.url if std_obj.profile_img else None
#         f_nm = std_obj.user.first_name
#         l_nm = std_obj.user.last_name
#         email = std_obj.user.email
#         get_batch = BatchJoined.objects.filter(student__id=std_obj.id)
#         data = []
#         if get_batch.exists():
#             for i in get_batch:
#                 batch_info = {
#                     'course': i.batch.course.name,
#                     'start_date': i.batch.start_date,
#                     'end_date': i.batch.end_date,
#                 }
#                 data.append(batch_info)
#             return Response({"message":1,"Student_f_nm":f_nm,"Student_l_nm":l_nm,"Student_email":email,"Student_ph_no":ph,"Student_profile_pic":profile_pic,"Stud_course_details":data}, status=status.HTTP_200_OK)
            
#         else:
#             return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)

#05/01/2024        
class StudentProfileInfo(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id      
            std_obj = Student.objects.get(user_id=user_id)
            ph = std_obj.phone_num
            terms_conditions = std_obj.terms_condition
            profile_pic = std_obj.profile_img.url if std_obj.profile_img else None
            f_nm = std_obj.user.first_name
            l_nm = std_obj.user.last_name
            email = std_obj.user.email
            get_batch = Batch.objects.filter(students__id=std_obj.id)
            data = []

            if get_batch.exists():
                for batch in get_batch:
                    inst_project_assign = []
                    batch_joined = BatchJoined.objects.filter(student=std_obj, batch=batch).first()
                    if batch_joined:
                        projects_topics = batch_joined.assign_topics.all()
                        projects = batch_joined.assign_projects.all()

                        for topic in projects_topics:
                            project_names = [project.project_name for project in projects if project in topic.project_name.all()]
                            inst_project_assign.append({
                                "is_completed_batch": batch_joined.batch.completed,
                                "batch_id": batch_joined.batch.id,
                                "project_title": topic.project_topic,
                                "project_topic": project_names
                            })

                    batch_info = {
                        'batch_id': batch.id,
                        'course': batch.course.name,
                        'start_date': batch.start_date,
                        'end_date': batch.end_date,
                        'inst_project_assign': inst_project_assign
                    }
                    data.append(batch_info)

            response_data = {
                "message": 1,
                "Student_f_nm": f_nm,
                "Student_l_nm": l_nm,
                "Student_email": email,
                "Student_ph_no": ph,
                "Student_terms_conditions": terms_conditions,
                "Student_profile_pic": profile_pic,
                "Stud_course_details": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)      
  
        
class ProfileDetailsUpdate(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Student.objects.all()
    serializer_class = ProfileSerializer

    def post(self, request):
        user_id = request.user.id      
        obj_user = User.objects.get(id=user_id)
        std_obj = Student.objects.get(user_id=user_id)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        profile_pic = request.FILES.get("profile_pic")
        if len(first_name) != 0 and len(last_name) != 0  and first_name != None and last_name != None :
            obj_user.first_name = first_name 
            obj_user.last_name  = last_name
            obj_user.save() 
            std_obj.profile_img = profile_pic
            std_obj.save() 
            return Response({"message":1}, status=status.HTTP_200_OK)
        else:
            return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)

#new_change1      
# class AllNotifications(ListAPIView):  # new code
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try :
#             all_notice = Notice.objects.all().order_by("-id")
#             std_id = [i["id"] for i in Student.objects.filter(user_id=request.user.id).values("id")]
#             stud_notification = NotificationStatus.objects.filter(student_id=std_id[0])
#             data = []
#             notice_count = 0
#             if stud_notification.exists():
#                 previous_notification = stud_notification.values("notice__id")
#                 previous_notification_id = [i["notice__id"] for i in previous_notification]
#                 all_notice = all_notice.exclude(id__in=previous_notification_id)
#             else:
#                 pass
#             msg_details = MessageDetails.objects.filter(student_id = std_id[0], is_read=False)
#             for j in msg_details:
#                 notice_info = {
#                     'notice_id': j.id,
#                     'condition':j.title,
#                     'status': "autometic notice",
#                     'content': j.content,
#                     # 'date': j.message_created,
#                     'date': j.message_created.strftime("%Y-%m-%d"),
#                 }
#                 data.append(notice_info)

#             for i in all_notice :
#                 notice_info = {
#                     'notice_id': i.id,
#                     'status': "manual notice",
#                     'content': i.content,
#                     'date': i.date,
#                 }
#                 data.append(notice_info)
#             notice_count = len(data)
#             return Response({"message":1 ,"notification_count":notice_count,"current_notification":data}, status=status.HTTP_200_OK)
#         except Exception as e :
#             return Response({"message":0,"error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

# #new_change1     
# class MarkAsRead(APIView):
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = (IsAuthenticated,)
#     def post(self, request):
#         try:
#             notification_id = request.POST.get('notification_id')
#             status_msg = request.POST.get('status_msg')
#             std_id = [i["id"] for i in Student.objects.filter(user_id=request.user.id).values("id")]
#             if status_msg == 'manual notice' :
#                 stud_notification = NotificationStatus.objects.filter(student_id__in=std_id)
#                 all_notice = Notice.objects.all().order_by("-id").values("id")
#                 if stud_notification.exists():
#                     previous_notification = stud_notification.values("notice__id")
#                     previous_notification_id = [i["notice__id"] for i in previous_notification]
#                     all_notice = all_notice.exclude(id__in=previous_notification_id)
#                     stud_notification = stud_notification.first()
#                     save_n = NotificationStatus.objects.get(id=stud_notification.id)
#                     save_n.notice.add(notification_id)
#                 else:
#                     save_notification = NotificationStatus(student_id=std_id[0])
#                     save_notification.save()
#                     save_notification.notice.add(notification_id)
#             else:
#                 MessageDetails.objects.filter(id = int(notification_id)).update(is_read=True)
#             return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
#         except Exception as e :
#             return Response({"message":0,"error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

#10/01/2024
class TermsAndConditionView(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_id = request.user.id      
        std_obj = Student.objects.get(user_id=user_id)
        message = 1 if std_obj.terms_condition else 0
        return Response({"message":message}, status=status.HTTP_200_OK)
    def post(self, request):
        user_id = request.user.id      
        std_obj = Student.objects.get(user_id=user_id)
        terms_conditions = request.data.get('terms_conditions', False)
        if not std_obj.terms_condition:
            std_obj.terms_condition = terms_conditions
            std_obj.save()
            return Response({"message":1}, status=status.HTTP_200_OK)
        else:
            return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,) 

    def get(self, request):
        data = {"status":status.HTTP_400_BAD_REQUEST, "message":None}
        try:
            user = request.user
            check_student = Student.objects.filter(user=user)
            check_instructor = Instructor.objects.filter(user=user)
            check_salesperson = SalesPerson.objects.filter(user=user)
            if check_student: 
                student = check_student.first()
                check_free_course = FreeCourseJoinee.objects.filter(student__user=user)
                check_paid_course = Batch.objects.filter(students__id=student.id)
                free_course_name = list(check_free_course.values_list("course__name"))
                paid_sourse_name = list(check_paid_course.values_list("course__name"))
                student_details = StudentPersonalDetails.objects.filter(student=student).first()
                details = {
                    "user_id":user.id,
                    "first_name": user.first_name,
                    "last_name":user.last_name,
                    "email":user.email,
                    # "password": user.password,
                    'user_type': 'student',
                    "phn_number":student.phone_num,
                    "image":student.profile_img.url if student.profile_img else None,
                    "free_course_name": free_course_name if len(free_course_name) > 0 else None,
                    "paid_course_name": paid_sourse_name if len(paid_sourse_name) > 0 else None,
                    "location":student_details.location if student_details else None,
                    "university":student_details.university if student_details else None,
                    "role": student_details.role if student_details else None
                }
            elif check_instructor:
                instructor = check_instructor.first()
                check_paid_course = Batch.objects.filter(instructor_id=instructor.id)
                paid_sourse_name = list(check_paid_course.values_list("course__name"))
                details = {
                    "user_id":user.id,
                    "first_name": user.first_name,
                    "last_name":user.last_name,
                    "email":user.email,
                    # "password": user.password,
                    'user_type': 'instructor',
                    "phn_number":instructor.phone_num,
                    "image":instructor.photo.url if instructor.photo else None,
                    "free_course_name": None,
                    "paid_course_name": paid_sourse_name if len(paid_sourse_name) > 0 else None,
                    "location":instructor.location,
                    "university":None,
                    "role": None
                }
            elif check_salesperson:
                salesperon = check_salesperson.first()
                details = {
                    "user_id":user.id,
                    "first_name": user.first_name,
                    "last_name":user.last_name,
                    "email":user.email,
                    # "password": user.password,
                    'user_type': 'instructor',
                    "phn_number":salesperon.phone_num,
                    "image":salesperon.photo.url if salesperon.photo else None,
                    "free_course_name": None,                    
                    "paid_course_name": None,
                    "location":salesperon.location,
                    "university":None,
                    "role": None
                }
            data["data"] = details                
            data["status"] = status.HTTP_200_OK
            data["message"] = "Profile details fetched successfully."            
                
        except Exception as e:          
            data["data"] = []
            data["status"] = status.HTTP_400_BAD_REQUEST
            data["message"] = f"{str(e)}"
        return Response(data)


class ProfileEditView(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = {"status": status.HTTP_400_BAD_REQUEST, "message": None}
        try:
            user = request.user
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            location = request.data.get("location")
            university = request.data.get("university")
            role = request.data.get("role")
            image = request.FILES.get("image")
            old_password = request.data.get('old_password')
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')

            # Update the user's basic information
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Update the user's password if provided
            if password1 not in ['', ' ', None, 'null']:
                if len(old_password) != 0 and len(password1) != 0 and len(password2) != 0 and password1 == password2:
                    if user.check_password(old_password):
                        user.set_password(password1)  # Use set_password to properly hash the password
                        user.save()
                        data["message"] = "Profile and Password updated successfully."
                    else:
                        data["message"] = "Old password is incorrect."
                        return Response(data)
                else:
                    data["message"] = "Password is not given or password and confirm password does not match."
            # Check if the user is a student, instructor, or salesperson and update the profile
            if Student.objects.filter(user=user).exists():
                student = Student.objects.get(user=user)
                if image:
                    student.profile_img = image
                student.save()

                student_detail, created = StudentPersonalDetails.objects.get_or_create(student=student)
                if location:
                    student_detail.location = location
                if university:
                    student_detail.university = university
                if role:
                    student_detail.role = role
                student_detail.save()

            elif Instructor.objects.filter(user=user).exists():
                instructor = Instructor.objects.get(user=user)
                if image:
                    instructor.photo = image
                if location:
                    instructor.location = location
                instructor.save()

            elif SalesPerson.objects.filter(user=user).exists():
                salesperson = SalesPerson.objects.get(user=user)
                if image:
                    salesperson.photo = image
                if location:
                    salesperson.location = location
                salesperson.save()

            data["status"] = status.HTTP_200_OK
            data["message"] = data["message"] or "Profile details updated successfully."

        except Exception as e:
            data["status"] = status.HTTP_400_BAD_REQUEST
            data["message"] = f"An error occurred: {str(e)}"
        
        return Response(data)
