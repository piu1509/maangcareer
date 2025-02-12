from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path

# router = DefaultRouter()
# router.register('list-free-courses', FreeCourseViewSet, basename='list-free-courses')

urlpatterns = [
    path('list-free-courses/', FreeCourseListView.as_view(), name='list-free-courses'),
    path('authenticated-user-registered-course-list/', AuthenticatedFreeCourseList.as_view(), name='authenticated-user-registered-course-list'),
    path('free-course-view/<int:pk>', FreeCourseDetailView.as_view(), name='free-course-view'),
    path('student-register-free-course/', StudentFreeCourseRegister.as_view(), name='student-join-free-course'),
    path('student-free-course-list/', StudentFreeCourseList.as_view(), name='student-free-course-list'),
    path('syllabus-list/', CourseSyllabusList.as_view(), name='syllabus-list'),
    path('syllabus-question-list/', SyllabusQuestionsList.as_view(), name='syllabus-question-list'),
    path('quiz-question-attempt/', QuizQuestionAttempt.as_view(), name='quiz-question-attempt'),

    # Compiler question

    ## Practice
    path('syllabus-list-practice-question/', PracticeQuestionLockStatus.as_view(), name='syllabus-list-practice-question'),
    path('practice-compiler-question-list/', PracticeCompilerQuestionList.as_view(), name='compiler-question-list'),
    path('practice-compiler-question-load-template/', PracticeCompilerQuestionLoadTemplate.as_view(), name='practice-compiler-question-load-template'),
    path('practice-compiler-question-save-code/', PracticeCompilerQuestionSaveCode.as_view(), name='practice-compiler-question-save-code'),
    path('delete-saved-compiler-question-code/', PracticeCompilerQuestionDeleteCode.as_view(), name='delete-saved-compiler-question-code'),
    path('practice-compiler-question-attempt/', PracticeQuestionAttempt.as_view(), name='practice-compiler-question-attempt'),
    path('practice-compiler-question-attempt-response/', PracticeQuestionAttemptResponse.as_view(), name='practice-compiler-question-attempt-response'),

    ## Mock
    path('mock-question-lock-status/', MockQuestionLockStatus.as_view(), name='mock-question-lock-status'),
    path('mock-compiler-question-list/', MockCompilerQuestionList.as_view(), name='mock-compiler-question-list'),
    path('mock-compiler-question-attempt/', MockQuestionAttempt.as_view(), name='mock-compiler-question-attempt'),
    path('mock-compiler-question-attempt-response/', MockQuestionAttemptResponse.as_view(), name='mock-compiler-question-attempt-response'),
    path('submit-all-mock-question/', SubmitAllMockQuestions.as_view(), name='submit-all-mock-question'),
    path('get-certificate/', GetCertificate.as_view(), name='get-certificate'),
    path('student-profile-free-course/', ProfileDetails.as_view(), name='student-profile-free-course'),
    path('student-dashboard-free-course/', FreeCourseStudentDashboard.as_view(), name='student-dashboard-free-course'),   

    
]
