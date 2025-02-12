from .views import *
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('submit-quiz-attempt/', QuizUpdateViewSet, basename='submit-quiz-attempt')

urlpatterns = [
    path('list-quiz/', QuizViewSet.as_view(), name='list-quiz'),
    # path('submit-quiz-attempt/<pk>/', QuizUpdateViewSet.as_view(), name='submit-quiz-attempt'),
    path('list-quiz-questions/', QuizQuestionViewSet.as_view(), name='list-quiz-ques'),
    path('list-compiler-questions/', CompilerQuestionViewSet.as_view(), name='list-comp-ques'),
    
    path('examquestiontimer/', QuestionTimerView.as_view(), name='examquestiontimer'),
    
    path('std-all-courese/', StudentallCourse.as_view(), name='std-all-courese'),#
    path('std-all-week-lock/', StudentallCourseWeekLock.as_view(), name='std-all-week-lock'),#
    path('course-question/', StudentCourseQuestions.as_view(), name='course-question'),
    path('std-question-attempts/', StudentCourseQuestionsAttempts.as_view(), name='std-question-attempts'),

    path('std-list-notes/', StudentallNotesWeekLock.as_view(), name='std-list-notes'),#
    path('std-practice-week-lock/', StudentallPracticeWeekLock.as_view(), name='std-practice-week-lock'),  ##30/01/2024
    path('std-practice-question-all/', StudentallPracticeQuestionAll.as_view(), name='std-practice-question'), #30/01/2024
    path('std-practice-question/', StudentallPracticeQuestion.as_view(), name='std-practice-question'), #30/01/2024
    path('std-practice-question-titel/<str:q_titel>', PracticeQuestionSearchTitel.as_view(), name='std-practice-question-titel'), #30/01/2024
    path('std-practice-question-temp/', StudentallPracticeLoadTemplate.as_view(), name='std-practice-question-temp'),
    path('std-practice-save-code/', StudentPracticeSaveCode.as_view(), name='std-practice-save-code'),
    path('std-practice-delete-code/', StudentPracticeDeleteCode.as_view(), name='std-practice-delete-code'),
    path('std-practice-question-submission/', StudentallPracticeQuestionSubmission.as_view(), name='std-practice-question'),##31/01/2024
    path('std-practice-question-submission-responce/', StudentallPracticeQuestionSubmissionResponce.as_view(), name='std-practice-question-submission-responce'),


    path('quizprogress/', StudentDashboardQuizProgressBar.as_view(), name='quizprogress'),
    path('mockprogress/', StudentDashboardMockProgressBar.as_view(), name='mockprogress'),

    #dashboard others
    path('std-onging-upcoming/', StudentDashboardOngoingUpcomingUpdates.as_view(), name='std-onging-upcoming'),
    path('quiz-contest/', StudentDashboardQuizWeekContest.as_view(), name='quiz-contest'),
    path('practice-contest/', StudentDashboardPracticeWeekContest.as_view(), name='practice-contest'),
    path('mock-contest/', StudentDashboardMockWeekContest.as_view(), name='mock-contest'),
    
    # submission protal #RijuDjango
    path('upload-task-for-user/', UploadTask.as_view(), name='upload-Task'),
    path('view-upload-task/', ViewUploadTask.as_view(), name='view-upload-Task'),

    #mock
    path('mock-week-lock/', StudentallMockWeekLock.as_view(), name='mock-week-lock'),#31/01/2024
    path('std-mock-question-all/', StudentallMockQuestionAll.as_view(), name='std-mock-question'),  #30/01/2024
    path('std-mock-question/', StudentallMockQuestion.as_view(), name='std-practice-question'),#30/01/2024
    #newadd
    path('std-mock-question-titel/<str:q_titel>', MockQuestionSearchTitel.as_view(), name='std-mock-question-titel'), #30/01/2024
    path('std-mock-question-submission/', StudentallMockQuestionSubmission.as_view(), name='std-mock-question-submission'),#31/01/2024
    path('std-mock-question-submission-all/', StudentallMockQuestionSubmissionAll.as_view(), name='std-mock-question-submission-all'),
    path('std-mock-question-submission-responce/', StudentallMockQuestionSubmissionResponce.as_view(), name='std-mock-question-submission-responce'),
    path('get_messages/', GetMessage.as_view(), name='get_messages'),
    path('stud-attend/', StudentAttendanceProgressBar.as_view(), name='stud-attend'),
    path('std-all-progress/', StudentDashboardAllProgressBar.as_view(), name='std-all-progress'), #02/01/2024 ->all progress bar api
    path('std-all-contests/', StudentDashboardAllContests.as_view(), name='std-all-contests'), #03/01/2024 ->all quiz/mock/practice contest api
    path('search-data/', SearchUploadTasks.as_view(), name='search-data'), #08/01/2024

    path('user-valid-check/', UserVarificationView.as_view(), name='user-valid-check'), #18/01/2024
    path('stud-course/', StudentCourseSelectionTabForQuiz.as_view(), name='stud-course'), #21/04/2024
    path('stud-revoke-course/', StudentRevokeFromCompleteCourse.as_view(), name='stud-revoke-course'), #21/04/2024

    path('stud-submission-topic/', GetSubmissionTopic.as_view(), name='stud-submission-topic'),



] + router.urls