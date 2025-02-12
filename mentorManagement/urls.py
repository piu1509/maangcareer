from django.urls import path
from .views import *


urlpatterns = [ 
    path('terms-condition/', InstructorTermsAndConditionView.as_view(), name='terms-condition'),
    path('rules-regulation/', InstructorRulesAndRegulationView.as_view(), name='rules-regulation'),
    path('page-visit-count/', InstructorRulesAndRegulationPageVisitCount.as_view(), name='page-visit-count'), #01/02/2024

    # mentor profile
    path('inst-profile/<pk>', InstructorProfileViewSet.as_view(), name='inst-profile'), ####
    path('inst-profilepasswordupdate/', InstructorProfilePasswordUpdate.as_view(), name='inst-profilepasswordupdate'),
    path('inst-profileinfo/', InstructorProfileInfo.as_view(), name='inst-profileinfo'),
    path('inst-profiledetailsupdate/', InstructorProfileDetailsUpdate.as_view(), name='inst-profiledetailsupdate'),

    #dashboard
    path('inst-calender-view/', InstructorDashboardCalenderViewList.as_view(), name='inst-calender-view'), #19/01/2024
    path('inst-cls-complete/', InstructorClassCompleteProgressBar.as_view(), name='inst-cls-complete'),  #19/01/2024
    path('inst-ongoing-upcomig/', InstructorDashboardOngoingUpcomingUpdates.as_view(), name='inst-ongoing-upcomig'),
    path('inst-timetable/', InstructorTimetableViewList.as_view(), name='inst-timetable'), 

    #24/01/2024
    path('inst-course/', InstructorCourseSelection.as_view(), name='inst-course'),
    path('inst-get-batch/', InstructorOngoingPreviousBatchSelection.as_view(), name='inst-get-batch'),
    path('inst-course-list/', InstructorCourseSelectionViewList.as_view(), name='inst-course-list'),
    path('week-topic-list/', InstructorSubmissionWeekTopicList.as_view(), name='week-topic-list'),
    path('batch-subission-data/', InstructorSubmissionPointBatchDataViewList.as_view(), name='batch-subission-point'),
    path('all_batch-subission-data/', InstructorSubmissionAllDataViewList.as_view(), name='all_batch-subission-data'),
    path('all-subission-data/', InstructorSubmissionPointAllViewList.as_view(), name='all-subission-data'),

    #29/01/2024
    path('task-status/', InstructorSubmissionTaskStatusChange.as_view(), name='task-status'),
    path('inst-search-ongoing-data/', SearchSubmissionOngoingTasks.as_view(), name='inst-search-ongoing-data'),
    path('inst-search-prev-data/', SearchSubmissionPreviousTasks.as_view(), name='inst-search-prev-data'),
    
    #31/01/2024
    path('course-syllabus/', GetCourseSyllabusViewList.as_view(), name='course-syllabus'),

    
    #02/02/2024
    path('batch-complete-view/', InstructorOngoingPreviousBatchComplitionList.as_view(), name='batch-complete-view'),
    path('batch-request-ongoing/', OngoingBatchCompleteRequestViewList.as_view(), name='batch-request-ongoing'),
    path('batch-complete-prev-list/', PreviousBatchCompleteRequestViewList.as_view(), name='batch-complete-prev-list'),

    # Teaching section 
    path('inst-week-notes/', InstructorAllNotesWeekLock.as_view(), name='inst-week-notes'),
    path('inst-practice-week-lock/', InstructorTeachingPracticeWeekLock.as_view(), name='inst-practice-week-lock'),#
    path('inst-practice-question-all/', InstructorAllPracticeQuestionsAll.as_view(), name='inst-practice-question-all'),#
    path('inst-practice-question/', InstructorAllPracticeQuestion.as_view(), name='inst-practice-question'),#
    path('inst-practice-question-titel/<str:q_titel>', InstructorPracticeQuestionSearchTitel.as_view(), name='inst-practice-question-titel'),#
    path('inst-practice-question-temp/', InstructorAllPracticeLoadTemplate.as_view(), name='inst-practice-question-temp'),
    path('inst-practice-save-code/', InstructorPracticeSaveCode.as_view(), name='inst-practice-save-code'),
    path('inst-practice-delete-code/', InstructorPracticeDeleteCode.as_view(), name='inst-practice-delete-code'),  #29/01/2024
    path('inst-practice-question-submission/', InstructorAllPracticeQuestionSubmission.as_view(), name='inst-practice-question'),#
    path('inst-practice-question-submission-responce/', InstructorAllPracticeQuestionSubmissionResponce.as_view(), name='inst-practice-question-submission-responce'),
    
]