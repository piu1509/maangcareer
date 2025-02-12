from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import random,json
from django.http import JsonResponse
from collections import OrderedDict
from django_filters.rest_framework import DjangoFilterBackend
import time
from datetime import datetime, timezone
import base64
from django.db.models import Sum 
from freeCourseManagement.helpers import save_pdf_to_model, send_email_for_certificate, check_certificate_status, notify_user
from courseManagement.helpers import send_email_for_emi_reminder
from django.conf import settings
# Create your views here.
RAPID_API_KEY = settings.RAPID_API_KEY 

class FreeCourseListView(APIView):
    """
    A simple APIView for listing Courses.
    """
    def get(self, request):
        queryset = FreeCourse.objects.filter(archive=False).order_by('serial_no')
        serializer = FreeCourseListSerializer(queryset, many=True)
        return Response(serializer.data)


class AuthenticatedFreeCourseList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        user = request.user
        queryset = FreeCourse.objects.filter(archive=False).order_by('serial_no')
        joined_courses = list(FreeCourseJoinee.objects.filter(student__user=user).values_list("course_id", flat=True))
        serializer = FreeCourseListSerializer(queryset, many=True)
        data = serializer.data
        for item in data:
            if item["id"] in joined_courses:
                item["is_registered"] = True
            else:
                item["is_registered"] = False
        return Response(data)


class FreeCourseDetailView(APIView):
    """
    A simple APIView for retrieving a specific Course.
    """
    def get(self, request, pk):
        queryset = FreeCourse.objects.all()
        course = get_object_or_404(queryset, pk=pk)
        serializer = FreeCourseSerializer(course, context={'request': request})
        return Response(serializer.data)


class StudentFreeCourseRegister(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_id = request.user.id
            check_student = Student.objects.filter(user_id=user_id)
            course_id = request.data.get("course_id")
            check_course = FreeCourse.objects.filter(id=course_id) 
            if check_course.exists() and check_student.exists():
                get_course = check_course.first()
                get_student = check_student.first() 
                if FreeCourseJoinee.objects.filter(course=get_course, student=get_student).exists():
                    return Response({"status":status.HTTP_400_BAD_REQUEST, "message": "You have already enrolled for this course."})

                FreeCourseJoinee.objects.create(course=get_course, student=get_student)                
                return Response({"status":status.HTTP_201_CREATED, "message": "Welcome aboard! Your course enrollment was successful."})
            
            return Response({"status":status.HTTP_404_NOT_FOUND, "message": "Student or Course not found."})        
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error": f"{e}"})


class StudentFreeCourseList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            check_student = Student.objects.filter(user_id=user_id)
            if check_student.exists():
                get_student = check_student.first()
                student_free_course = FreeCourseJoinee.objects.filter(student=get_student).order_by('course__serial_no')
                courses = [joinee.course for joinee in student_free_course]
                serializer = FreeCourseListSerializer(courses, many=True)
                data = serializer.data
                return Response({"status":status.HTTP_200_OK, "data":data})
            return Response({"status":status.HTTP_404_NOT_FOUND, "message": "Student not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error": f"{e}"})
        
#working
class StudentVerficationFreeCourse(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id 
            std_obj = Student.objects.filter(user_id=user_id)
            if std_obj.exists():            
                std_id = std_obj.first().id
                check_free_course = FreeCourseJoinee.objects.filter(student_id=std_id).order_by('course__serial_no')
                name = std_obj.first().user.first_name
                if len(check_free_course) == 0:
                    response_data = {
                        "name": name,
                        "role": "Student",
                        "free_course_status": False,
                        "message": "You don't have any free course."
                    }
                else: 
                    count = len(check_free_course)           
                    response_data = {
                        "name": name,
                        "role": "Student",
                        "login_status": True,
                        "message": f"You have {count} free course."
                    }
                return Response({"status":status.HTTP_200_OK, "data":response_data, "message": "Status fetched succesfully."})
            return Response({"status":status.HTTP_404_NOT_FOUND, "data":[], "message": "Student or Course not found."}) 
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error": f"{e}"})


class CourseSyllabusList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user
            course_id = request.GET.get('course_id')
            check_course = FreeCourse.objects.filter(id=course_id)
            if check_course:
                get_course = check_course.first()
                student_id = Student.objects.filter(user=user).first().id
                
                course_syllabus = FreeCourseSyllabus.objects.filter(course=get_course).order_by('number')
                serializer = FreeCourseSyllabusSerializer(course_syllabus, many=True)
                
                result = []                
                for data in serializer.data:

                    if data.get("number") == 1:
                        data = dict(data)
                        attempt_syll_one = QuizQuestionAttempts.objects.filter(student__user=user, course_id=course_id, syllabus_id=data.get("id"))
                        questions = FreeCourseQuizQuestion.objects.filter(course_section_question__course_section__id = data.get("id"))
                        if questions.exists():
                            if attempt_syll_one:
                                num_attempt = attempt_syll_one.last().attempt_number
                                # print(data)
                                if num_attempt >= data['syllabus_topics'][0]['section']['max_attempts']:
                                    data["is_lock"] = True
                                    data["is_disable"] = False
                                    data["message"] = "You don't have anymore attempt left."
                                else:
                                    data["is_lock"] = False
                                    data["is_disable"] = False
                                    data["message"] = None
                                data["score"] = max(list(attempt_syll_one.values_list("attempt_score", flat=True)))
                                data["attempt"] = num_attempt 
                                data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts']                             
                            else:   
                                data["is_lock"] = False
                                data["is_disable"] = False
                                data["message"] = None
                                data["score"] = 0
                                data["attempt"] = 0
                                data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts']
                        else:
                            data["is_lock"] = True
                            data["is_disable"] = False
                            data["score"] = 0
                            data["attempt"] = 0
                            data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts']
                            data["message"] = "Reachout to suport team"
                        data["number"] = 2
                        result.append(data)  
                    else:
                        #pre section result pre_max_score, pre_max_attempt
                        pre_syllabus = result[data.get("number") - 2]
                        pre_syllabus_id = pre_syllabus.get("id")
                        pre_syllabus_max_score = pre_syllabus['syllabus_topics'][0]['section']['max_score']                       
                        rec_questions = FreeCourseQuizQuestion.objects.filter(course_section_question__course_section__id = data.get("id"))
                        pre_attempt = QuizQuestionAttempts.objects.filter(student__user=user, course_id=course_id, syllabus_id=pre_syllabus_id)
                        if pre_attempt:
                            pre_att_score_list = list(pre_attempt.values_list("attempt_score", flat=True))
                            pre_att_max_score = max(pre_att_score_list)
                            rec_syllabus_id = data.get("id")
                            rec_syllabus_max_attempt = data['syllabus_topics'][0]['section']['max_attempts']
                            recent_attempt = QuizQuestionAttempts.objects.filter(student__user=user, course_id=course_id, syllabus_id=rec_syllabus_id)
                    
                            if pre_att_max_score >= pre_syllabus_max_score:
                                if rec_questions.exists():
                                    if recent_attempt:
                                        rec_att_num_attempt = recent_attempt.last().attempt_number
                                        if rec_att_num_attempt >= rec_syllabus_max_attempt:
                                            data["is_lock"] = True
                                            data["is_disable"] = True
                                            data["message"] = "You don't have anymore attempt left."                                        
                                        else:
                                            data["is_lock"] = False
                                            data["is_disable"] = False
                                            data["message"] = None 
                                        data["score"] = max(list(recent_attempt.values_list("attempt_score", flat=True)))
                                        data["attempt"] = rec_att_num_attempt 
                                        data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts']  
                                                                 
                                    else:
                                        data["is_lock"] = False
                                        data["is_disable"] = False
                                        data["score"] = 0
                                        data["attempt"] = 0
                                        data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts'] 
                                        data["message"] = None 
                                         
                                else:
                                    data["is_lock"] = True
                                    data["is_disable"] = False
                                    data["score"] = 0
                                    data["attempt"] = 0
                                    data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts'] 
                                    data["message"] = "Reachout to suport team ......" 
                                                          
                            else:
                                data["is_lock"] = True
                                data["is_disable"] = True
                                data["score"] = 0
                                data["attempt"] = 0
                                data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts'] 
                                data["message"] = None   
                                                        
                        else:
                            data["is_lock"] = True
                            data["is_disable"] = True
                            data["score"] = 0
                            data["attempt"] = 0
                            data["maximum_attempts"] = data['syllabus_topics'][0]['section']['max_attempts'] 
                            data["message"] = None
                            
                        result.append(data)
                          
                return Response({"status":status.HTTP_200_OK, "data":result, "message":"Syllabus fetched succesfully."})
            return Response({"status":status.HTTP_404_NOT_FOUND, "data":[], "message":"Course not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error": f"{e}"})


class SyllabusQuestionsList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            syllabus_id = request.GET.get('syllabus_id')
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
            if check_syllabus:
                get_syllabus = check_syllabus.first()
                course_section_questions = FreeCourseQuizQuestion.objects.filter(course_section_question__course_section=get_syllabus)
                serializer = QuizQuestionSerializer(course_section_questions, many=True)
                data = serializer.data
                random.shuffle(data)
                print(data)
                final_data = data[0:get_syllabus.number_of_questions+1]
                return Response({"status":status.HTTP_200_OK, "time":get_syllabus.time_duration, "data":final_data, "message":"Questions fetched succesfully."})
            else:
                return Response({"status":status.HTTP_404_NOT_FOUND, "time": None, "data":[], "message":"Syllabus not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "time": None, "error": f"{e}"})
        

class QuizQuestionAttempt(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_id = request.user.id
            course_id = request.data.get("course_id")
            syllabus_id = request.data.get("syllabus_id")
            attempt_answer = request.data.get("attempt_answer")
            # right_answers = request.data.get("right_answers")
            # wrong_answers = request.data.get("wrong_answers")
            check_student = Student.objects.filter(user_id=user_id)
            check_course = FreeCourse.objects.filter(id=course_id)
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
            if check_student and check_course and check_syllabus:
                get_student = check_student.first()
                get_course = check_course.first()
                get_syllabus = check_syllabus.first()
                check_attempt = QuizQuestionAttempts.objects.filter(student= get_student, course=get_course, syllabus=get_syllabus)
                if check_attempt:
                    attempt_number = check_attempt.last().attempt_number + 1
                else:
                    attempt_number = 1
                attempt_answer = json.loads(attempt_answer)
                quiz_questions = list(FreeCourseQuizQuestion.objects.filter(course_section_question__course_section=get_syllabus).values('id','answer'))
                right_answers = 0
                wrong_answers = 0
                for question in quiz_questions:
                    for index in attempt_answer:
                        if index["question_id"] == question["id"]:
                            if index["answer"] == question["answer"]:
                                right_answers += 1
                            else:
                                wrong_answers +=1
                
                attempt_score =  (int(right_answers) / len(quiz_questions) ) * 100
                is_passed = True if int(attempt_score) >= int(get_syllabus.max_score) else False
                attempt = QuizQuestionAttempts.objects.create(student= get_student, course=get_course, syllabus=get_syllabus,
                                                              attempt_number=attempt_number, right_answers=right_answers, 
                                                              wrong_answers=wrong_answers, attempt_answer=attempt_answer, 
                                                              attempt_score=attempt_score, is_passed=is_passed)
                
                # Notify the student if next syllabus quiz is unlocked
                syllabus_max_quiz_score = get_syllabus.max_score
                if attempt_score >= syllabus_max_quiz_score and not (get_course.section_number == get_syllabus.number):
                    title = f'Next Quiz Unlock'
                    current_date = datetime.now().strftime("%d-%m-%Y")
                    message = f"Your {get_course.name}'s Syllabus-{int(get_syllabus.number) + 1} quiz test is unlocked.\nDate : {current_date}"
                    notify_user(user_id, title, message)

                if get_course.section_number == get_syllabus.number:
                    get_syll_quiz_att_passed = QuizQuestionAttempts.objects.filter(student=get_student, course=get_course, syllabus=get_syllabus, is_passed=True)
                    if get_syll_quiz_att_passed:
                        certificate_status = check_certificate_status(get_course.id, get_student.id)
                        print(certificate_status)
                        if certificate_status == True:
                            joined_student = FreeCourseJoinee.objects.filter(course=get_course, student=get_student).first()
                            if joined_student and not joined_student.is_certificate:
                                joined_student.is_completed = True
                                joined_student.is_certificate = True
                                joined_student.save()

                                save_pdf_to_model(get_student.id, get_course.id, request)
                                site_url = "https://www.maangcareers.com/free/certificates"
                                course_name = get_course.name
                                # subject = 'Course Completion Certificate'
                                # message = f'You have successfully completed your {get_course.name} course. Please click on the link to download your certificate.'
                                send_email_for_certificate(site_url, get_student.user.email, course_name)

                                # Notify the student if certificate is unlocked                                
                                title = f'Certificate Unlocked'
                                current_date = datetime.now().strftime("%d-%m-%Y")
                                message = f"Your {get_course.name} is complete. Please download your certificate from the Certificates section.\nDate : {current_date}"
                                notify_user(user_id, title, message)
    
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass

                data = {"attempt_number":attempt.attempt_number,
                        "attempts_left":(int(get_syllabus.max_attempts) - int(attempt.attempt_number)),
                        "right_answers":attempt.right_answers,
                        "wrong_answers": attempt.wrong_answers,
                        "score": attempt.attempt_score,
                        "status":attempt.is_passed,
                        "max_score":get_syllabus.max_score,
                        "total_questions":attempt.right_answers + attempt.wrong_answers,
                        "total_attempts":get_syllabus.max_attempts
                        }
                return Response({"status":status.HTTP_200_OK, "data":data, "message":"Attempt saved succesfully."})
            return Response({"status":status.HTTP_404_NOT_FOUND, "data":[], "message":"Student or Course or Syllabus not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "data":[], "error": f"{e}"})


class PracticeQuestionLockStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user
            course_id = request.GET.get('course_id')
            check_course = FreeCourse.objects.filter(id=course_id)
            if check_course:
                get_course = check_course.first()
                course_syllabus = FreeCourseSyllabus.objects.filter(course=get_course).order_by('number')
                serializer = SyllabusLockSerializer(course_syllabus, many=True)
                
                result = []                
                for data in serializer.data:

                    if data.get("number") == 1:
                        data = dict(data)
                        attempt_syll_one = FreeCourseCompilerQuestionAttempt.objects.filter(student__user=user, course_id=course_id, syllabus_id=data.get("id"), question__practice_mock=False, status=True).values('student_id', 'question_id').distinct()
                        questions = FreeCourseCompilerQuestion.objects.filter(course_section_id = data.get("id"), practice_mock=False,disable=False)
                        if questions.exists():
                            
                            data["is_lock"] = False
                            data["is_disable"] = False
                            data["right_answer"] = attempt_syll_one.count() 
                            data["total_questions"] = questions.count()                       
                            data["message"] = None
                        else:
                            data["is_lock"] = True
                            data["is_disable"] = True
                            data["right_answer"] = 0 
                            data["total_questions"] = 0                            
                            data["message"] = "Reachout to suport team"
                        result.append(data)  
                    else:
                       
                        pre_syllabus = result[data.get("number") - 2]
                        pre_syllabus_id = pre_syllabus.get("id")                     
                        rec_questions = FreeCourseCompilerQuestion.objects.filter(course_section_id = data.get("id"), practice_mock=False,disable=False)
                        
                        rec_right_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student__user=user, course_id=course_id, syllabus_id=data.get("id"), question__practice_mock=False, status=True).values('student_id', 'question_id').distinct()
                        pre_right_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student__user=user, course_id=course_id, syllabus_id=pre_syllabus_id, question__practice_mock=False, status=True).values('student_id', 'question_id').distinct()
                        pre_syll_ques = FreeCourseCompilerQuestion.objects.filter(course_section_id=pre_syllabus_id, practice_mock=False,disable=False)
                        if pre_right_attempt:                                                 
                            pre_practice_score = (pre_right_attempt.count()/pre_syll_ques.count()) * 100                            
                            if pre_practice_score >= pre_syllabus.get("max_score_practice"):
                                if rec_questions.exists():                                                           
                                  
                                    data["is_lock"] = False
                                    data["is_disable"] = False
                                    data["right_answer"] = rec_right_attempt.count() 
                                    data["total_questions"] = rec_questions.count() 
                                    data["message"] = None   
                                else:
                                    data["is_lock"] = True
                                    data["is_disable"] = False
                                    data["right_answer"] = 0 
                                    data["total_questions"] = rec_questions.count()
                                    data["message"] = "Reachout to suport team ......"                           
                            else:
                                data["is_lock"] = True
                                data["is_disable"] = True
                                data["right_answer"] = 0
                                data["total_questions"] = rec_questions.count()
                                data["message"] = None                             
                        else:
                            data["is_lock"] = True
                            data["is_disable"] = True
                            data["right_answer"] = 0
                            data["total_questions"] = rec_questions.count()
                            data["message"] = None
                        result.append(data)
                          
                return Response({"status":status.HTTP_200_OK, "data":result, "message":"Syllabus fetched succesfully."})
            return Response({"status":status.HTTP_404_NOT_FOUND, "data":[], "message":"Course not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error": f"{e}"})
      


class PracticeCompilerQuestionList(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,)   
    filter_backends = (DjangoFilterBackend,)
    
    def get(self, request):
        try:
            syllabus_id = request.GET.get("syllabus_id")
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
            if check_syllabus:
                get_syllabus = check_syllabus.first()
                queryset = FreeCourseCompilerQuestion.objects.filter(course_section=get_syllabus, practice_mock=False, disable=False).select_related('topic').order_by('id')

                topic_questions = {}
                for question in queryset:
                    topic_title = question.topic.title
                    if topic_title not in topic_questions:
                        topic_questions[topic_title] = []
                    
                    topic_questions[topic_title].append(question)
                
                response_data = [{'topic': topic, 'questions': questions} for topic, questions in topic_questions.items()]
                
                serializer = TopicWithQuestionsSerializer(response_data, many=True)
                data = serializer.data
                for item in data:
                    for question in item["questions"]:
                        is_done = FreeCourseCompilerQuestionAttempt.objects.filter(question_id=question["id"], student__user=request.user, status=True).exists()
                        question["is_done"] = is_done              

                return Response({"status": status.HTTP_200_OK, "data": data, "message": "Questions fetched successfully."})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "data": [], "message": "Syllabus not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "error": str(e)})

#changed
class PracticeCompilerQuestionLoadTemplate(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        try:
            user = request.user
            check_student = Student.objects.filter(user=user)
            if check_student:
                get_student = check_student.first()
                question_id = request.GET.get("question_id")
                check_temp = FreeCourseCompilerQuestionLoadTemplate.objects.filter(question_id=question_id)
                if check_temp:   
                    
                    serializer = CompilerQuestionLoadTemplateSerializer(check_temp, many=True)
                    for temp in serializer.data:
                        template_id = temp.get("id")
                        check_saved_code = SavePracticeCompilerQuestionCode.objects.filter(student = get_student, template_id=template_id)  
                        if check_saved_code.exists():
                            temp["load_template"] = check_saved_code.first().code_text
                    return Response({"status": status.HTTP_200_OK,"main_data":serializer.data})
                else:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "main_data":[], "message":"Template not found."})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "main_data":[], "message": "Student not found."})
        except Exception as e :
            return Response({"status": status.HTTP_400_BAD_REQUEST, "error":f"{e}"})

#changed
class PracticeCompilerQuestionSaveCode(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            user = request.user
            std = Student.objects.filter(user_id=user).first()
            template_id = request.data.get("template_id")
            code = request.data.get("code")
            
            check_saved_code = SavePracticeCompilerQuestionCode.objects.filter(student_id = std.id, template_id=template_id)
            
            if check_saved_code.exists():
                saved_code = check_saved_code.first()
                saved_code.code_text = code
                saved_code.save()
            else:
                saved_code = SavePracticeCompilerQuestionCode(student_id = std.id, template_id=template_id, code_text=code)
                saved_code.save()
            compiler_id = saved_code.template.compiler.split("||")[1]

            return Response({"status":True,"compliler_id":int(compiler_id)})
        except Exception as e :
            return Response({"error":f"{e}"})

#changed
class PracticeCompilerQuestionDeleteCode(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request) :
        try :
            user = request.user
            std = Student.objects.filter(user_id=user).first()
            template_id = request.data.get("template_id")
            SavePracticeCompilerQuestionCode.objects.filter(student_id=std.id, template_id=template_id).delete()
            return Response({"status":status.HTTP_204_NO_CONTENT,"message":"Saved code has been deleted"})
        except Exception as e :
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error":f"{e}"})


class PracticeQuestionAttempt(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,)  

    def post(self, request):
        main_data = []
        try:
            q_id = request.data.get("q_id")
            course_id = request.data.get("course_id")
            syllabus_id = request.data.get("syllabus_id")
            source_code = request.data.get("source_code")
            compiler = request.data.get("compiler")
            button_clicked = request.data.get("button_clicked")            
            user = request.user
            check_student = Student.objects.filter(user=user)
            check_question = FreeCourseCompilerQuestion.objects.filter(id=q_id, practice_mock=False, disable=False)
            check_course = FreeCourse.objects.filter(id=course_id)
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
           
            if check_student and check_question and check_course and check_syllabus:
                student = check_student.first()
                question = check_question.first()
                check_compiler_tem = FreeCourseCompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
                if check_compiler_tem:
                    get_template = check_compiler_tem.first()
                    coding_language = get_template.compiler
                else:
                    return Response({"main_data":main_data})
                check_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student=student, question=question, course=check_course.first(),
                                                                                syllabus=check_syllabus.first(), load_template=get_template,
                                                                                coding_language=coding_language, button_clicked="Run")
                if check_attempt:
                    attempt_number = check_attempt.last().attepmt_number
                    get_attempt = check_attempt.first()
                    get_attempt.attepmt_number = attempt_number + 1
                    get_attempt.student_ans = source_code
                    get_attempt.button_clicked = button_clicked
                    if button_clicked == "Submit":
                        get_attempt.submitted = True
                    else:
                        get_attempt.submitted = False
                    get_attempt.save()
                else:
                    attepmt_number = 1
                    get_attempt = FreeCourseCompilerQuestionAttempt.objects.create(student=student, question=question, course=check_course.first(),
                                                                                syllabus=check_syllabus.first(), load_template=get_template,
                                                                                coding_language=coding_language, student_ans=source_code,
                                                                                attepmt_number=attepmt_number, button_clicked=button_clicked)
                    if button_clicked == "Submit":
                        get_attempt.submitted = True
                        get_attempt.save()
                main_data = get_attempt.id
                return Response({"status": status.HTTP_200_OK, "main_data":main_data, "message": "Attempt saved successfully."})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "main_data":main_data, "message": "Invalid request."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "main_data":main_data, "error": str(e)})


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


class PracticeQuestionAttemptResponse(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,) 

    def get(self, request):
        try:
            main_data = []
            user = request.user
            check_student = Student.objects.filter(user=user)
            if check_student:
                api_result = []
                main_data_id = request.GET.get("main_data_id")
                check_ans = FreeCourseCompilerQuestionAttempt.objects.filter(id=main_data_id)
                if check_ans.exists():
                    get_ans = check_ans.first()
                    student_id = get_ans.student.id
                    ques_id = get_ans.question.id
                    ques_name = get_ans.question.ques_title
                    source_code = get_ans.student_ans
                    compiler = get_ans.load_template.compiler.split("||")
                
                    triple_quoted_string = '''{}'''.format(source_code)
                    compiler_id = compiler[1]
                    
                    
                    if isinstance(get_ans.question.test_cases, str):
                        test_cases = json.loads(get_ans.question.test_cases)['data']
                    else:
                        test_cases = get_ans.question.test_cases['data']

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
                                'code': None,
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
                        get_ans.score = 100 if main_data[0]['result']['status']['code'] == 15 else 0 
                        get_ans.save()

                        # Notify the student if next syllabus practice is unlocked.
                        course = get_ans.course
                        syllabus = get_ans.syllabus
                        syllabus_max_practice_score = syllabus.max_score_practice
                        total_right_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student__user=user, course_id=course.id, syllabus_id=syllabus.id, question__practice_mock=False, status=True).values('student_id', 'question_id').distinct()
                        total_syll_ques = FreeCourseCompilerQuestion.objects.filter(course_section_id=syllabus.id, practice_mock=False,disable=False)
                        avg_practice_score = (total_right_attempt.count()/total_syll_ques.count()) * 100 
                        if avg_practice_score >= syllabus_max_practice_score and not (course.section_number == syllabus.number):
                            title = f'Next Practice Unlock'
                            current_date = datetime.now().strftime("%d-%m-%Y")
                            message = f"Your {course.name}'s Syllabus-{int(syllabus.number) + 1} practice is unlocked.\nDate : {current_date}"
                            notify_user(user.id, title, message)

                        previous_attempts = FreeCourseCompilerQuestionAttempt.objects.filter(
                            question_id=ques_id,
                            student_id=student_id,
                            question__practice_mock=False,
                            submitted=True,
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
            else:
                return Response({"error": "Student not found."})
        except Exception as e:
            return Response({"error": f"{e}"})


class MockQuestionLockStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user
            course_id = request.GET.get('course_id')
            check_course = FreeCourse.objects.filter(id=course_id)
            if check_course:
                get_course = check_course.first()
                course_syllabus = FreeCourseSyllabus.objects.filter(course=get_course).order_by('number')
                serializer = SyllabusLockStatusSerializer(course_syllabus, many=True)
                
                result = []                
                for data in serializer.data:

                    if data.get("number") == 1:
                        data = dict(data)
                        attempt_syll_one = MockCompilerQuestionResult.objects.filter(student__user=user, course_id=course_id, course_section_id=data.get("id"))
                        questions = FreeCourseCompilerQuestion.objects.filter(course_section_id=data.get("id"), practice_mock=True, disable=False)
                        if questions.exists():
                            if attempt_syll_one:
                                num_attempt = attempt_syll_one.last().attempt_number
                                # print(data)
                                if num_attempt >= data['max_attempts_mock']:
                                    data["is_lock"] = True
                                    data["is_disable"] = False
                                    data["message"] = "You don't have anymore attempt left."
                                else:
                                    data["is_lock"] = False
                                    data["is_disable"] = False
                                    data["message"] = None
                                data["score"] = max(list(attempt_syll_one.values_list("score", flat=True)))
                                data["attempt"] = num_attempt 
                                data["maximum_attempts"] = data['max_attempts_mock']                             
                            else:   
                                data["is_lock"] = False
                                data["is_disable"] = False
                                data["message"] = None
                                data["score"] = 0
                                data["attempt"] = 0
                                data["maximum_attempts"] = data['max_attempts_mock']
                        else:
                            data["is_lock"] = True
                            data["is_disable"] = False
                            data["score"] = 0
                            data["attempt"] = 0
                            data["maximum_attempts"] = data['max_attempts_mock']
                            data["message"] = "Reachout to suport team"
                        result.append(data)  
                    else:
                        #pre section result pre_max_score, pre_max_attempt
                        pre_syllabus = result[data.get("number") - 2]
                        pre_syllabus_id = pre_syllabus.get("id")
                        pre_syllabus_max_score = pre_syllabus['max_score_mock']                       
                        rec_questions = FreeCourseCompilerQuestion.objects.filter(course_section_id = data.get("id"), practice_mock=True,disable=False)
                        pre_attempt = MockCompilerQuestionResult.objects.filter(student__user=user, course_id=course_id, course_section_id=pre_syllabus_id)
                        if pre_attempt:
                            pre_att_score_list = list(pre_attempt.values_list("score", flat=True))
                            pre_att_max_score = max(pre_att_score_list)
                            rec_syllabus_id = data.get("id")
                            rec_syllabus_max_attempt = data['max_attempts_mock']
                            recent_attempt = MockCompilerQuestionResult.objects.filter(student__user=user, course_id=course_id, course_section_id=rec_syllabus_id)
                    
                            if pre_att_max_score >= pre_syllabus_max_score:
                                if rec_questions.exists():
                                    if recent_attempt:
                                        rec_att_num_attempt = recent_attempt.last().attempt_number
                                        if rec_att_num_attempt >= rec_syllabus_max_attempt:
                                            data["is_lock"] = True
                                            data["is_disable"] = True
                                            data["message"] = "You don't have anymore attempt left."                                        
                                        else:
                                            data["is_lock"] = False
                                            data["is_disable"] = False
                                            data["message"] = None 
                                        data["score"] = max(list(recent_attempt.values_list("score", flat=True)))
                                        data["attempt"] = rec_att_num_attempt 
                                        data["maximum_attempts"] = data['max_attempts_mock']                               
                                    else:
                                        data["is_lock"] = False
                                        data["is_disable"] = False
                                        data["score"] = 0
                                        data["attempt"] = 0
                                        data["maximum_attempts"] = data['max_attempts_mock'] 
                                        data["message"] = None   
                                else:
                                    data["is_lock"] = True
                                    data["is_disable"] = False
                                    data["score"] = 0
                                    data["attempt"] = 0
                                    data["maximum_attempts"] = data['max_attempts_mock'] 
                                    data["message"] = "Reachout to suport team ......"                           
                            else:
                                data["is_lock"] = True
                                data["is_disable"] = True
                                data["score"] = 0
                                data["attempt"] = 0
                                data["maximum_attempts"] = data['max_attempts_mock'] 
                                data["message"] = None                             
                        else:
                            data["is_lock"] = True
                            data["is_disable"] = True
                            data["score"] = 0
                            data["attempt"] = 0
                            data["maximum_attempts"] = data['max_attempts_mock'] 
                            data["message"] = None
                        result.append(data)
                          
                return Response({"status":status.HTTP_200_OK, "data":result, "message":"Syllabus fetched succesfully."})
            return Response({"status":status.HTTP_404_NOT_FOUND, "data":[], "message":"Course not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "error": f"{e}"})


class MockCompilerQuestionList(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,)   
    filter_backends = (DjangoFilterBackend,)
    
    def get(self, request):
        try:
            syllabus_id = request.GET.get("syllabus_id")
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
            if check_syllabus:
                get_syllabus = check_syllabus.first()
                queryset = FreeCourseCompilerQuestion.objects.filter(course_section=get_syllabus, practice_mock=True, disable=False).select_related('topic').order_by('id')
                print(queryset)
                topic_questions = {}
                for question in queryset:
                    topic_title = question.topic.title
                    if topic_title not in topic_questions:
                        topic_questions[topic_title] = []
                    topic_questions[topic_title].append(question)                
                response_data = [{'topic': topic, 'questions': questions} for topic, questions in topic_questions.items()]
                serializer = TopicWithQuestionsSerializer(response_data, many=True)
                data = serializer.data
                for item in data:
                    for question in item["questions"]:
                        is_done = False
                        attempt = FreeCourseCompilerQuestionAttempt.objects.filter(question_id=question["id"], student__user=request.user)
                        if attempt.exists():
                            is_done = attempt.last().status
                            question["is_done"] = is_done               

                return Response({"status": status.HTTP_200_OK, "time": get_syllabus.time_duration_mock, "data": data, "message": "Questions fetched successfully."})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "time": None, "data": [], "message": "Syllabus not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "time": None, "error": str(e)}) 
        

class MockQuestionAttempt(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,)  

    def post(self, request):
        main_data = []
        try:
            q_id = request.data.get("q_id")
            course_id = request.data.get("course_id")
            syllabus_id = request.data.get("syllabus_id")
            source_code = request.data.get("source_code")
            compiler = request.data.get("compiler")
            button_clicked = request.data.get("button_clicked")            
            user = request.user
            check_student = Student.objects.filter(user=user)
            check_question = FreeCourseCompilerQuestion.objects.filter(id=q_id, practice_mock=True, disable=False)
            check_course = FreeCourse.objects.filter(id=course_id)
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
            
            if check_student and check_question and check_course and check_syllabus:
                student = check_student.first()
                question = check_question.first()
                check_compiler_tem = FreeCourseCompilerQuestionLoadTemplate.objects.filter(compiler=compiler)
                if check_compiler_tem:
                    get_template = check_compiler_tem.first()
                    coding_language = get_template.compiler
                else:
                    return Response({"main_data":main_data})
                check_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student=student, question=question, course=check_course.first(),
                                                                                syllabus=check_syllabus.first(), load_template=get_template,
                                                                                coding_language=coding_language, button_clicked="Run")
                if check_attempt:                    
                    get_attempt = check_attempt.first()                   
                    get_attempt.student_ans = source_code
                    get_attempt.button_clicked = button_clicked                    
                    get_attempt.save()
                else:                   
                    get_attempt = FreeCourseCompilerQuestionAttempt.objects.create(student=student, question=question, course=check_course.first(),
                                                                                syllabus=check_syllabus.first(), load_template=get_template,
                                                                                coding_language=coding_language, student_ans=source_code,
                                                                                button_clicked=button_clicked)
                main_data = get_attempt.id
                return Response({"status": status.HTTP_200_OK, "main_data":main_data, "message": "Attempt saved successfully."})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "main_data":main_data, "message": "Invalid request."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "main_data":main_data, "error": str(e)})


#changed
class MockQuestionAttemptResponse(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,) 

    def get(self, request):
        try:
            main_data = []
            pre_attmpt = []
            is_green = False
            user = request.user
            check_student = Student.objects.filter(user=user)
            if check_student:
                api_result = []
                main_data_id = request.GET.get("main_data_id")
                check_ans = FreeCourseCompilerQuestionAttempt.objects.filter(id=main_data_id)
                if check_ans.exists():
                    get_ans = check_ans.first()
                    # student_id = get_ans.student.id
                    ques_id = get_ans.question.id
                    ques_name = get_ans.question.ques_title
                    source_code = get_ans.student_ans
                    compiler = get_ans.load_template.compiler.split("||")
                
                    triple_quoted_string = '''{}'''.format(source_code)
                    compiler_id = compiler[1]                    
                    
                    if isinstance(get_ans.question.test_cases, str):
                        test_cases = json.loads(get_ans.question.test_cases)['data']
                    else:
                        test_cases = get_ans.question.test_cases['data']

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

                        if isinstance(data, dict) and 'submissions' in data:
                            batch_tokens = ','.join([sub['token'] for sub in data['submissions']])
                        elif isinstance(data, list):
                            batch_tokens = ','.join([sub['token'] for sub in data])
                        else:
                            raise ValueError("Unexpected data structure in API response")

                        time.sleep(3)
                        batch_result = get_batch_result(batch_tokens)
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
                                'code': None,
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
                        get_ans.score = 100 if main_data[0]['result']['status']['code'] == 15 else 0 
                        get_ans.save()

                        previous_attempts = FreeCourseCompilerQuestionAttempt.objects.filter(
                            question_id=ques_id,
                            student=check_student.first(),
                            question__practice_mock=True,
                            submitted=True,
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
            else:
                return Response({"error": "Student not found."})
        except Exception as e:
            return Response({"error": f"{e}"})



#changed
class SubmitAllMockQuestions(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,) 
    
    def post(self, request):
        try:
            user = request.user
            check_student = Student.objects.filter(user=user)
            ques_id_list = request.data.get("ques_id_list")
            ques_id_list = json.loads(ques_id_list)
            course_id = request.data.get("course_id")
            syllabus_id = request.data.get("syllabus_id")
            check_course = FreeCourse.objects.filter(id=course_id)
            check_syllabus = FreeCourseSyllabus.objects.filter(id=syllabus_id)
           
            if check_student and check_course and check_syllabus:
                #delete save code.
                student = check_student.first()
                for i in ques_id_list:
                    SavePracticeCompilerQuestionCode.objects.filter(template__question__id=int(i), student=student).delete()
                get_course = check_course.first()
                course_id = get_course.id
                get_syllabus = check_syllabus.first()
                syllabus_id = get_syllabus.id
                check_submit = MockCompilerQuestionResult.objects.filter(course=course_id, course_section_id=syllabus_id, student=student)
                if check_submit:
                    attempts = check_submit.last().attempt_number
                    attempt_number = int(attempts) + 1
                else:
                    attempt_number = 1

                right_answer = 0
                
                for ques_id in ques_id_list:
                    check_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student=student, question_id=ques_id, course=course_id, syllabus=syllabus_id)
                    
                    if check_attempt:
                        correct_answer = check_attempt.filter(status=True)
                        if correct_answer:
                            right_answer += 1
                        check_attempt.update(attepmt_number=attempt_number, submitted=True, button_clicked="Submit")
                        SavePracticeCompilerQuestionCode.objects.filter(template_id=check_attempt.first().load_template_id).delete()
                    else:
                        question = FreeCourseCompilerQuestion.objects.filter(id=ques_id, disable=False).first()
                        FreeCourseCompilerQuestionAttempt.objects.create(student=student, question_id=question.id, course_id=course_id, syllabus_id=syllabus_id, attepmt_number=int(attempt_number), submitted=True, button_clicked="Submit")

                wrong_answer = len(ques_id_list) - right_answer
                score =  (int(right_answer) / int(right_answer + wrong_answer) ) * 100
                is_passed = True if int(score) >= int(check_syllabus.first().max_score_mock) else False

                attempt = MockCompilerQuestionResult.objects.create(student=student, course_id=course_id, course_section_id=syllabus_id, questions=ques_id_list,
                                                        attempt_number=attempt_number, score=score, is_passed=is_passed, right_answers=right_answer,
                                                        wrong_answers=wrong_answer)
                
                # Notify the student if next syllabus mock is unlocked
                syllabus_max_mock_score = get_syllabus.max_score_mock
                if score >= syllabus_max_mock_score and not (get_course.section_number == get_syllabus.number):
                    title = f'Next Mock Unlock'
                    current_date = datetime.now().strftime("%d-%m-%Y")
                    message = f"Your {get_course.name}'s Syllabus-{int(get_syllabus.number) + 1} mock test is unlocked.\nDate : {current_date}"
                    notify_user(user.id, title, message)

                if get_course.section_number == get_syllabus.number:
                    get_syllabus_mock_att_passed = MockCompilerQuestionResult.objects.filter(student=student, course=get_course, course_section=get_syllabus, is_passed=True)
                    if get_syllabus_mock_att_passed:
                        
                        certificate_status = check_certificate_status(get_course.id, student.id)
                        
                        if certificate_status == True:
                            joined_student = FreeCourseJoinee.objects.filter(course=get_course, student=student).first()
                            if joined_student and not joined_student.is_certificate:
                                joined_student.is_completed = True
                                joined_student.is_certificate = True
                                joined_student.save(update_fields=['is_completed', 'is_certificate'])
                                today_date = datetime.now().strftime("%d-%m-%Y")   
                                save_pdf_to_model(student.id, get_course.id, today_date, request)
                                site_url = "https://www.maangcareers.com/free/certificates" # Need to be 
                                course_name = get_course.name
                                # subject = 'Course Completion Certificate'
                                # message = f'You have successfully completed your {get_course.name} course. Please click on the link to download your certificate.'
                                test = send_email_for_certificate(site_url, student.user.email, course_name) 
                                print(test) 

                                # Notify the student if certificate is unlocked                                
                                title = f'Certificate Unlocked'
                                current_date = datetime.now().strftime("%d-%m-%Y")
                                message = f"Your {get_course.name} is complete. Please download your certificate from the Certificates section.\nDate : {current_date}"
                                notify_user(user.id, title, message)

                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                  
                data = {"attempt_number":attempt.attempt_number,
                            "attempts_left":(int(check_syllabus.first().max_attempts_mock) - int(attempt.attempt_number)),
                            "right_answers":attempt.right_answers,
                            "worng_answers": attempt.wrong_answers,
                            "score": attempt.score,
                            "status":attempt.is_passed,
                            "max_score":get_syllabus.max_score_mock,
                            "total_questions":attempt.right_answers + attempt.wrong_answers,
                            "total_attempts":get_syllabus.max_attempts_mock
                            }
                
                return Response({"status":status.HTTP_200_OK, "data":data, "message":"Attempt saved succesfully."})
            else:
                return Response({"status":status.HTTP_404_NOT_FOUND, "data":[], "message":"Student or Course or Syllabus not found."})
        except Exception as e:
            return Response({"status":status.HTTP_400_BAD_REQUEST, "data":[], "error": f"{e}"})
       

class GetCertificate(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,) 

    def get(self, request):        
        context = {"status":status.HTTP_400_BAD_REQUEST, "message": None, "data":[]}
        try:
            user = request.user
            check_student = Student.objects.filter(user=user)
           
            if check_student.exists():
                student = check_student.first()
                
                joined_courses = FreeCourseJoinee.objects.filter(student=student).values_list('course_id', flat=True)
                if len(joined_courses) > 0:
                    data = []
                    for course_id in joined_courses:
                        course = FreeCourse.objects.filter(id=course_id).first()
                        course_join_details = FreeCourseJoinee.objects.filter(student=student, course=course).first()
                        course_data = {"course_id": course.id,
                                       "course_name":course.name,
                                       "start_date":course_join_details.joined_at,
                                       "end_date": course_join_details.end_date if course_join_details.end_date else None,
                                       "certificate_status":course_join_details.is_certificate,
                                       'certificate': course_join_details.certificate.url if course_join_details.certificate else None
                                       }
                        data.append(course_data)
                    context["status"] = status.HTTP_200_OK
                    context["message"] = "Data fetched successfully."
                    context["data"] = data                    
                else:
                    context["status"] = status.HTTP_404_NOT_FOUND
                    context["message"] = "Course registration not found "
                    context["data"] = []
            else:
                context["status"] = status.HTTP_404_NOT_FOUND
                context["message"] = "User or course not found."
                context["data"] = []
        except Exception as e:
            context["status"] = status.HTTP_400_BAD_REQUEST
            context["message"] = f"{str(e)}"
            context["data"] = []
        return Response(context)


class ProfileDetails(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,) 

    def get(self, request):
        data = {"status":status.HTTP_400_BAD_REQUEST, "message":None}
        try:
            user = request.user
            check_student = Student.objects.filter(user=user)
            if check_student:            
                profile_data = check_student.values("id","user__email","user__first_name","user__last_name","phone_num","joined_date","profile_img")
                check_joined_courses = FreeCourseJoinee.objects.filter(student__user=user)
                if check_joined_courses:
                    joined_courses = check_joined_courses.values("course__name","joined_at","is_completed","is_certificate","end_date")
                    data["profile_data"] = profile_data
                    data["course_data"] = joined_courses
                    data["status"] = status.HTTP_200_OK
                    data["message"] = "Profile and Courses fetched successfully."
                else:
                    data["profile_data"] = profile_data
                    data["course_data"] = []
                    data["status"] = status.HTTP_200_OK
                    data["message"] = "Not registered to any course."
            else:
                data["profile_data"] = []
                data["course_data"] = []
                data["status"] = status.HTTP_404_NOT_FOUND
                data["message"] = "Student not found."
        except Exception as e:
            data["profile_data"] = []
            data["course_data"] = []
            data["status"] = status.HTTP_400_BAD_REQUEST
            data["message"] = f"{str(e)}"
        return Response(data)


class FreeCourseStudentDashboard(APIView):
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        data = {"status":status.HTTP_400_BAD_REQUEST, "message":None, "data":[]}
        try:
            user = request.user
            check_student = Student.objects.filter(user=user)
            courses = []
            if check_student:
                joined_courses = FreeCourseJoinee.objects.filter(student__user=user).values_list("course_id", flat=True) 
                           
                if len(joined_courses) > 0:                
                    
                    for course_id in joined_courses:
                        c_data = {"course_id":None,"course_name":None,"quiz":{},"practice":{},"mock":{}}
                        course = FreeCourse.objects.filter(id=course_id).first()
                        c_data["course_id"] = course.id
                        c_data["course_name"] = course.name                                                
                        check_quiz_attempt = QuizQuestionAttempts.objects.filter(student__user=user,course=course)
                        check_mock_attempt = MockCompilerQuestionResult.objects.filter(student__user=user, course=course)
                        check_practice_attempt = FreeCourseCompilerQuestionAttempt.objects.filter(student__user=user, question__practice_mock=False, course=course)
                        if check_quiz_attempt:
                            get_quiz_attempt = check_quiz_attempt.last()
                            attempt_number = get_quiz_attempt.attempt_number
                            score = max(list(check_quiz_attempt.filter(syllabus=get_quiz_attempt.syllabus).values_list("attempt_score", flat=True)))
                            max_attempts = get_quiz_attempt.syllabus.max_attempts
                            max_score = get_quiz_attempt.syllabus.max_score 
                            print(max_attempts, max_score)                       
                            
                            if score >= max_score and not(course.section_number == get_quiz_attempt.syllabus.number):
                                next_syllabus_id = int(get_quiz_attempt.syllabus.id) + 1
                                next_syllabus = FreeCourseSyllabus.objects.filter(id=next_syllabus_id).first()
                                next_quiz = FreeCourseQuizQuestion.objects.filter(
                                    course_section_question__course_section__id=next_syllabus_id)
                                if next_quiz.exists():                                    
                                    c_data["quiz"]["is_lock"] = False
                                    c_data["quiz"]["syllabus_id"] = next_syllabus_id
                                    c_data["quiz"]["syllabus_name"] = next_syllabus.name
                                    c_data["quiz"]["max_attempts"] = next_syllabus.max_attempts
                                    c_data["quiz"]["max_score"] = next_syllabus.max_score
                                    c_data["quiz"]["attempt_number"] = 0
                                    c_data["quiz"]["score"] = 0
                                    c_data["quiz"]["msg"] = None
                                    c_data["quiz"]["time"] = get_quiz_attempt.attempted_at
                                else:
                                    c_data["quiz"]["is_lock"] = True
                                    c_data["quiz"]["syllabus_id"] = next_syllabus_id
                                    c_data["quiz"]["syllabus_name"] = next_syllabus.name
                                    c_data["quiz"]["max_attempts"] = next_syllabus.max_attempts
                                    c_data["quiz"]["max_score"] = next_syllabus.max_score
                                    c_data["quiz"]["attempt_number"] = 0
                                    c_data["quiz"]["score"] = 0
                                    c_data["quiz"]["msg"] = "Reach out to support team as no question is added."
                                    c_data["quiz"]["time"] = get_quiz_attempt.attempted_at
                            elif score >= max_score and (course.section_number == get_quiz_attempt.syllabus.number):
                                first_syllabus = FreeCourseSyllabus.objects.filter(course=course).first()
                                
                                c_data["quiz"]["is_lock"] = False
                                c_data["quiz"]["syllabus_id"] = first_syllabus.id
                                c_data["quiz"]["syllabus_name"] = first_syllabus.name
                                c_data["quiz"]["max_attempts"] = first_syllabus.max_attempts
                                c_data["quiz"]["max_score"] = first_syllabus.max_score
                                c_data["quiz"]["attempt_number"] = 0
                                c_data["quiz"]["score"] = 0
                                c_data["quiz"]["msg"] = None
                                c_data["quiz"]["time"] = get_quiz_attempt.attempted_at
                            else:
                                if attempt_number == max_attempts:
                                    c_data["quiz"]["is_lock"] = True
                                    c_data["quiz"]["syllabus_id"] = get_quiz_attempt.syllabus.id
                                    c_data["quiz"]["syllabus_name"] = get_quiz_attempt.syllabus.name
                                    c_data["quiz"]["max_attempts"] = get_quiz_attempt.syllabus.max_attempts
                                    c_data["quiz"]["max_score"] = get_quiz_attempt.syllabus.max_score
                                    c_data["quiz"]["attempt_number"] = attempt_number
                                    c_data["quiz"]["score"] = score
                                    c_data["quiz"]["msg"] = "Reach out to support team to unlock your quiz as you have exceeded your attempt limit."
                                    c_data["quiz"]["time"] = get_quiz_attempt.attempted_at
                                else:
                                    c_data["quiz"]["is_lock"] = False
                                    c_data["quiz"]["syllabus_id"] = get_quiz_attempt.syllabus.id
                                    c_data["quiz"]["syllabus_name"] = get_quiz_attempt.syllabus.name
                                    c_data["quiz"]["max_attempts"] = get_quiz_attempt.syllabus.max_attempts
                                    c_data["quiz"]["max_score"] = get_quiz_attempt.syllabus.max_score
                                    c_data["quiz"]["attempt_number"] = attempt_number
                                    c_data["quiz"]["score"] = score
                                    c_data["quiz"]["msg"] = None
                                    c_data["quiz"]["time"] = get_quiz_attempt.attempted_at
                        if check_mock_attempt:
                            get_mock_attempt = check_mock_attempt.last()
                            attempt_number = get_mock_attempt.attempt_number
                            score = max(list(check_mock_attempt.filter(course_section=get_mock_attempt.course_section).values_list("score", flat=True)))
                            max_attempts = get_mock_attempt.course_section.max_attempts_mock
                            max_score = get_mock_attempt.course_section.max_score_mock  

                            if score >= max_score and not(course.section_number == get_mock_attempt.course_section.number):
                                next_syllabus_id = int(get_mock_attempt.course_section.id) + 1
                                next_syllabus = FreeCourseSyllabus.objects.filter(id=next_syllabus_id).first()
                                next_mock = FreeCourseCompilerQuestion.objects.filter(course_section_id=next_syllabus_id, practice_mock=True, disable=False)
                               
                                if next_mock.exists():
                                    c_data["mock"]["is_lock"] = False
                                    c_data["mock"]["syllabus_id"] = next_syllabus_id
                                    c_data["mock"]["syllabus_name"] = next_syllabus.name
                                    c_data["mock"]["max_attempts"] = next_syllabus.max_attempts_mock
                                    c_data["mock"]["max_score"] = next_syllabus.max_score_mock
                                    c_data["mock"]["attempt_number"] = 0
                                    c_data["mock"]["score"] = 0
                                    c_data["mock"]["msg"] = None
                                    c_data["mock"]["time"] = get_mock_attempt.attempted_at
                                else:
                                    c_data["mock"]["is_lock"] = True
                                    c_data["mock"]["syllabus_id"] = next_syllabus_id
                                    c_data["mock"]["syllabus_name"] = next_syllabus.name
                                    c_data["mock"]["max_attempts"] = next_syllabus.max_attempts_mock
                                    c_data["mock"]["max_score"] = next_syllabus.max_score_mock
                                    c_data["mock"]["attempt_number"] = 0
                                    c_data["mock"]["score"] = 0
                                    c_data["mock"]["msg"] = "Reach out to support team as no question is added."
                                    c_data["mock"]["time"] = get_mock_attempt.attempted_at
                            elif score >= max_score and (course.section_number == get_mock_attempt.course_section.number):
                                first_syllabus = FreeCourseSyllabus.objects.filter(course=course).first()
                                
                                c_data["mock"]["is_lock"] = False
                                c_data["mock"]["syllabus_id"] = first_syllabus.id
                                c_data["mock"]["syllabus_name"] = first_syllabus.name
                                c_data["mock"]["max_attempts"] = first_syllabus.max_attempts_mock
                                c_data["mock"]["max_score"] = first_syllabus.max_score_mock
                                c_data["mock"]["attempt_number"] = 0
                                c_data["mock"]["score"] = 0
                                c_data["mock"]["msg"] = None
                                c_data["mock"]["time"] = get_mock_attempt.attempted_at
                            else:
                                if attempt_number == max_attempts:
                                    c_data["mock"]["is_lock"] = True
                                    c_data["mock"]["syllabus_id"] = get_mock_attempt.course_section.id
                                    c_data["mock"]["syllabus_name"] = get_mock_attempt.course_section.name
                                    c_data["mock"]["max_attempts"] = get_mock_attempt.course_section.max_attempts_mock
                                    c_data["mock"]["max_score"] = get_mock_attempt.course_section.max_score_mock
                                    c_data["mock"]["attempt_number"] = attempt_number
                                    c_data["mock"]["score"] = score
                                    c_data["mock"]["msg"] = "Reach out to support team to unlock your quiz as you have exceeded your attempt limit."
                                    c_data["mock"]["time"] = get_mock_attempt.attempted_at
                                else:
                                    c_data["mock"]["is_lock"] = False
                                    c_data["mock"]["syllabus_id"] = get_mock_attempt.course_section.id
                                    c_data["mock"]["syllabus_name"] = get_mock_attempt.course_section.name
                                    c_data["mock"]["max_attempts"] = get_mock_attempt.course_section.max_attempts_mock
                                    c_data["mock"]["max_score"] = get_mock_attempt.course_section.max_score_mock
                                    c_data["mock"]["attempt_number"] = attempt_number
                                    c_data["mock"]["score"] = score
                                    c_data["mock"]["msg"] = None
                                    c_data["mock"]["time"] = get_mock_attempt.attempted_at

                        if check_practice_attempt:
                            get_practice_attempt = check_practice_attempt.last()
                            check_next_practice_ques = FreeCourseCompilerQuestion.objects.filter(course_section_id=get_practice_attempt.syllabus.id, practice_mock=False, question_number=(int(get_practice_attempt.question.question_number) + 1), disable=False)
                            if get_practice_attempt.status == True:
                                if check_next_practice_ques:
                                    c_data["practice"]["is_lock"] = False
                                    c_data["practice"]["syllabus_id"] = get_practice_attempt.syllabus.id
                                    c_data["practice"]["syllabus_name"] = get_practice_attempt.syllabus.name
                                    c_data["practice"]["question_id"] = int(get_practice_attempt.question.id) + 1
                                    c_data["practice"]["max_score"] = get_practice_attempt.syllabus.max_score_practice
                                    c_data["practice"]["attempt_number"] = 0
                                    c_data["practice"]["score"] = 0
                                    c_data["practice"]["msg"] = None
                                    c_data["practice"]["time"] = get_practice_attempt.time
                                else:
                                    check_right_ans = check_practice_attempt.filter(syllabus=get_practice_attempt.syllabus, status=True)
                                    check_ques = FreeCourseCompilerQuestion.objects.filter(course_section_id=get_practice_attempt.syllabus.id, practice_mock=False, disable=False)
                                    max_score = (check_right_ans.count()/check_ques.count()) * 100
                                    next_syllabus = FreeCourseSyllabus.objects.filter(id=(int(get_practice_attempt.syllabus.id) + 1)).first()
                                    
                                    if max_score >= get_practice_attempt.syllabus.max_score_practice and next_syllabus:
                                        next_syllabus_ques = FreeCourseCompilerQuestion.objects.filter(course_section_id=next_syllabus.id, practice_mock=False, disable=False)
                                        if next_syllabus_ques:
                                            c_data["practice"]["is_lock"] = False
                                            c_data["practice"]["syllabus_id"] = next_syllabus.id
                                            c_data["practice"]["syllabus_name"] = next_syllabus.name
                                            c_data["practice"]["question_id"] = next_syllabus_ques.first().id
                                            c_data["practice"]["max_score"] = get_practice_attempt.syllabus.max_score_practice
                                            c_data["practice"]["attempt_number"] = 0
                                            c_data["practice"]["score"] = 0
                                            c_data["practice"]["msg"] = None
                                            c_data["practice"]["time"] = get_practice_attempt.time
                                        else:
                                            c_data["practice"]["is_lock"] = True
                                            c_data["practice"]["syllabus_id"] = next_syllabus.id
                                            c_data["practice"]["syllabus_name"] = next_syllabus.name
                                            c_data["practice"]["question_id"] = None
                                            c_data["practice"]["max_score"] = get_practice_attempt.syllabus.max_score_practice
                                            c_data["practice"]["attempt_number"] = 0
                                            c_data["practice"]["score"] = 0
                                            c_data["practice"]["msg"] = "Reach out to support team as no question is added."
                                            c_data["practice"]["time"] = get_practice_attempt.time

                                    elif max_score >= get_practice_attempt.syllabus.max_score_practice and not next_syllabus :
                                        first_syllabus = FreeCourseSyllabus.objects.filter(course=course).first()
                                        first_syllabus_practice = FreeCourseCompilerQuestion.objects.filter(course_section=first_syllabus, practice_mock=False, disable=False).first()
                                        c_data["practice"]["is_lock"] = False
                                        c_data["practice"]["syllabus_id"] = first_syllabus.id
                                        c_data["practice"]["syllabus_name"] = first_syllabus.name
                                        c_data["practice"]["question_id"] = first_syllabus_practice.id
                                        c_data["practice"]["max_score"] = first_syllabus.max_score_practice
                                        c_data["practice"]["attempt_number"] = 0
                                        c_data["practice"]["score"] = 0
                                        c_data["practice"]["msg"] = None
                                        c_data["practice"]["time"] = get_practice_attempt.time
                                    else:
                                        failed_question = FreeCourseCompilerQuestionAttempt.objects.filter(student__user=user, course=course, syllabus_id=get_practice_attempt.syllabus.id, question__practice_mock=False, status=False)
                                        c_data["practice"]["is_lock"] = False
                                        c_data["practice"]["syllabus_id"] = get_practice_attempt.syllabus.id
                                        c_data["practice"]["syllabus_name"] = get_practice_attempt.syllabus.name
                                        c_data["practice"]["question_id"] = failed_question.first().id if failed_question else get_practice_attempt.question.id
                                        c_data["practice"]["max_score"] = get_practice_attempt.syllabus.max_score_practice
                                        c_data["practice"]["attempt_number"] = get_practice_attempt.attepmt_number
                                        c_data["practice"]["score"] = 100
                                        c_data["practice"]["msg"] = None
                                        c_data["practice"]["time"] = get_practice_attempt.time
                            else:
                                c_data["practice"]["is_lock"] = False
                                c_data["practice"]["syllabus_id"] = get_practice_attempt.syllabus.id
                                c_data["practice"]["syllabus_name"] = get_practice_attempt.syllabus.name
                                c_data["practice"]["question_id"] = get_practice_attempt.question.id
                                c_data["practice"]["max_score"] = get_practice_attempt.syllabus.max_score_practice
                                c_data["practice"]["attempt_number"] = get_practice_attempt.attepmt_number
                                c_data["practice"]["score"] = 0
                                c_data["practice"]["msg"] = None
                                c_data["practice"]["time"] = get_practice_attempt.time
                        courses.append(c_data)
                    data["status"] = status.HTTP_200_OK
                    data["message"] = "Data fetched successfully."
                    data["data"] = courses
                else:
                    data["status"] = status.HTTP_404_NOT_FOUND
                    data["message"] = "Not registered to any course yet."
                    data["data"] = courses
            else:
                data["status"] = status.HTTP_404_NOT_FOUND
                data["message"] = "Student not found."
                data["data"] = courses
        except Exception as e:
            data["status"] = status.HTTP_400_BAD_REQUEST
            data["message"] = f"{str(e)}"
            data["data"] = []
        return Response(data)

