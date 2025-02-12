from django.shortcuts import render

# Create your views here.
from .models import *
from rest_framework.generics import ListAPIView , RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from courseManagement.models import *
from testsManagement.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import random
import ast
from datetime import datetime ,timedelta
from django.db.models import Max
import requests
import json
from rest_framework import serializers
from collections import defaultdict
from django.db.models import Q
from django.db.models import F
from django.contrib.auth.hashers import make_password
from django.conf import settings    
import time
from datetime import timezone
import base64

RAPID_API_KEY = settings.RAPID_API_KEY



# def find_next_number(sorted_list, c_num):
#     index_c_num = sorted_list.index(c_num)
#     if index_c_num < len(sorted_list) - 1:
#         return sorted_list[index_c_num + 1]
#     else:
#         return sorted_list[0] if sorted_list else None


def get_next_index(lst, number):
    if number in lst:
        current_index = lst.index(number)
        next_index = (current_index + 1) % len(lst)
        return lst[next_index]
    else:
        return None
    


def get_completed_days(timetable):
    current_datetime = datetime.now()
    completed_days = []
    for index, entry in enumerate(timetable):
        start_date = entry.get('start_date')
        start_time = entry.get('start_time')
        start_datetime = datetime.combine(start_date, start_time) if start_date and start_time else None

        if start_datetime and current_datetime >= start_datetime:
            completed_days.append(index + 1)
    return completed_days


# def current_batch(timetable):
#     max_date = None

#     for entry in timetable:
#         start_date = entry.get('start_date')
#         if start_date:
#             if max_date is None or start_date > max_date :
#                 max_date = start_date
#     max_date = max_date + timedelta(30)
#     current_date = datetime.now().date()
#     if max_date > current_date:
#         return True
#     else:
#         return False


def current_batch(timetable, rev_date=None):
    current_date = datetime.now().date()
    if rev_date is None:
        max_date = datetime.min.date() 

        for entry in timetable:
            start_date = entry.get('start_date')
            if start_date:
                if max_date == 0 or start_date > max_date:
                    max_date = start_date      
        max_date = max_date + timedelta(days=30)
        result = max_date > current_date
    else:
        result = rev_date > current_date
    return result 

def compiler_question_all_practice(user_id,q_id,course_id):  ##
    inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
    if len(inst_id) > 0 :
        inst_id = inst_id[0]
    else:
        inst_id = ""
    check_ans = CompilerQuestionAtempt.objects.filter(instructor_id=inst_id,question__practice_mock=False, question_id = int(q_id),question__course_id =course_id,status=True, button_clicked = 'Submit' ).values("id","question_id","student_id","code_response_status")
    if check_ans.exists():
        return True
    else:
        return False
    

def compiler_question_approches_practice(q_id):
    queryset = list(CompilerQuestion.objects.filter(id = q_id, practice_mock=False,disable= False).values())
    approch_flg = []
    exam_pic_flg =[]
    all_data =[]
    if queryset[0]["check_exm_pic1"] == True:
        # example_pic1 = queryset[0]["example1_picture"]
        exam_1 ={
            "name":"Sample Eg1",
            "example_pic":CompilerQuestion.objects.filter(id = q_id, practice_mock=False,disable= False).first().example1_picture.url
        }
        exam_pic_flg.append(exam_1)
    else:
        None
    if queryset[0]["check_exm_pic2"] == True:
        # example_pic2 = queryset[0]["example2_picture"]
        exam_2 ={
            "name":"Sample Eg2",
            "example_pic":CompilerQuestion.objects.filter(id = q_id, practice_mock=False,disable= False).first().example2_picture.url
        }
        exam_pic_flg.append(exam_2)
    else:
        None
    if queryset[0]["check_exm_pic3"] == True:
        # example_pic3 = queryset[0]["example3_picture"]
        exam_3 ={
            "name":"Sample Eg3",
            "example_pic":CompilerQuestion.objects.filter(id = q_id, practice_mock=False,disable= False).first().example3_picture.url
        }
        exam_pic_flg.append(exam_3)
    else:
        None
    #main_dict appr1
    my_dict1 = {}
    #main_dict appr2
    my_dict2 = {}
    #main_dict appr3
    my_dict3 = {}

    # approach1_block
    if queryset[0]["approach1_block"] == True:
        my_dict1["id"] = 1
        my_dict1["approach_title"] = queryset[0]["approach1_title"]
        my_dict1["approach_intuition"] = queryset[0]["approach1_intuition"]
        my_dict1["approach_algorithm"] = queryset[0]["approach1_algo"]
        my_dict1["approach_complexity_analysis"] = queryset[0]["approach1_complexity_analysis"]
    # apporch pic:
    if queryset[0]["approach1_picture_implementation"] == True : 
        code_imgs = [{"pic": queryset[0]["approach1_pic1"]} if queryset[0]["check_pic1"] == True else None,
                {"pic": queryset[0]["approach1_pic2"]} if queryset[0]["check_pic2"] == True else None,
                {"pic": queryset[0]["approach1_pic3"]} if queryset[0]["check_pic3"] == True else None,
                {"pic": queryset[0]["approach1_pic4"]} if queryset[0]["check_pic4"] == True else None,
                {"pic": queryset[0]["approach1_pic5"]} if queryset[0]["check_pic5"] == True else None ]
        my_dict1["code_imgs"] = code_imgs
    else:
        my_dict1["code_imgs"] = []
    #apporch code text:
    if queryset[0]["approach1_code_implementation"] == True :
        code_text_data = [
            {
                "id":1,
                "language": "c++",
                "code": queryset[0]["approach1_cpp_code"]
            },
            {
                "id":2,
                "language": "java",
                "code": queryset[0]["approach1_java_code"]
            },
            {
                "id":3,
                "language": "python",
                "code": queryset[0]["approach1_python_code"]
            }
        ]
        
        my_dict1["code_text_data"] = code_text_data
    else:
        my_dict1["code_text_data"] = []
    approch_flg.append(my_dict1)
  
    # approach2_block
    if queryset[0]["approach2_block"] == True:
        my_dict2["id"] = 2
        my_dict2["approach_title"] = queryset[0]["approach2_title"]
        my_dict2["approach_intuition"] = queryset[0]["approach2_intuition"]
        my_dict2["approach_algorithm"] = queryset[0]["approach2_algo"]
        my_dict3["approach_complexity_analysis"] = queryset[0]["approach2_complexity_analysis"]
    # apporch pic:
        if queryset[0]["approach2_picture_implementation"] == True : 
            code_imgs = [{"pic": queryset[0]["approach2_pic1"]} if queryset[0]["check_pic1_approach2"] == True else None,
                    {"pic": queryset[0]["approach2_pic2"]} if queryset[0]["check_pic2_approach2"] == True else None,
                    {"pic": queryset[0]["approach2_pic3"]} if queryset[0]["check_pic3_approach2"] == True else None,
                    {"pic": queryset[0]["approach2_pic4"]} if queryset[0]["check_pic4_approach2"] == True else None,
                    {"pic": queryset[0]["approach2_pic5"]} if queryset[0]["check_pic5_approach2"] == True else None ]
            my_dict2["code_imgs"] = code_imgs
        else:
            my_dict2["code_imgs"] = []
        #apporch code text:
        if queryset[0]["approach2_code_implementation"] == True :
            code_text_data = [
                {
                    "id":1,
                    "language": "c++",
                    "code": queryset[0]["approach2_cpp_code"]
                },
                {
                    "id":2,
                    "language": "java",
                    "code": queryset[0]["approach2_java_code"]
                },
                {
                    "id":3,
                    "language": "python",
                    "code": queryset[0]["approach2_python_code"]
                }
            ]
            
            my_dict2["code_text_data"] = code_text_data
        else:
            my_dict2["code_text_data"] = []
        
        approch_flg.append(my_dict2)

    # approach3_block
    if queryset[0]["approach3_block"] == True:
        my_dict3["id"] = 3
        my_dict3["approach_title"] = queryset[0]["approach3_title"]
        my_dict3["approach_intuition"] = queryset[0]["approach3_intuition"]
        my_dict3["approach_algorithm"] = queryset[0]["approach3_algo"]
        my_dict3["approach_complexity_analysis"] = queryset[0]["approach3_complexity_analysis"]
        # apporch pic:
        if queryset[0]["approach3_picture_implementation"] == True : 
            code_imgs = [{"pic": queryset[0]["approach3_pic1"]} if queryset[0]["check_pic1_approach3"] == True else None,
                    {"pic": queryset[0]["approach3_pic2"]} if queryset[0]["check_pic2_approach3"] == True else None,
                    {"pic": queryset[0]["approach3_pic3"]} if queryset[0]["check_pic3_approach3"] == True else None,
                    {"pic": queryset[0]["approach3_pic4"]} if queryset[0]["check_pic4_approach3"] == True else None,
                    {"pic": queryset[0]["approach3_pic5"]} if queryset[0]["check_pic5_approach3"] == True else None ]
            my_dict3["code_imgs"] = code_imgs
        else:
            my_dict3["code_imgs"] = []
        #apporch code text:
        if queryset[0]["approach3_code_implementation"] == True :
            code_text_data = [
                {
                    "id":1,
                    "language": "c++",
                    "code": queryset[0]["approach3_cpp_code"]
                },
                {
                    "id":2,
                    "language": "java",
                    "code": queryset[0]["approach3_java_code"]
                },
                {
                    "id":3,
                    "language": "python",
                    "code": queryset[0]["approach3_python_code"]
                }
            ]
            
            my_dict3["code_text_data"] = code_text_data
        else:
            my_dict3["code_text_data"] = []
        approch_flg.append(my_dict3)
    all_data ={"approch_flg":approch_flg,"example_pics":exam_pic_flg}    
    return all_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'phone_num', 'joined_date', 'profile_img', 'terms_condition']

class CourseSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubmission
        fields = ['submission_topic']

class TaskUploadSerializer(serializers.ModelSerializer):
    student_first_name = serializers.CharField(source='student.user.first_name', read_only=True)
    student_last_name = serializers.CharField(source='student.user.last_name', read_only=True)
    topic = serializers.CharField(source='project_topics.project_topic', read_only=True)
    project = serializers.CharField(source='submited_project.project_name', read_only=True)
    course = serializers.CharField(source='batch.course.name', read_only=True)
    class Meta:
        model = TaskSubmission
        fields = ["id", "batch_id", "student_first_name","course", "project", "topic", "student_last_name", "file", "status", "created_at"]


class CourseSerializer(serializers.ModelSerializer): #31/01/2024
    class Meta:
        model = Course
        fields = ['id', 'name']

class SyllabusSerializer(serializers.ModelSerializer):
    course = CourseSerializer() 
    class Meta:
        model = Syllabus
        # fields = ['id', 'week', 'day', 'course', 'topic', 'file', 'uploaded_at']
        fields = ['id', 'week', 'day', 'course', 'topic', 'file', 'uploaded_at','description']

class InstructorTermsAndConditionView(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_id = request.user.id      
        inst_obj = Instructor.objects.get(user_id=user_id)
        message = 1 if inst_obj.terms_condition else 0
        return Response({"message":message}, status=status.HTTP_200_OK)
    def post(self, request):
        user_id = request.user.id      
        inst_obj = Instructor.objects.get(user_id=user_id)
        terms_conditions = request.data.get('terms_conditions', False)
        if not inst_obj.terms_condition:
            inst_obj.terms_condition = terms_conditions
            inst_obj.save()
            return Response({"message":1}, status=status.HTTP_200_OK)
        else:
            return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)

class InstructorRulesAndRegulationView(ListAPIView):

    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_id = request.user.id      
        inst_obj = Instructor.objects.get(user_id=user_id)
        counter = 1 if inst_obj.rules_regulation_count  else 0
        return Response({"counter":counter}, status=status.HTTP_200_OK)
    def post(self, request):
        user_id = request.user.id      
        inst_obj = Instructor.objects.get(user_id=user_id)
        count = int(request.data.get('count'))
        if count == 10 :
            inst_obj.rules_regulation_count = 1
            inst_obj.save()
            return Response({'message': 'Count updated successfully'})
        else:
            return Response({'message': 'complete all steps'})


class InstructorRulesAndRegulationPageVisitCount(ListAPIView):  #01/02/2024
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            user_id = request.user.id      
            inst_obj = Instructor.objects.get(user_id=user_id)
            inst_obj.page_visit_count += 1
            inst_obj.save()
            return Response({'message':1}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"{e}"})
        

class InstructorProfileUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email'
        )

class InstructorProfileSerializer(ModelSerializer):
    user = InstructorProfileUserSerializer()
    class Meta:
        model = Instructor
        fields = (
            'phone_num',
            'user'
        )


class InstructorProfileViewSet(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Instructor.objects.all()
    serializer_class = InstructorProfileSerializer
    
class InstructorProfilePasswordUpdate(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Instructor.objects.all()
    serializer_class = InstructorProfileSerializer
    def post(self, request):
        try:
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
        except Exception as e :
            return Response({"error":f"{e}"})

# class InstructorProfileInfo(RetrieveAPIView):
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = (IsAuthenticated,)
#     queryset = Instructor.objects.all()
#     serializer_class = InstructorProfileSerializer

#     def get(self, request):
#         try:
#             user_id = request.user.id      
#             inst_obj = Instructor.objects.get(user_id=user_id)
#             ph = inst_obj.phone_num
#             profile_pic = inst_obj.photo.url if inst_obj.photo else None
#             f_nm = inst_obj.user.first_name
#             l_nm = inst_obj.user.last_name
#             email = inst_obj.user.email
#             get_batch = Batch.objects.filter(instructor__id=inst_obj.id ,completed=False )
#             data = []
#             if get_batch.exists():
#                 for i in get_batch:
#                     batch_info = {
#                         'batch_id':i.id,
#                         'course': i.course.name,
#                         'start_date': i.start_date,
#                         'end_date': i.end_date,
#                     }
#                     data.append(batch_info)
#                 return Response({"message":1,"Instructor_f_nm":f_nm,"Instructor_l_nm":l_nm,"Instructor_email":email,"Instructor_ph_no":ph,"Instructor_profile_pic":profile_pic,"Inst_course_details":data}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)   
#         except Exception as e :
#             return Response({"error":f"{e}"}) 


class InstructorProfileInfo(RetrieveAPIView):  #05/02/2024
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Instructor.objects.all()
    serializer_class = InstructorProfileSerializer

    def get(self, request):
        try:
            user_id = request.user.id      
            inst_obj = Instructor.objects.get(user_id=user_id)
            ph = inst_obj.phone_num
            profile_pic = inst_obj.photo.url if inst_obj.photo else None
            f_nm = inst_obj.user.first_name
            l_nm = inst_obj.user.last_name
            email = inst_obj.user.email
            get_batch = Batch.objects.filter(instructor__id=inst_obj.id, completed=False)

            data = []
            if get_batch.exists():
                for i in get_batch:
                    inst_project_assign = []
                    projects_topics = i.project_topics.all()
                    for topic in projects_topics:
                        project_names = topic.project_name.values_list("project_name", flat=True)
                        inst_project_assign.append({"project_title": topic.project_topic, "project_topic": list(project_names)})
                        
                    batch_info = {
                        'batch_id': i.id,
                        'course': i.course.name,
                        'start_date': i.start_date,
                        'end_date': i.end_date,
                        'inst_project_assign': inst_project_assign
                    }
                    data.append(batch_info)
                return Response({"message":1,"Instructor_f_nm":f_nm,"Instructor_l_nm":l_nm,"Instructor_email":email,"Instructor_ph_no":ph,"Instructor_profile_pic":profile_pic,"Inst_course_details":data}, status=status.HTTP_200_OK)
            else:
                return Response({"message":1,"Instructor_f_nm":f_nm,"Instructor_l_nm":l_nm,"Instructor_email":email,"Instructor_ph_no":ph,"Instructor_profile_pic":profile_pic,"Inst_course_details":data}, status=status.HTTP_200_OK)   
        except Exception as e :
            return Response({"error":f"{e}"})            
        
class InstructorProfileDetailsUpdate(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    queryset = Instructor.objects.all()
    serializer_class = InstructorProfileSerializer

    def post(self, request):
        try:
            user_id = request.user.id      
            obj_user = User.objects.get(id=user_id)
            inst_obj = Instructor.objects.get(user_id=user_id)
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            profile_pic = request.FILES.get("profile_pic")
            if len(first_name) != 0 and len(last_name) != 0  and first_name != None and last_name != None :
                obj_user.first_name = first_name 
                obj_user.last_name  = last_name
                obj_user.save() 
                inst_obj.photo = profile_pic
                inst_obj.save() 
                return Response({"message":1}, status=status.HTTP_200_OK)
            else:
                return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)        
        except Exception as e :
            return Response({"error":f"{e}"})        


class InstructorDashboardCalenderViewList(ListAPIView):  #19/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            batch_ids = [i["id"] for i in get_batch]
            course_ids = list(set(i["course_id"] for i in get_batch))
            all_times = TimeTable.objects.filter(batch__course_id__in=course_ids, batch_id__in=batch_ids).values(
                    "batch_id","batch__course__name", "start_date", "week"
                ).order_by("batch__course__name", "week", "start_date")
            result_data = {}
            for entry in all_times:
                date_key = entry["start_date"]
                course_name = entry["batch__course__name"]
                if date_key in result_data:
                    result_data[date_key]["course_names"].append(course_name)
                else:
                    result_data[date_key] = {
                        # "batch_id": entry["batch_id"],
                        "date": entry["start_date"],
                        "course_names": [course_name],
                        "week": entry["week"],
                    }
            result_list = list(result_data.values())
            return Response({"message": 1, "all_data": result_list}, status=status.HTTP_200_OK)
        except:
            return Response({"message": 0}, status=status.HTTP_400_BAD_REQUEST)          
        


class InstructorClassCompleteProgressBar(ListAPIView):  #19/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]

            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            course_ids = list(set(i["course_id"] for i in get_batch))
            get_batches = Batch.objects.filter(instructor_id__in=inst_id, course_id__in=course_ids , completed = False ).values("id", "course__name", "start_date", "end_date")

            if not get_batches.exists():
                return Response({"course_info": "Course not found", "message": 0}, status=status.HTTP_200_OK)

            batch_details = []
            for batch_info in get_batches:
                batch_info = {
                    "batch_id": batch_info["id"],
                    "course_name": batch_info["course__name"],
                    "start_date": batch_info["start_date"],
                    "end_date": batch_info["end_date"],
                }
                batch_details.append(batch_info)

            course_attendance = defaultdict(lambda: {"total_cls_sum": 0, "completed_classes_sum": 0})
            batch_details_user = list(Batch.objects.filter(instructor_id__in=inst_id, completed=False).values_list("id", flat=True))
            current_batch_list = []

            for i in batch_details_user:
                time_table = TimeTable.objects.filter(batch_id=i).values("start_date", "start_time")
                # current_batch_ = current_batch(time_table)
                rev_date = Batch.objects.filter(id=i).first().revoke_date
                current_batch_ = current_batch(time_table, rev_date)
                if current_batch_:
                    current_batch_list.append(i)

            if len(current_batch_list) == 0:  
                return Response({"status": "Batch not found"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_data = [] 

                for batch_info in batch_details:
                    batch_id = batch_info["batch_id"]
                    time_table = TimeTable.objects.filter(batch_id=batch_id).values("start_date", "start_time")
                    total_cls = len(time_table)
                    completed_classes = get_completed_days(list(time_table))
                    course_name = batch_info["course_name"]
                    start_date = batch_info["start_date"]
                    end_date = batch_info["end_date"]
                    course_attendance[course_name]["total_cls_sum"] += total_cls
                    course_attendance[course_name]["completed_classes_sum"] += len(completed_classes)
                    total_cls_sum = total_cls
                    completed_classes_sum = len(completed_classes)
                    remaining_classes = total_cls_sum - completed_classes_sum
                    cls_attend_percentage = (completed_classes_sum / total_cls_sum) * 100 if total_cls_sum > 0 else 0
        
                    if remaining_classes != 0:
                        response_data.append({
                            "batch_id": batch_id,
                            "course_name": course_name,
                            "start_date": start_date,
                            "end_date": end_date,
                            "total_class": total_cls_sum,
                            "num_of_completed_classes": completed_classes_sum,
                            "remaining_classes": remaining_classes,
                            "cls_percentage": f"{cls_attend_percentage:.2f}",
                            "status": "",
                        })
                    else:
                        response_data.append({
                            "batch_id": batch_id,
                            "course_name": course_name,
                            "start_date": start_date,
                            "end_date": end_date,
                            "total_class": total_cls_sum,
                            "num_of_completed_classes": completed_classes_sum,
                            "remaining_classes": remaining_classes,
                            "cls_percentage": f"{cls_attend_percentage:.2f}",
                            "status": "Classes completed !",
                        })

                return Response({"coursewise_progress": response_data, "message": 1}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)         


class InstructorTimetableViewList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            batch_ids = [i["id"] for i in get_batch]
            course_ids = [i["course_id"] for i in get_batch]
            all_times_week = TimeTable.objects.filter(
                batch__course_id__in=course_ids,
                batch_id__in=batch_ids 
            ).values(
                "id",
                "batch_id",
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
                    "batch_id":entry["batch_id"],
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
        
class InstructorDashboardOngoingUpcomingUpdates(ListAPIView):  
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)        
    def get(self, request): 
        try:
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            batch_ids = [i["id"] for i in get_batch]
            all_timetable = []
            for i in batch_ids:
                timetable = list(TimeTable.objects.filter(batch_id=i).values("id", "start_date", "start_time", "end_time", "link", "week", "batch_id", "day"))
                all_timetable += timetable
            sorted_all_timetable = sorted(all_timetable, key=lambda x: (x['start_date'], x['start_time']))
            current_datetime = datetime.now()
            past_classes = [c for c in sorted_all_timetable if c['end_time'] and datetime.combine(c['start_date'], c['end_time']) < current_datetime]
            future_classes = [c for c in sorted_all_timetable if c['end_time'] and datetime.combine(c['start_date'], c['end_time']) >= current_datetime]
            for post_class in past_classes:
                post_class["course"] = Batch.objects.filter(id=post_class["batch_id"]).values("course__name")[0]["course__name"]
                post_class["course_id"] = Batch.objects.filter(id=post_class["batch_id"]).values("course_id")[0]["course_id"] #
                post_class["time_table_topic"] = TimeTable.objects.filter(week=post_class["week"], day=post_class["day"], batch_id = post_class["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=post_class["week"], course_id=int(Batch.objects.filter(id=post_class["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                today_topic_list = Topic.objects.filter(week_id=int(week_id[0]["id"]), day=post_class["day"]).values("name")
                if len(today_topic_list) == 0:
                    post_class["today_topic"] = ""
                else:
                    post_class["today_topic"] = today_topic_list[0]["name"]
            ongoing_data = []
            upcoming_data = []
            all_upcoming_data = []
            if len(future_classes) == 1:
                data = future_classes[0]
                data["course"] = Batch.objects.filter(id=data["batch_id"]).values("course__name")[0]["course__name"]
                data["course_id"] = Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"]  #
                data["time_table_topic"] = TimeTable.objects.filter(week=data["week"], day=data["day"], batch_id = data["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=data["week"], course_id=int(Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                today_topic_list = Topic.objects.filter(week_id=int(week_id[0]["id"]), day=data["day"]).values("name")
                if len(today_topic_list) == 0:
                    data["today_topic"] = ""
                else:
                    data["today_topic"] = today_topic_list[0]["name"]
                ongoing_data.append(data)
                data = {"message": "No Upcoming Class"}
                upcoming_data.append(data)
            elif len(future_classes) > 1:
                data = future_classes[0]
                data["course"] = Batch.objects.filter(id=data["batch_id"]).values("course__name")[0]["course__name"]
                data["course_id"] = Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"]  #
                data["time_table_topic"] = TimeTable.objects.filter(week=data["week"], day=data["day"], batch_id = data["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=data["week"], course_id=int(Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                today_topic_list = Topic.objects.filter(week_id=int(week_id[0]["id"]), day=data["day"]).values("name")
                if len(today_topic_list) == 0:
                    data["today_topic"] = ""
                else:
                    data["today_topic"] = today_topic_list[0]["name"]
                ongoing_data.append(data)
                data = future_classes[1]
                data["course"] = Batch.objects.filter(id=data["batch_id"]).values("course__name")[0]["course__name"]
                data["course_id"] = Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"] #
                data["time_table_topic"] = TimeTable.objects.filter(week=data["week"], day=data["day"], batch_id = data["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=data["week"], course_id=int(Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                today_topic_list = Topic.objects.filter(week_id=int(week_id[0]["id"]), day=data["day"]).values("name")
                if len(today_topic_list) == 0:
                    data["today_topic"] = ""
                else:
                    data["today_topic"] = today_topic_list[0]["name"]
                upcoming_data.append(data)
            else:
                pass
            for data in future_classes:
                data["course"] = Batch.objects.filter(id=data["batch_id"]).values("course__name")[0]["course__name"]
                data["time_table_topic"] = TimeTable.objects.filter(week=data["week"], day=data["day"], batch_id=data["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=data["week"], course_id=int(Batch.objects.filter(id=data["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                today_topic_list = Topic.objects.filter(week_id=int(week_id[0]["id"]), day=data["day"]).values("name")
                if len(today_topic_list) == 0:
                    data["today_topic"] = ""
                else:
                    data["today_topic"] = today_topic_list[0]["name"]
                all_upcoming_data.append(data)  

            data = {"ongoing": ongoing_data, "upcoming": upcoming_data, "all_upcoming_data": all_upcoming_data, "recent_passed": past_classes[::-1]}
            return Response({"response_data": data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})    
        
class InstructorCourseSelection(ListAPIView):   #24/01/2024
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            inst_obj = Instructor.objects.get(user_id=user_id)   
            data =[]
            course_batches_details = Batch.objects.filter(instructor_id = inst_obj.id ,completed = False).values("id" ,"course_id" ,"course__name")
            if course_batches_details.exists():
                for i in course_batches_details:
                        batch_info = {
                            'batch_id':i["id"],
                            'course_id': i["course_id"],
                            'course__name': i["course__name"], 
                        }
                        data.append(batch_info)
                return Response({"message":1,"course_batches_details":data}, status=status.HTTP_200_OK)
            else:
                data =[]
                return Response({"message":0,"course_batches_details":data}, status=status.HTTP_400_BAD_REQUEST)   
        except Exception as e :
            return Response({"error":f"{e}"})        



# class InstructorCourseSelectionViewList(ListAPIView):
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try:
#             user_id = request.user.id
#             inst_obj = Instructor.objects.get(user_id=user_id)   
#             course_batches_details = Batch.objects.filter(instructor_id = inst_obj.id ,completed = False).values("course_id" ,"course__name")
#             course__name = list(set(i["course__name"] for i in course_batches_details))
#             course_id = list(set(i["course_id"] for i in course_batches_details))
           
#             if course_batches_details.exists():
#                 return Response({"message":1,"course_id":course_id if course_id else None , "course__name":course__name if course__name else None , }, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)   
#         except Exception as e :
#             return Response({"error":f"{e}"})


#####RijuDjango #task14 #new
class InstructorCourseSelectionViewList(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            inst_obj = Instructor.objects.get(user_id=user_id)   
            course_batches_details = Batch.objects.filter(instructor_id=inst_obj.id, completed=False).values("course_id", "course__name").distinct()

            return Response({"message": 1, "courses": list(course_batches_details)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "courses":[]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



##########################
#mentor show the submission topic list #RijuDjango #task9
class InstructorSubmissionWeekTopicList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            course_id = request.GET.get("course_id")
            submission_topic = list(CourseSubmission.objects.filter(course_id=course_id).values("id","submission_topic","week"))
            return Response({"main_data":submission_topic})
        except Exception as e :
            return Response({"error":f"{e}"}) 

# class InstructorSubmissionPointBatchDataViewList(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             batch_id = request.GET.get('batch_id')            
#             ongoing_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__completed=False).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             ).order_by("-id")
#             assigned_projects = BatchJoined.objects.filter(batch_id=batch_id).values(
#                 'student__user__first_name', 'student__user__last_name',
#                 'assign_topic__project_topic', 'assign_project__project_name'
#             )
#             topic_by_student = {f"{project['student__user__first_name']} {project['student__user__last_name']}": {
#                 'assigned_project': project.get('assign_project__project_name', None),
#                 'assigned_topic': project.get('assign_topic__project_topic', None),
#             } for project in assigned_projects}
            
#             ongoing_grouped_data = []
#             previous_grouped_data = []

#             for entry in ongoing_data:
#                 student_name = f"{entry['student__user__first_name']} {entry['student__user__last_name']}"
#                 assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
#                 file_path = entry['file']
#                 file_url = None
#                 if file_path:
#                     file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
#                 entry_info = {
#                     "id": entry["id"],
#                     "batch_id": entry["batch_id"],
#                     "course_submission__submission_topic": entry["course_submission__submission_topic"],
#                     "student__user__first_name": entry["student__user__first_name"],
#                     "student__user__last_name": entry["student__user__last_name"],
#                     "week": entry["week"],
#                     "assigned_project": assigned_info['assigned_project'],
#                     "assigned_topic": assigned_info['assigned_topic'],
#                     "file": file_url,
#                     "status": entry['status'],
#                     "created_at": entry["created_at"],
#                 }

#                 ongoing_grouped_data.append(entry_info)

#             previous_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__completed=True).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             ).order_by("id")

#             for entry in previous_data:
#                 student_name = f"{entry['student__user__first_name']} {entry['student__user__last_name']}"
#                 assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
#                 file_path = entry['file']
#                 file_url = None
#                 if file_path:
#                     file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
#                 entry_info = {
#                     "id": entry["id"],
#                     "batch_id": entry["batch_id"],
#                     "course_submission__submission_topic": entry["course_submission__submission_topic"],
#                     "student__user__first_name": entry["student__user__first_name"],
#                     "student__user__last_name": entry["student__user__last_name"],
#                     "week": entry["week"],
#                     "assigned_project": assigned_info['assigned_project'],
#                     "assigned_topic": assigned_info['assigned_topic'],
#                     "file": file_url,
#                     "status": entry['status'],
#                     "created_at": entry["created_at"],
#                 }

#                 previous_grouped_data.append(entry_info)

#             return Response({"message":1,"ongoing_data": ongoing_grouped_data, "previous_data": previous_grouped_data}, status=status.HTTP_200_OK)  
#         except Exception as e:
#             return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

  
# class InstructorSubmissionPointAllViewList(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             batch_id = request.GET.get('batch_id')            
#             week_id = request.GET.get('week_id') 
#             ongoing_data = TaskSubmission.objects.filter(batch_id=batch_id, week=week_id, batch__completed=False).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             ).order_by("-id")
#             assigned_projects = BatchJoined.objects.filter(batch_id=batch_id).values(
#                 'student__user__first_name', 'student__user__last_name',
#                 'assign_topic__project_topic', 'assign_project__project_name'
#             )
#             topic_by_student = {f"{project['student__user__first_name']} {project['student__user__last_name']}": {
#                 'assigned_project': project.get('assign_project__project_name', None),
#                 'assigned_topic': project.get('assign_topic__project_topic', None),
#             } for project in assigned_projects}
            
#             ongoing_grouped_data = []
#             previous_grouped_data = []

#             for entry in ongoing_data:
#                 student_name = f"{entry['student__user__first_name']} {entry['student__user__last_name']}"
#                 assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
                
#                 file_path = entry['file']
#                 file_url = None
#                 if file_path:
#                     file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)

#                 entry_info = {
#                     "id": entry["id"],
#                     "batch_id": entry["batch_id"],
#                     "course_submission__submission_topic": entry["course_submission__submission_topic"],
#                     "student__user__first_name": entry["student__user__first_name"],
#                     "student__user__last_name": entry["student__user__last_name"],
#                     "week": entry["week"],
#                     "assigned_project": assigned_info['assigned_project'],
#                     "assigned_topic": assigned_info['assigned_topic'],
#                     "file":  file_url,
#                     "status": entry['status'],
#                     "created_at": entry["created_at"],
#                 }

#                 ongoing_grouped_data.append(entry_info)

#             previous_data = TaskSubmission.objects.filter(batch_id=batch_id, week=week_id, batch__completed=True).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             ).order_by("id")

#             for entry in previous_data:
#                 student_name = f"{entry['student__user__first_name']} {entry['student__user__last_name']}"
#                 assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
#                 file_path = entry['file']
#                 file_url = None
#                 if file_path:
#                     file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
#                 entry_info = {
#                     "id": entry["id"],
#                     "batch_id": entry["batch_id"],
#                     "course_submission__submission_topic": entry["course_submission__submission_topic"],
#                     "student__user__first_name": entry["student__user__first_name"],
#                     "student__user__last_name": entry["student__user__last_name"],
#                     "week": entry["week"],
#                     "assigned_project": assigned_info['assigned_project'],
#                     "assigned_topic": assigned_info['assigned_topic'],
#                     "file": file_url,
#                     "status": entry['status'],
#                     "created_at": entry["created_at"],
#                 }

#                 previous_grouped_data.append(entry_info)
    
#             return Response({"message":1,"ongoing_data": ongoing_grouped_data, "previous_data": previous_grouped_data}, status=status.HTTP_200_OK)  
#         except Exception as e:
#             return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

#####################
# Mentor can Show the Batch base on course id #RijuDjango #task 6
class InstructorOngoingPreviousBatchSelection(ListAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get('course_id')  
            inst_obj = Instructor.objects.get(user_id=user_id)   
            if course_id:
                ongoing_batches = Batch.objects.filter(instructor_id = inst_obj.id ,course_id = course_id, completed = False)
                previous_batches = Batch.objects.filter(instructor_id = inst_obj.id ,course_id = course_id, completed = True)
            else:
                ongoing_batches = Batch.objects.filter(instructor_id = inst_obj.id, completed = False)
                previous_batches = Batch.objects.filter(instructor_id = inst_obj.id, completed = True)
            data = {
                "ongoing_batches_ids": list(ongoing_batches.values("id")) if ongoing_batches.exists() else None,
                "previous_batches_ids": list(previous_batches.values("id")) if previous_batches.exists() else None,
            }
            return Response({"message": 1, "data": data}, status=status.HTTP_200_OK)   
        except Exception as e :
            return Response({"error":f"{e}"})   
        

######################
# Mentor can Show the Submission list (Batch wise) #RijuDjango #task 7
class InstructorSubmissionPointBatchDataViewList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            batch_id = request.GET.get('batch_id') 
            filter_id = request.GET.get('filter_id')
            if filter_id:
                main_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__instructor__user_id=request.user.id, project_topics_id = int(filter_id)).order_by("-id")
            else:
                # Filter the TaskSubmission objects based on batch_id and the instructor's user ID
                main_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__instructor__user_id=request.user.id).order_by("-id")
            
            # Serialize the main data
            serializer_main_data = TaskUploadSerializer(main_data, many=True).data
            
            # Get the batch and its related project topics
            get_batch = Batch.objects.filter(id=batch_id).first()
            
            if get_batch:
                topics = get_batch.project_topics.all()
                topic_list = []

                for topic in topics:
                    # Retrieve project names related to the topic
                    projects_list = list(topic.project_name.all().values_list("project_name", flat=True))
                    topic_list.append({"id":topic.id,"topic_name": topic.project_topic, "projects_list": projects_list})

                # Return the response with main data and topic list
                return Response({"message": 1, "main_data": serializer_main_data, "topic_list": topic_list}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

# class InstructorSubmissionPointBatchDataViewList(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             batch_id = request.GET.get('batch_id') 
#             filter = request.GET.get('batch_id')           
#             main_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__instructor__user_id = request.user.id).order_by("-id")
#             serializer_main_data = TaskUploadSerializer(main_data, many=True).data
#             get_batch = Batch.objects.filter(id=batch_id).first()
#             topics = get_batch.project_topics().all()
#             topic_list = []
#             for topic in topics:
#                 projects_list = list(topic.project_name.all().values_list("project_name", falt=True))
#                 topic_list.append({"topic_name":topic, "projects_list":projects_list})
#             return Response({"message": 1, "main_data": serializer_main_data, "topic":topic}, status=status.HTTP_200_OK)  
#         except Exception as e:
#             return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


######################
# Mentor can Show the Submission list(All) #RijuDjango #task 8
class InstructorSubmissionAllDataViewList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user  
            # course_id = request.GET.get('course_id')  
            # pre_sub_data = TaskSubmission.objects.filter(batch__instructor__user_id = user.id, batch__completed=True, batch__course_id = course_id).order_by("-id")       
            # ong_sub_data = TaskSubmission.objects.filter(batch__instructor__user_id = user.id, batch__completed=False, batch__course_id = course_id).order_by("-id")
            pre_sub_data = TaskSubmission.objects.filter(batch__instructor__user_id = user.id, batch__completed=True).order_by("-id")
            ong_sub_data = TaskSubmission.objects.filter(batch__instructor__user_id = user.id, batch__completed=False).order_by("-id")
            serializer_pre_sub_data = TaskUploadSerializer(pre_sub_data, many=True).data
            serializer_ong_sub_data = TaskUploadSerializer(ong_sub_data, many=True).data
            return Response({"message": 1, "previous_data": serializer_pre_sub_data, "ongoing_data":serializer_ong_sub_data}, status=status.HTTP_200_OK)  
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)



 
class InstructorSubmissionPointAllViewList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            batch_id = request.GET.get('batch_id')             
            ongoing_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__completed=False).order_by("-id")
            assigned_projects = BatchJoined.objects.filter(batch_id=batch_id).values(
                'student__user__first_name', 'student__user__last_name',
                'assign_topic__project_topic', 'assign_project__project_name'
            )
            topic_by_student = {f"{project['student__user__first_name']} {project['student__user__last_name']}": {
                'assigned_project': project.get('assign_project__project_name', None),
                'assigned_topic': project.get('assign_topic__project_topic', None),
            } for project in assigned_projects}

            serializer_ongoing_data = TaskUploadSerializer(ongoing_data, many=True).data

            ongoing_grouped_data = []
            for entry in serializer_ongoing_data:
                student_name = f"{entry['student_first_name']} {entry['student_last_name']}"
                assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
                entry_info = {
                    "assigned_project": assigned_info['assigned_project'],
                    "assigned_topic": assigned_info['assigned_topic'],
                    **entry
                }
                ongoing_grouped_data.append(entry_info)

            previous_data = TaskSubmission.objects.filter(batch_id=batch_id, batch__completed=True).order_by("id")

            serializer_previous_data = TaskUploadSerializer(previous_data, many=True).data

            previous_grouped_data = []
            for entry in serializer_previous_data:
                student_name = f"{entry['student_first_name']} {entry['student_last_name']}"
                assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
                entry_info = {
                    "assigned_project": assigned_info['assigned_project'],
                    "assigned_topic": assigned_info['assigned_topic'],
                    **entry
                }
                previous_grouped_data.append(entry_info)

            return Response({"message": 1, "ongoing_data": ongoing_grouped_data, "previous_data": previous_grouped_data}, status=status.HTTP_200_OK)  
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)



######################
# Mentor can Show the Submission list(All) #RijuDjango #task 10
class InstructorSubmissionTaskStatusChange(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            submission_data_list = request.data.get('submission_data', [])
            if submission_data_list:
                for submission_data in submission_data_list:
                    submission_id = submission_data.get('submission_id')
                    status = submission_data.get('status')
                    task_submission = TaskSubmission.objects.get(id=submission_id)
                    task_submission.status = status
                    task_submission.save()
                    
                return Response({'message': 'Status updated successfully'})
            else:
                return Response({"message":0})   
        except Exception as e:
            return Response({'error': str(e)})
        

# class SearchSubmissionOngoingTasks(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try:
#             user_id = request.user.id
#             search_name = request.GET.get('search_name')
#             inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
#             get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
#             batch_ids = [i["id"] for i in get_batch]
#             queryset = TaskSubmission.objects.filter(batch_id__in=batch_ids,batch__completed=False).order_by('-id')
#             searching_data = queryset.filter(Q(student__user__first_name__icontains=search_name) |Q(student__user__last_name__icontains=search_name) |
#                 Q(file__icontains=search_name) | 
#                 Q(course_submission__submission_topic__icontains=search_name)| Q(week__icontains=search_name)
#             ).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             )
#             if len(searching_data)==0:
#                 searching_data2 = queryset.filter(Q(week__icontains=search_name)).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             )
#                 return Response({"ongoing_data": searching_data2, "message": 1}, status=status.HTTP_200_OK)
#             return Response({"ongoing_data": searching_data, "message": 1}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class SearchSubmissionPreviousTasks(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try:
#             user_id = request.user.id
#             search_name = request.GET.get('search_name')
#             inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
#             get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
#             batch_ids = [i["id"] for i in get_batch]
#             queryset = TaskSubmission.objects.filter(batch_id__in=batch_ids,batch__completed=True).order_by('-id')
#             searching_data = queryset.filter(Q(student__user__first_name__icontains=search_name) |Q(student__user__last_name__icontains=search_name) |
#                 Q(file__icontains=search_name) | 
#                 Q(course_submission__submission_topic__icontains=search_name)| Q(week__icontains=search_name)
#             ).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             )
#             if len(searching_data)==0:
#                 searching_data2 = queryset.filter(Q(week__icontains=search_name)).values(
#                 "id", "batch_id", "student__user__first_name", "student__user__last_name", "week",
#                 "course_submission__submission_topic","file","status", "created_at"
#             )
#                 return Response({"previous_data": searching_data2, "message": 1}, status=status.HTTP_200_OK)
#             return Response({"previous_data": searching_data, "message": 1}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        



class SearchSubmissionOngoingTasks(APIView):   #06/02/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        try:
            user_id = request.user.id
            search_name = request.GET.get('search_name')
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            batch_ids = [i["id"] for i in get_batch]
            queryset = TaskSubmission.objects.filter(batch_id__in=batch_ids, batch__completed=False).order_by('-id')
            searching_data = queryset.filter(
                Q(student__user__first_name__icontains=search_name) |
                Q(student__user__last_name__icontains=search_name) |
                Q(file__icontains=search_name) |
                Q(project_topics__project_topic__icontains=search_name) |
                Q(week__icontains=search_name)
            )

            if len(searching_data) == 0:
                searching_data2 = queryset.filter(Q(week__icontains=search_name))
                serializer = TaskUploadSerializer(searching_data2, many=True)
                return Response({"ongoing_data": serializer.data, "message": 1}, status=status.HTTP_200_OK)

            serializer = TaskUploadSerializer(searching_data, many=True)
            
            assigned_projects = BatchJoined.objects.filter(batch_id__in=batch_ids).values(
                'student__user__first_name', 'student__user__last_name',
                'assign_topic__project_topic', 'assign_project__project_name'
            )
            
            topic_by_student = {f"{project['student__user__first_name']} {project['student__user__last_name']}": {
                'assigned_project': project.get('assign_project__project_name', None),
                'assigned_topic': project.get('assign_topic__project_topic', None),
            } for project in assigned_projects}
            
            serialized_data = []
            
            for task in serializer.data:
                student_name = f"{task['student_first_name']} {task['student_last_name']}"
                assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
                
                task['assigned_project'] = assigned_info['assigned_project']
                task['assigned_topic'] = assigned_info['assigned_topic']
                
                serialized_data.append(task)
            
            return Response({"ongoing_data": serialized_data, "message": 1}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchSubmissionPreviousTasks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        try:
            user_id = request.user.id
            search_name = request.GET.get('search_name')
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            batch_ids = [i["id"] for i in get_batch]
            queryset = TaskSubmission.objects.filter(batch_id__in=batch_ids, batch__completed=True).order_by('-id')
            searching_data = queryset.filter(
                Q(student__user__first_name__icontains=search_name) |
                Q(student__user__last_name__icontains=search_name) |
                Q(file__icontains=search_name) |
                Q(course_submission__submission_topic__icontains=search_name) |
                Q(week__icontains=search_name)
            )

            if len(searching_data) == 0:
                searching_data2 = queryset.filter(Q(week__icontains=search_name))
                serializer = TaskUploadSerializer(searching_data2, many=True)
                return Response({"previous_data": serializer.data, "message": 1}, status=status.HTTP_200_OK)

            serializer = TaskUploadSerializer(searching_data, many=True)
            
            assigned_projects = BatchJoined.objects.filter(batch_id__in=batch_ids).values(
                'student__user__first_name', 'student__user__last_name',
                'assign_topic__project_topic', 'assign_project__project_name'
            )
            
            topic_by_student = {f"{project['student__user__first_name']} {project['student__user__last_name']}": {
                'assigned_project': project.get('assign_project__project_name', None),
                'assigned_topic': project.get('assign_topic__project_topic', None),
            } for project in assigned_projects}
            
            serialized_data = []
            
            for task in serializer.data:
                student_name = f"{task['student_first_name']} {task['student_last_name']}"
                assigned_info = topic_by_student.get(student_name, {'assigned_project': None, 'assigned_topic': None})
                
                task['assigned_project'] = assigned_info['assigned_project']
                task['assigned_topic'] = assigned_info['assigned_topic']
                
                serialized_data.append(task)
            
            return Response({"previous_data": serialized_data, "message": 1}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetCourseSyllabusViewList(ListAPIView):  #31/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        try:
            course_id = request.GET.get('course_id') 
            week_topics = Syllabus.objects.filter(course_id=course_id).order_by("id")  
            if week_topics.exists():
                serializer = SyllabusSerializer(week_topics, many=True)
                return Response({"message": 1, "all_data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "course specific syllabus not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"{e}"})


class InstructorOngoingPreviousBatchComplitionList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id 
            course_id = request.GET.get("course_id")
            inst_obj = Instructor.objects.get(user_id=user_id)           
            ongoing_b_data = Batch.objects.filter(instructor_id = inst_obj.id ,course_id = course_id, completed=False,b_certificate=False).values(
                "id","course__name" ,"max_participants", "end_date" ).order_by("id")
            ongoing_grouped_data = []
            previous_grouped_data = []

            for entry in ongoing_b_data:
                check_req = BatchCompleteRequest.objects.filter(batch_id=entry["id"], instructor_id=inst_obj.id )

                entry_info = {
                    "batch_id": entry["id"],
                    "course__name": entry["course__name"],
                    "no_of_students": entry["max_participants"],
                    "end_date": entry["end_date"],
                    "completed_status": check_req.first().is_complete if check_req.exists() else "Request",
                    "b_certificate_status": check_req.first().is_certificate if check_req.exists() else "Request"
                }
                ongoing_grouped_data.append(entry_info)

            previous_b_data = Batch.objects.filter(instructor_id = inst_obj.id ,course_id = course_id,completed=True).values(
                "id","course__name" ,"max_participants", "end_date" ).order_by("id")

            for entry in previous_b_data:
                entry_info = {
                    "batch_id": entry["id"],
                    "course__name": entry["course__name"],
                    "no_of_students": entry["max_participants"],
                    "end_date": entry["end_date"],
                    "completed_status": "Completed",
                    "b_certificate_status": "Completed"
                }
                previous_grouped_data.append(entry_info)

            return Response({"message":1,"ongoing_data": ongoing_grouped_data, "previous_data": previous_grouped_data}, status=status.HTTP_200_OK)  
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class OngoingBatchCompleteRequestViewList(ListAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id  
            inst_id = Instructor.objects.filter(user_id=user_id).first().id 
            batch_id = request.GET.get("batch_id")
            ongoing_batches = Batch.objects.filter(
                instructor_id=inst_id, id=batch_id
            ).values("id", "course_id", "course__name", "completed", "b_certificate").order_by("id")

            for batch in ongoing_batches:
                check_req = BatchCompleteRequest.objects.filter(batch_id=batch["id"], instructor_id=inst_id)
                
                if check_req.exists():
                    batch["completed_status"] = check_req.first().is_complete
                    batch["b_certificate_status"] = check_req.first().is_certificate
                else:
                    batch["completed_status"] = "Request"
                    batch["b_certificate_status"] = "Request"

            return Response({"message": 1, "data": ongoing_batches}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"{e}"})

    def post(self, request):
        try:
            user_id = request.user.id  
            inst_id = Instructor.objects.filter(user_id=user_id).first().id 
            batch_id = request.POST.get("batch_id")
            is_complete = "pending"
            is_certificate = "pending"
            BatchCompleteRequest.objects.create(batch_id=batch_id,instructor_id=inst_id,is_complete=is_complete,is_certificate=is_certificate)
            return Response({"message":"Admin recived the request"}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})
        
           
class PreviousBatchCompleteRequestViewList(ListAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id  
            inst_id = Instructor.objects.filter(user_id=user_id).first().id 
            previous_batches = Batch.objects.filter(
                instructor_id=inst_id, completed=True,b_certificate=True
            ).values("id", "course_id", "course__name", "completed", "b_certificate").order_by("id")
            
            if previous_batches.exists():
                return Response({"message": 1, "data": previous_batches,"status":"Completed"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": 0,"data":"there is no previous batches!!"}, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            return Response({"error": f"{e}"})
        
        
################################### Mentor Teaching Section ################################################
    
def prc_week_first_questions(course_id, week_id):
    get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day").first()
    
    if get_q:
        topics = {"q_id":get_q.id,"title":get_q.ques_title,"slg":get_q.ques_title.replace(" ", "-")}
    else:
        topics = {"q_id":None,"title":None,"slg":None}
    return topics

class InstructorAllNotesWeekLock(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
            batch_ids = [i["id"] for i in get_batch]
            all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            week_conut = []
            for i in all_times :
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                    week_conut.append(i["week"])
            main_data = []
            for i in range(1,9) :
                if  week_conut.count(str(i)) >= 1 :
                    std_all_note = Note.objects.filter(course_id=course_id,week=i) 
                    if std_all_note.exists():
                        std_all_note = std_all_note.first()
                        file = f"{std_all_note.file.url}"
                        main_data.append({"topic":std_all_note.topic,"week":i,"file":file,"week_status":"unlock","condition":""})
                    else:
                        main_data.append({"topic":"","week":i,"file":"","week_status":"unlock","condition":"no notes at this moment"})
                else:
                    main_data.append({"topic":"","week":i,"file":"","week_status":"lock"})
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})       


# class InstructorTeachingPracticeWeekLock(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try :
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
#             get_batch = Batch.objects.filter(instructor_id__in=inst_id).values("id", "course_id")
#             batch_ids = [i["id"] for i in get_batch]
#             if not course_id :
#                 course_ids = [i["course_id"] for i in get_batch]
#                 queryset = Course.objects.filter(id__in=course_ids).values("id","name").order_by("name")
#                 course_id = queryset.first()["id"]
#                 course_name = queryset.first()["name"]
#             else:
#                 queryset = Course.objects.filter(id=course_id).values("id","name")
#                 course_id = queryset.first()["id"]
#                 course_name = queryset.first()["name"]

#             all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
#             current_datetime = datetime.now()
#             formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
#             week_conut = []
#             for i in all_times :
#                 if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
#                     week_conut.append(i["week"])
#             main_data = []
#             result = []
            
            
#             for i in range(1,9) :
#                 total_question = CompilerQuestion.objects.filter(practice_mock=False,week=str(i))
#                 complted_question = 0
#                 pre_week_complted_question = 0
#                 pre_week_total_question = CompilerQuestion.objects.filter(practice_mock=False,week=str(i-1))
#                 for k in total_question.values("id"):
#                     check_com = CompilerQuestionAtempt.objects.filter(instructor_id = inst_id[0], button_clicked = 'Submit', question__week = str(i), question__practice_mock=False, status=True,  question_id=int(k["id"])).values("id").count()
#                     if check_com >= 1:
#                         complted_question = complted_question + 1
#                 for l in pre_week_total_question.values("id"):
#                     check__com = CompilerQuestionAtempt.objects.filter(instructor_id = inst_id[0], button_clicked = 'Submit', question__week = str(i-1), question__practice_mock=False, status=True,  question_id=int(k["id"])).values("id").count()
#                     if check__com >= 1:
#                         pre_week_complted_question = pre_week_complted_question + 1
#                 if  week_conut.count(str(i)) >= 1:
#                     if i == 1:
#                         if len(total_question) != 0:
#                             main_data.append({
#                                 "week": i,
#                                 "name": course_name,
#                                 "img": "/images/Practice/week2.svg",
#                                 "status": True,
#                                 "completed": complted_question,
#                                 "total": len(total_question),
#                                 "isDisabled": False,
#                                 "condition":""
#                                 })
#                         else:
#                             main_data.append({
#                                 "week": i,
#                                 "name": course_name,
#                                 "img": "/images/Practice/week2.svg",
#                                 "status": True,
#                                 "completed": complted_question,
#                                 "total": len(total_question),
#                                 "isDisabled": False,
#                                 "condition":"Reach out to support team to unlock this"
#                                 })
#                     else:
#                         if len(total_question) != 0:
                            
#                             main_data.append({
#                                 "week": i,
#                                 "name": course_name,
#                                 "img": "/images/Practice/week2.svg",
#                                 "status": True,
#                                 "completed": complted_question,
#                                 "total": len(total_question),
#                                 "isDisabled": False,
#                                 "condition":""
#                                 })
#                         else:
#                             main_data.append({
#                                 "week": i,
#                                 "name": course_name,
#                                 "img": "/images/Practice/week2.svg",
#                                 "status": True,
#                                 "completed": complted_question,
#                                 "total": len(total_question),
#                                 "isDisabled": False,
#                                 "condition":"Reach out to support team to unlock this"
#                                 })
#                 else:
#                     main_data.append({
#                         "week": i,
#                         "name": course_name,
#                         "img": "/images/Practice/week2.svg",
#                         "status": False,
#                         "completed": complted_question,
#                         "total": len(total_question),
#                         "isDisabled": True,
#                         })
#             for i in range(1, len(main_data)+1):
#                 prc_week_first = prc_week_first_questions(course_id, str(i))
#                 week_data = main_data[i-1]
#                 week_data.update(prc_week_first)
#                 result.append(week_data)
#             return Response({"main_data":result})
#         except Exception as e :
#             return Response({"error":f"{e}"})     


class InstructorTeachingPracticeWeekLock(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # try:
            user_id = request.user.id
            batch_id = request.GET.get("batch_id") 
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_batch = Batch.objects.filter(instructor_id__in=inst_id, id=batch_id).values("id", "course_id")
            
            if not get_batch:
                return Response({"error": "Invalid batch_id"})
                
            course_id = get_batch[0]["course_id"]
            course_info = Course.objects.filter(id=course_id).first()
            if not course_info:
                return Response({"error": "Invalid course_id"})
                
            course_name = course_info.name

            all_times = TimeTable.objects.filter(batch__id=batch_id).values("week", "start_date", "start_time", "batch__course__name").order_by("id")
            current_datetime = datetime.now()
            if course_info.course_duration:
                course_duration = int(course_info.course_duration) + 1
            else:
                course_duration = 8+1
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            week_count = []

            for i in all_times:
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime:
                    week_count.append(i["week"])

            main_data = []
            result = []

            for i in range(1, course_duration):
                total_question = CompilerQuestion.objects.filter(practice_mock=False, week=str(i), course_id=course_id,disable= False)
                completed_question = 0
                pre_week_completed_question = 0
                pre_week_total_question = CompilerQuestion.objects.filter(practice_mock=False, week=str(i - 1), course_id=course_id,disable= False)

                for k in total_question.values("id"):
                    check_com = CompilerQuestionAtempt.objects.filter(
                        instructor_id=inst_id[0], button_clicked='Submit', question__week=str(i),
                        question__practice_mock=False, status=True, question_id=int(k["id"])
                    ).values("id").count()

                    if check_com >= 1:
                        completed_question += 1

                for l in pre_week_total_question.values("id"):
                    check__com = CompilerQuestionAtempt.objects.filter(
                        instructor_id=inst_id[0], button_clicked='Submit', question__week=str(i - 1),
                        question__practice_mock=False, status=True, question_id=int(l["id"])
                    ).values("id").count()

                    if check__com >= 1:
                        pre_week_completed_question += 1

                if week_count.count(str(i)) >= 1:
                    condition = ""
                    if i == 1:
                        if len(total_question) != 0:
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": completed_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition": condition
                            })
                        else:
                            condition = "Reach out to support team to unlock this"
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": completed_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition": condition
                            })
                    else:
                        if len(total_question) != 0:
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": completed_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition": condition
                            })
                        else:
                            condition = "Reach out to support team to unlock this"
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": completed_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition": condition
                            })
                else:
                    main_data.append({
                        "week": i,
                        "name": course_name,
                        "img": "/images/Practice/week2.svg",
                        "status": False,
                        "completed": completed_question,
                        "total": len(total_question),
                        "isDisabled": True,
                    })

            for i in range(1, len(main_data) + 1):
                prc_week_first = prc_week_first_questions(course_id, str(i))
                week_data = main_data[i - 1]
                week_data.update(prc_week_first)
                result.append(week_data)
            return Response({"main_data": result})
        # except Exception as e:
        #     return Response({"error": f"{e}"})
        


class InstructorAllPracticeQuestionsAll(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            week_id = request.GET.get("week_id")
            get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day","question_number")
            for_day1 = get_q.filter(day=1)
            main_data = []
            topics = []
            for i in range(1,4):
                for_day1 = get_q.filter(day=i)

                if for_day1.exists():
                    for j in for_day1 :
                        q_status= compiler_question_all_practice(user_id,j.id,course_id)
                        slg = j.ques_title.replace(" ", "-")
                        topics.append({"q_id":j.id,"question_number":j.question_number,"title":j.ques_title,"slg":slg, "isOnGoing":True, "que_status":q_status})

                    main_data.append({"id":i,"day":i,"name":f"day{i}","active":True,"topics":topics})
                else:
                    main_data.append({"id":i,"day":i,"name":f"day{i}","active":False,"topics":[]})
                topics = []
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})
        

class InstructorAllPracticeQuestion(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            main_data = []
            user_id = request.user.id
            q_id = request.GET.get("q_id")
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            # get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False).order_by("question_number")
            get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False,disable= False).order_by("day","question_number")

            #next_questions
            get_c_q = CompilerQuestion.objects.filter(id=q_id, practice_mock=False,disable= False).values("week", "course_id")
            if len(get_c_q) != 0:
                week_id = int(get_c_q[0]["week"])
                course_id = int(get_c_q[0]["course_id"])
                # get_q_all = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False).order_by("day")
                get_q_all = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day","question_number")
                get_all_q_id = []
                loop_count = 4
                for k in range(1, loop_count):
                    for_day = get_q_all.filter(day=k)
                    for t in for_day:
                        get_all_q_id.append(t.id)
                # next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
                next_q_id = get_next_index(get_all_q_id, int(q_id))
            #end
            get_course = CompilerQuestion.objects.get(id=q_id, practice_mock=False,disable= False)
            get_course.course.name if get_course.course else None
            socialSitList = []
            examples = []
            test_case_list = []

            for i in get_q :
                if i.google :
                    socialSitList.append("Google") 
                if i.amazon :
                    socialSitList.append("Amazon")
                if i.microsoft :
                    socialSitList.append("Microsoft")
                if i.meta :
                    socialSitList.append("Facebook")
                if i.linkedin :
                    socialSitList.append("Linkedin")
                if i.uber :
                    socialSitList.append("Uber")
                if i.adobe :
                    socialSitList.append("Adobe")
                if i.cred :
                    socialSitList.append("Cred")
                    
                #testcases
                test_cases = i.test_cases
                if test_cases == {}:
                    test_casess = []
                else:
                    test_casess = test_cases["data"]
                # print(test_casess)
                # if i.test_case is not None and len(i.test_case) != 0:
                #     if i.test_case != "null":
                #         try:
                #             test_case_txt = str(i.test_case).split("\r\n\r\n\r\n")
                #             t_counter = 0
                #             for case_ in test_case_txt:
                #                 t_counter += 1
                #                 caa = str(case_).replace("\r", "").replace("\n", "")
                #                 caaa = caa.split("||")
                #                 case_titel = caaa[0]
                                
                #                 # Split the parts and handle index out of range
                #                 test_case_parts = caaa[1].split("=")
                #                 test_case_titel = test_case_parts[0] + "=" if len(test_case_parts) > 1 else None
                #                 test_case_value = test_case_parts[1] if len(test_case_parts) > 1 else None

                #                 target_parts = caaa[2].split("=")
                #                 target_titel = target_parts[0] + "=" if len(target_parts) > 1 else None
                #                 target_value = target_parts[1] if len(target_parts) > 1 else None

                #                 expected_parts = caaa[3].split("=")
                #                 expected_titel = expected_parts[0] + "=" if len(expected_parts) > 1 else None
                #                 expected_value = expected_parts[1] if len(expected_parts) > 1 else None

                #                 test_case_list.append({
                #                     "id": t_counter,
                #                     "case_titel": case_titel,
                #                     "test_case_titel": test_case_titel,
                #                     "test_case_value": test_case_value,
                #                     "target_titel": target_titel,
                #                     "target_value": target_value,
                #                     "expected_titel": expected_titel,
                #                     "expected_value": expected_value
                #                 })
                #         except:
                #             test_case_list.append({
                #                     "info":"Please follow The Process"
                #                 })
                #examples
                try:
                    exampless = str(i.examples)
                    lines = exampless.strip().split('\n')
                    exampless_list = []
                    for line in lines:
                        line = line.strip()  # Remove leading and trailing spaces
                        if line.startswith("Sample Eg") and "||" in line:
                            exampless_list.append(line)
                    counter = 0
                    for j in exampless_list:
                        ex = str(j).replace("\r","").replace("\n","")
                        exx = ex.split("||")
                        title = exx[0]
                        input = exx[1]
                        output = exx[2]
                        explanation = exx[3]
                        examples.append({"id":counter+1,"title":title,"input":input,"output":output,"explanation":explanation})
                        counter +=1
                except:
                    pass
                # constrains
                constrain =[]    
                if i.constraints is not None and len(i.constraints) != 0:
                    try:
                        cons_txt = str(i.constraints).split("\r\n\r\n\r\n")
                        con_counter = 0
                        for con in cons_txt:
                            con_counter += 1
                            conss = str(con).replace("\r", "").replace("\n", "")
                            nw_cons = conss.split("||")
                            cons_title = nw_cons[0]
                            cons_value = nw_cons[1]
                            constrain.append({"constrain_title":cons_title,"constrain_value":cons_value})
                    except:
                        constrain.append({
                                    "info":"Please follow The Process"
                                })         
                # video solutions
                all_videos =[]    
                if i.video_solutions is not None and len(i.video_solutions) != 0:
                    try:
                        vids = str(i.video_solutions).split("\r\n\r\n\r\n")
                        vid_counter = 0
                        for v in vids:
                            vid_counter += 1
                            vidd = str(v).replace("\r", "").replace("\n", "")
                            nw_vids = vidd.split("||")
                            vid_language = nw_vids[0]
                            vid_url = nw_vids[1]
                            all_videos.append({"video_title":vid_language,"video_links":vid_url})     
                    except:
                        all_videos.append({
                                    "info":"Please follow The Process"
                                }) 
                approch_values = compiler_question_approches_practice(q_id) 
                prob_pic = i.prob_pic.url if i.prob_pic else "null" 
                const_pic = i.const_pic.url if i.const_pic else "null" 
                #add
                pre_code_list = SavePracticeCode.objects.filter(question_id=int(q_id), instructor_id= (inst_id[0])).values("code_text") 
                if len(pre_code_list) == 0:
                    pre_code = None
                else:
                    pre_code = pre_code_list[0]["code_text"]
                
                previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=q_id,instructor_id=inst_id[0],question__practice_mock=False, submited=True, button_clicked="Submit").order_by("-id").values("id","status","load_template__compiler","student_ans","practic_time","code_response", "code_response_status")
                for ti in previous_attempts:
                    if ti["code_response"] is not None:
                        res = json.loads(ti["code_response"])
                        ti["timer"] = res['items'][0]['result']["time"]
                        ti["memory"] = res['items'][0]['result']["memory"]
                        # ti["status"] = res['items'][0]['result']["status"]["name"]
                        # print(ti["code_response_status"])
                        # print(dict(ti["code_response_status"]))
                        ti.update(ti["code_response_status"])
                        del ti["code_response"]
                        del ti["code_response_status"]
                # print(previous_attempts)
                
                main_data.append({"next_q_id":next_q_id,"course_name":get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
                                "prob_pic":prob_pic,"examples":examples,"constrains":constrain,"const_pic":const_pic,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_casess ,"approch_values":approch_values, "pre_code":pre_code, "previous_attempts":previous_attempts})
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})    


class InstructorPracticeQuestionSearchTitel(ListAPIView):  
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, q_titel):
        try :
            main_data = []
            q_titel = q_titel.replace("-", " ")
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=False,disable= False).order_by("day","question_number")
            # get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=False,disable= False)
            
            get_c_q = CompilerQuestion.objects.filter(ques_title=q_titel, practice_mock=False,disable= False).values("week", "course_id", "id")
            if len(get_c_q) != 0:
                week_id = int(get_c_q[0]["week"])
                course_id = int(get_c_q[0]["course_id"])
                # get_q_all = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day")
                get_q_all = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day","question_number")
                get_all_q_id = []
                loop_count = 4
                for k in range(1, loop_count):
                    for_day = get_q_all.filter(day=k)
                    for t in for_day:
                        get_all_q_id.append(t.id)     
                q_id = get_c_q[0]["id"]
                # next_q_id = get_next_index(get_all_q_id.copy(), int(q_id))
                next_q_id = get_next_index(get_all_q_id, int(q_id))
                next_q_titel = CompilerQuestion.objects.filter(id=next_q_id, practice_mock=False,disable= False).values("ques_title")[0]["ques_title"]
            #end
            get_course = CompilerQuestion.objects.get(ques_title=q_titel, practice_mock=False,disable= False)
            get_course.course.name if get_course.course else None
            socialSitList = []
            examples = []
            # test_case_list = []

            for i in get_q :
                if i.google :
                    socialSitList.append("Google") 
                if i.amazon :
                    socialSitList.append("Amazon")
                if i.microsoft :
                    socialSitList.append("Microsoft")
                if i.meta :
                    socialSitList.append("Facebook")
                if i.linkedin :
                    socialSitList.append("Linkedin")
                if i.uber :
                    socialSitList.append("Uber")
                if i.adobe :
                    socialSitList.append("Adobe")
                if i.cred :
                    socialSitList.append("Cred")
                test_cases = i.test_cases
                if test_cases == {}:
                    test_casess = []
                else:
                    test_casess = test_cases["data"]
                # print(test_casess)
                #testcases
                # if i.test_case is not None and len(i.test_case) != 0:
                #     if i.test_case != "null":
                #         try:
                #             test_case_txt = str(i.test_case).split("\r\n\r\n\r\n")
                #             t_counter = 0
                #             for case_ in test_case_txt:
                #                 t_counter += 1
                #                 caa = str(case_).replace("\r", "").replace("\n", "")
                #                 caaa = caa.split("||")
                #                 case_titel = caaa[0]
                                
                #                 # Split the parts and handle index out of range
                #                 test_case_parts = caaa[1].split("=")
                #                 test_case_titel = test_case_parts[0] + "=" if len(test_case_parts) > 1 else None
                #                 test_case_value = test_case_parts[1] if len(test_case_parts) > 1 else None

                #                 target_parts = caaa[2].split("=")
                #                 target_titel = target_parts[0] + "=" if len(target_parts) > 1 else None
                #                 target_value = target_parts[1] if len(target_parts) > 1 else None

                #                 expected_parts = caaa[3].split("=")
                #                 expected_titel = expected_parts[0] + "=" if len(expected_parts) > 1 else None
                #                 expected_value = expected_parts[1] if len(expected_parts) > 1 else None

                #                 test_case_list.append({
                #                     "id": t_counter,
                #                     "case_titel": case_titel,
                #                     "test_case_titel": test_case_titel,
                #                     "test_case_value": test_case_value,
                #                     "target_titel": target_titel,
                #                     "target_value": target_value,
                #                     "expected_titel": expected_titel,
                #                     "expected_value": expected_value
                #                 })
                #         except:
                #             test_case_list.append({
                #                     "info":"Please follow The Process"
                #                 })
                #examples
                try:
                    exampless = str(i.examples)
                    lines = exampless.strip().split('\n')
                    exampless_list = []
                    for line in lines:
                        line = line.strip()  # Remove leading and trailing spaces
                        if line.startswith("Sample Eg") and "||" in line:
                            exampless_list.append(line)
                    counter = 0
                    for j in exampless_list:
                        ex = str(j).replace("\r","").replace("\n","")
                        exx = ex.split("||")
                        title = exx[0]
                        input = exx[1]
                        output = exx[2]
                        explanation = exx[3]
                        examples.append({"id":counter+1,"title":title,"input":input,"output":output,"explanation":explanation})
                        counter +=1
                except:
                    pass
                # constrains
                constrain =[]    
                if i.constraints is not None and len(i.constraints) != 0:
                    try:
                        cons_txt = str(i.constraints).split("\r\n\r\n\r\n")
                        con_counter = 0
                        for con in cons_txt:
                            con_counter += 1
                            conss = str(con).replace("\r", "").replace("\n", "")
                            nw_cons = conss.split("||")
                            cons_title = nw_cons[0]
                            cons_value = nw_cons[1]
                            constrain.append({"constrain_title":cons_title,"constrain_value":cons_value})
                    except:
                        constrain.append({
                                    "info":"Please follow The Process"
                                })         
                # video solutions
                all_videos =[]    
                if i.video_solutions is not None and len(i.video_solutions) != 0:
                    try:
                        vids = str(i.video_solutions).split("\r\n\r\n\r\n")
                        vid_counter = 0
                        for v in vids:
                            vid_counter += 1
                            vidd = str(v).replace("\r", "").replace("\n", "")
                            nw_vids = vidd.split("||")
                            vid_language = nw_vids[0]
                            vid_url = nw_vids[1]
                            all_videos.append({"video_title":vid_language,"video_links":vid_url})     
                    except:
                        all_videos.append({
                                    "info":"Please follow The Process"
                                }) 
                approch_values = compiler_question_approches_practice(q_id) 
                prob_pic = i.prob_pic.url if i.prob_pic else "null" 
                const_pic = i.const_pic.url if i.const_pic else "null" 
                #add
                pre_code_list = SavePracticeCode.objects.filter(question_id=int(q_id), instructor_id= (inst_id[0])).values("code_text") 
                if len(pre_code_list) == 0:
                    pre_code = None
                else:
                    pre_code = pre_code_list[0]["code_text"]
                q_id = get_q.first().id
                previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=q_id,instructor_id=inst_id[0],question__practice_mock=False, submited=True, button_clicked="Submit").order_by("-id").values("id","status","load_template__compiler","student_ans","practic_time","code_response", "code_response_status")
                for ti in previous_attempts:
                    if ti["code_response"] is not None:
                        res = json.loads(ti["code_response"])
                        ti["timer"] = res['items'][0]['result']["time"]
                        ti["memory"] = res['items'][0]['result']["memory"]
                        # ti["status"] = res['items'][0]['result']["status"]["name"]
                        # print(ti["code_response_status"])
                        # print(dict(ti["code_response_status"]))
                        ti.update(ti["code_response_status"])
                        del ti["code_response"]
                        del ti["code_response_status"]
                main_data.append({"previous_attempts":previous_attempts,"next_q_id":next_q_id,"next_q_titel":next_q_titel.replace(" ", "-"),"course_name":get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
                                "prob_pic":prob_pic,"examples":examples,"constrains":constrain,"const_pic":const_pic,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_casess ,"approch_values":approch_values, "pre_code":pre_code})
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})  
        

class InstructorAllPracticeLoadTemplate(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        try:
            main_data = []
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            question_id = request.GET.get("question_id")
            all_temp = CompilerQuestionLoadTemplate.objects.filter(question_id=question_id).order_by("compiler").values("id","compiler","load_template")
            for i in all_temp:
                data_id = i["id"]
                compilers = str(i["compiler"]).split("||")
                compilers_name = compilers[0]
                compilers_id = compilers[1]
                have_code = SavePracticeCode.objects.filter(compliler_id = data_id, instructor_id = inst_id[0], question_id = question_id).values("code_text")
                if have_code.exists():
                    pre_code = have_code[0]["code_text"]
                else:
                    pre_code = i["load_template"]
                main_data.append({"save_code_id":data_id, "compiler":i["compiler"],"compilers_name":compilers_name,"compilers_id":compilers_id,"load_template":pre_code})
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})


class InstructorPracticeSaveCode(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            user_id = request.user.id
            inst = Instructor.objects.filter(user_id=user_id).first()
            q_id = request.data.get("q_id")
            code = request.data.get("code")
            compliler_id = request.data.get("compliler_id")
            user_save_code = SavePracticeCode.objects.filter(instructor_id = inst.id, question_id=q_id, compliler_id=int(compliler_id))
            if user_save_code.exists():
                user_save_code.update(code_text=code)
            else:
                user_save_code_craete = SavePracticeCode(instructor_id = inst.id, question_id=q_id, compliler_id=int(compliler_id), code_text=code)
                user_save_code_craete.save()
            return Response({"status":True,"compliler_id":int(compliler_id)})
        except Exception as e :
            return Response({"error":f"{e}"})     


class InstructorPracticeDeleteCode(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            user_id = request.user.id
            # std = Student.objects.filter(user_id=user_id).first()
            inst = Instructor.objects.filter(user_id=user_id).first()
            q_id = request.data.get("q_id")
            compliler_id = request.data.get("compliler_id")
            SavePracticeCode.objects.filter(instructor_id = inst.id, question_id=q_id, compliler_id=int(compliler_id)).delete()
            return Response({"status":True,"message":"save code is deleted"})
        except Exception as e :
            return Response({"error":f"{e}"})


class InstructorAllPracticeQuestionSubmission(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            main_data = []
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            if len(inst_id) > 0 :
                inst_id = inst_id[0]
            else:
                inst_id = ""
            q_id = request.data.get("q_id")
            source_code = request.data.get("source_code")
            compiler = request.data.get("compiler")
            compiler_id = request.data.get("compiler_id")
            problem_id = request.data.get("problem_id")
            coding_language = request.data.get("coding_language")
            button_clicked = request.data.get("button_clicked")
            get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False,disable= False)
            if get_q.exists() and inst_id !="" and source_code and compiler_id and problem_id and coding_language and button_clicked :
                get_q = get_q.first()
                check_temp = CompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
                if check_temp.exists():
                    get_temp = check_temp.first()
                    load_template_id = get_temp.id
                    coding_language = coding_language
                else:
                    return Response({"main_data":main_data})
                attepmt_number = CompilerQuestionAtempt.objects.filter(question_id=q_id,instructor_id=inst_id,load_template_id=load_template_id,
                                                                    coding_language=coding_language,button_clicked="Run")
                if attepmt_number.exists():
                    get_attepmt_number = len(attepmt_number)
                    get_attepmt_temp = attepmt_number.first()
                    get_attepmt_temp.attepmt_number = int(get_attepmt_number) + 1
                    get_attepmt_temp.student_ans = source_code
                    get_attepmt_temp.button_clicked = button_clicked
                    if button_clicked == "Submit":
                        get_attepmt_temp.submited = True
                    else:
                        get_attepmt_temp.submited = False
                    get_attepmt_temp.save()
                    main_data = get_attepmt_temp.id
                else:
                    get_attepmt_number = 1
                    get_attepmt_temp = CompilerQuestionAtempt(question_id=q_id,instructor_id=inst_id,attepmt_number=get_attepmt_number,load_template_id=load_template_id,
                                        coding_language=coding_language,student_ans=source_code,button_clicked=button_clicked)
                    if button_clicked == "Submit":
                        get_attepmt_temp.submited = True
                    get_attepmt_temp.save()
                    main_data = get_attepmt_temp.id
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})

      
def accept_api_output(res_ids):
    url3 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/output?access_token=3d839c6883687fa7e1db43995c8d60c2"
    response3 = requests.get(url3)
    parsed_json = response3.text
    data_list = str(parsed_json).split("\n")
    dataset_index = data_list.index('DATASET NUMBER: 0')
    dataset_values = []
    for value in data_list[dataset_index + 1:]:
        if not value:
            break
        dataset_values.append(value)
    dataset_values = [value for value in dataset_values]
    return dataset_values

def compilation_error_data(res_ids):
    url4 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/cmpinfo?access_token=3d839c6883687fa7e1db43995c8d60c2"
    response4 = requests.get(url4)
    return response4.text

def wrong_answer_data(res_ids):
    url3 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/output?access_token=3d839c6883687fa7e1db43995c8d60c2"
    response3 = requests.get(url3)
    parsed_json = response3.text
    data_list = str(parsed_json).split("\n")
    dataset_index = data_list.index('DATASET NUMBER: 0')
    dataset_values = []
    for value in data_list[dataset_index + 1:]:
        if not value:
            break
        dataset_values.append(value)
    dataset_values = [value for value in dataset_values]
    return dataset_values

def runtime_error_data(res_ids):
    url5 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/error?access_token=3d839c6883687fa7e1db43995c8d60c2"
    response5 = requests.get(url5)
    return response5.text


# class InstructorAllPracticeQuestionSubmissionResponce(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
#             if len(inst_id) > 0 :
#                 inst_id = inst_id[0]
#             else:
#                 inst_id = ""
#             api_result = []
#             main_data_id = request.GET.get("main_data_id")
#             check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
#             print(check_ans)
#             if check_ans.exists():
#                 get_ans = check_ans.first()
#                 instructor_id = get_ans.instructor.id
#                 ques_id = get_ans.question.id
#                 source_code = get_ans.student_ans
#                 compiler = str(get_ans.load_template.compiler).split("||")
#                 compiler_id = compiler[1]
#                 problem_id = get_ans.question.prob_id
#                 url1 = 'https://31c7692b.problems.sphere-engine.com/api/v4/submissions?access_token=3d839c6883687fa7e1db43995c8d60c2'
#                 headers = {'Content-Type': 'application/json'}
#                 triple_quoted_string = '''{}'''.format(source_code)
#                 payload_for_post = {
#                     "compilerId": compiler_id,
#                     "source": triple_quoted_string,
#                     "problemId": problem_id
#                 }
#                 response = requests.post(url1, headers=headers, json=payload_for_post)
#                 data = json.loads(response.text)
#                 get_ans.code_response = data
#                 print(response.status_code)
#                 if response.status_code == 201 :
#                     get_sphere_engine_problems_id = data['id']
#                     time.sleep(3)
#                     url2 = f'https://31c7692b.problems.sphere-engine.com/api/v4/submissions?ids={get_sphere_engine_problems_id}&access_token=3d839c6883687fa7e1db43995c8d60c2'
#                     response2 = requests.get(url2)
#                     main_data = json.loads(response2.text)
#                     get_ans.code_response = response2.text
#                     get_ans.submissions_id = get_sphere_engine_problems_id
#                     # if code accepted
#                     res_ids = main_data['items'][0]['id']
#                     if main_data['items'][0]['result']['status']['name'] == "accepted" :
#                         accept_data = accept_api_output(res_ids)
#                         res_da = {
#                             "status":"accepted",
#                             "data":accept_data    
#                             }
#                         get_ans.code_response_status = res_da
#                         api_result.append(res_da)
                        
#                         get_ans.status = True
#                         get_ans.save()
#                     # if code compilation error
#                     elif main_data['items'][0]['result']['status']['name'] == "compilation error" :
#                         error_data = compilation_error_data(res_ids)
#                         res_da = {
#                             "status":"compilation error",
#                             "data":error_data    
#                             }
#                         get_ans.code_response_status = res_da
#                         api_result.append(res_da)
#                         get_ans.status = False
#                         get_ans.save()
#                     # if code wrong answer
#                     elif main_data['items'][0]['result']['status']['name'] == "wrong answer" :
#                         output_data = wrong_answer_data(res_ids)
#                         res_da = {
#                             "status":"wrong answer",
#                             "data":output_data    
#                             }
#                         get_ans.code_response_status = res_da
#                         api_result.append(res_da)
#                         get_ans.status = False
#                         get_ans.save()
#                     else:
#                         error_data = runtime_error_data(res_ids)
#                         get_ans.code_response_status = error_data
#                         api_result.append({
#                             "status":"runtime error",
#                             "data":error_data    
#                             })
#                         get_ans.status = False
#                         get_ans.save()
#                     previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=ques_id,instructor_id=instructor_id,question__practice_mock=False, submited=True, button_clicked="Submit").order_by("-id").values("id","status","load_template__compiler","student_ans","practic_time","code_response", "code_response_status")
#             for ti in previous_attempts:
#                 if ti["code_response"] is not None:
#                     res = json.loads(ti["code_response"])
#                     ti["timer"] = res['items'][0]['result']["time"]
#                     ti["memory"] = res['items'][0]['result']["memory"]
#                     # ti["status"] = res['items'][0]['result']["status"]["name"]
#                     print(ti["code_response_status"])
#                     print(dict(ti["code_response_status"]))
#                     ti.update(ti["code_response_status"])
#                     del ti["code_response"]
#                     del ti["code_response_status"]
#             print(previous_attempts)  
#             return Response({"main_data":main_data,"source_code":"source_code","previous_attempts":previous_attempts, "api_result":api_result})
#         except Exception as e :
#             return Response({"error":f"{e}"})  


# Function to fetch the batch submission result
def get_batch_result(batch_tokens):
    url = "https://judge0-ce.p.rapidapi.com/submissions/batch"
    querystring = {
        "tokens": batch_tokens,
        "base64_encoded": "true",
        "fields": "*"
    }
    headers = {
        "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
        "x-rapidapi-key": RAPID_API_KEY
    }
    response = requests.get(url, headers=headers, params=querystring)    
    if response.status_code == 200:
        data = response.json()       
        for submission in data["submissions"]:
            if 'stdout' in submission and submission['stdout']:
                submission['stdout'] = base64.b64decode(submission['stdout']).decode('utf-8')
            if 'stderr' in submission and submission['stderr']:
                submission['stderr'] = base64.b64decode(submission['stderr']).decode('utf-8')
            if 'compile_output' in submission and submission['compile_output']:
                submission['compile_output'] = base64.b64decode(submission['compile_output']).decode('utf-8')
        return data
    
    return []


class InstructorAllPracticeQuestionSubmissionResponce(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            main_data = []
            user_id = request.user.id
            inst_id = [i["id"] for i in Instructor.objects.filter(user_id=user_id).values("id")]
            if len(inst_id) > 0 :
                inst_id = inst_id[0]
            else:
                inst_id = ""
            api_result = []
            main_data_id = request.GET.get("main_data_id")
            check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
            if check_ans.exists():
                get_ans = check_ans.first()
                instructor_id = get_ans.instructor.id
                ques_id = get_ans.question.id
                ques_name = get_ans.question.ques_title
                prob_id = get_ans.question.prob_id
                source_code = get_ans.student_ans
                compiler = get_ans.load_template.compiler.split("||")
              
                triple_quoted_string = '''{}'''.format(source_code)
                compiler_id = compiler[1]
                
                
                if isinstance(get_ans.question.test_cases_to_pass, str):
                    test_cases = json.loads(get_ans.question.test_cases_to_pass)['data']
                else:
                    test_cases = get_ans.question.test_cases_to_pass['data']

                url = 'https://judge0-ce.p.rapidapi.com/submissions/batch'
                headers = {
                    'Content-Type': 'application/json',
                    'x-rapidapi-host': "judge0-ce.p.rapidapi.com",
                    'x-rapidapi-key': RAPID_API_KEY  # Replace with your RapidAPI key
                }

                submissions = []

                def format_stdin(inputs, output):
                    stdin = None
                    expected_output = None
                    for i in inputs:
                        if not stdin:
                            stdin = str(i["value"])
                        else:
                            stdin = stdin + f" {i["value"]}"
                    for j in output:
                        if not expected_output:
                            expected_output = f"{j["value"]}\n"
                        
                    return stdin, expected_output
                
                for test_case in test_cases:
                    inputs = test_case["input"]
                    
                    # num_tests = len(inputs) // len(inputs)  # Assuming each test case has two numbers
                    # stdin = f"{num_tests}\n" + "\n".join([str(input['value']) for input in inputs])
                    stdin, expected_output = format_stdin(inputs, test_case["expected"])
                    # expected_output = "\n".join([str(exp['value']) for exp in test_case["expected"]]) + "\n"
                    print(stdin)
                    print(expected_output)
                    
                    submissions.append({
                        "language_id": compiler_id,
                        "source_code": triple_quoted_string,
                        "stdin": stdin,
                        "expected_output": expected_output,
                        "time_limit": 5,
                        "memory_limit": 128000
                    })

                payload_for_post = {
                    "submissions": submissions
                }

                response = requests.post(url, headers=headers, json=payload_for_post)
                
                if response.status_code == 201:
                    data = response.json()
                    get_ans.code_response = data

                    if isinstance(data, dict) and 'submissions' in data:
                        batch_tokens = ','.join([sub['token'] for sub in data['submissions']])
                    elif isinstance(data, list):
                        batch_tokens = ','.join([sub['token'] for sub in data])
                    else:
                        raise ValueError("Unexpected data structure in API response")

                    time.sleep(3)
                    batch_result = get_batch_result(batch_tokens)
                    print(batch_result)
                    for i, result in enumerate(batch_result['submissions']):   
                        test_case = test_cases[i]
                        res_da = {
                            "number": i,
                            "status": {
                                "code": result['status']['id'],
                                "name": result['status']['description']
                            },
                            "score": 0,
                            "time": result.get('time', 0),
                            "memory": result.get('memory', 0),
                            "signal": 0,
                            "signal_desc": ""
                        }
                        api_result.append(res_da)

                    passed_tests = sum(1 for res in api_result if res['status']['code'] == 3)  # Assuming 'accepted' has status code 3
                    total_tests = len(api_result)
                
                    main_data_item = {
                        'id': get_ans.id,
                        'executing': False,
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S +00:00'),
                        'compiler': {
                            'id': compiler_id,
                            'name': compiler,
                            'version': {
                                'id': None,
                                'name': None
                            }
                        },
                        'problem': {
                            'id': ques_id,
                            'code': prob_id,
                            'name': ques_name,
                            'uri': ''
                        },
                        'result': {
                            'score': (passed_tests / total_tests) * 100,
                            'status': {
                                'code': 15 if passed_tests == total_tests else 11,
                                'name': 'Accepted' if passed_tests == total_tests else 'Wrong Answer'
                                # 'name': next((r['status']['description'] for r in batch_result["submissions"] if r['status']['description']), None)
                            },
                            'time': sum([float(r.get('time', 0)) if r.get('time') is not None else 0 for r in batch_result["submissions"]]),
                            'memory': max([int(r.get('memory', 0)) if r.get('memory') is not None else 0 for r in batch_result["submissions"]] or [0]),
                            'signal': 0,
                            'signal_desc': '',
                            'testcases': api_result
                        },
                        'uri': ''
                    }
                    main_data.append(main_data_item)

                    get_ans.code_response = json.dumps({"items": main_data})
                    get_ans.submissions_id = None
                    result_data = []
                    error_data = None
                    for r in batch_result["submissions"]:
                        if r.get("stdout") is not None:
                            data = r.get("stdout").strip()
                            result_data.append(data)
                        elif r.get("stderr") is not None:
                            error_data = r.get("stderr").strip()
                            break
                        elif r.get("compile_output") is not None:
                            error_data = r.get("compile_output").strip()
                            break
                    get_ans.code_response_status = {"status":main_data[0]['result']['status']["name"], "data":result_data if len(result_data) > 0 else error_data }
                    get_ans.status = True if main_data[0]['result']['status']['code'] == 15 else False
                    get_ans.save()

                    previous_attempts = CompilerQuestionAtempt.objects.filter(
                        question_id=ques_id,
                        instructor_id=instructor_id,
                        question__practice_mock=False,
                        submited=True,
                        button_clicked="Submit"
                    ).order_by("-id").values(
                        "id", "status", "load_template__compiler", "student_ans", "practic_time", "code_response", "code_response_status"
                    )
                    for ti in previous_attempts:
                        if ti["code_response"] is not None:
                            res = json.loads(ti["code_response"])
                            ti["timer"] = res['items'][0]['result']["time"]
                            ti["memory"] = res['items'][0]['result']["memory"]
                            ti.update(ti["code_response_status"])
                            del ti["code_response"]
                            del ti["code_response_status"]
                    
                    return Response({
                        "main_data": {
                            "items": main_data
                        },
                        "source_code": source_code,
                        "previous_attempts": previous_attempts if previous_attempts else [],
                        "api_result": get_ans.code_response_status
                    })
            else:
                return Response({"error": "Invalid main_data_id"})
        except Exception as e:
            return Response({"error": f"{e}"})

