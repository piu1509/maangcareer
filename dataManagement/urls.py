from django.urls import path
from .views import *

urlpatterns = [
    path('login/', DataEntryUserLoginView.as_view(), name='data-entry-user-login'),   
    path('verify-otp/', DataEntryUserOTPVerificationView.as_view(), name='verify_otp-for-data-entry-user'),
    path('resend-otp/', DataEntryUserResendOTPView.as_view(), name='resend-otp-for-data-entry'),

    path('course-list/', PaidCourseListAPI.as_view(), name='course-list-for-data-entry'),
    path('batch-list/', PaidBatchListAPI.as_view(), name='batch-list-for-data-entry'),
    path('instructor-list/', InstructorListAPI.as_view(), name='instructor-list-for-data-entry'),
    path('project-list/', ProjectListAPI.as_view(), name='project-list-for-data-entry'),
    path('add-batch/', AddBatchAPI.as_view(), name='add-batch-for-data-entry'),
    path('preview-add-batch/', PreviewAddBatchAPI.as_view(), name='preview-add-batch-for-data-entry'),
    path('batch-details/', BatchDetailsViewAPI.as_view(), name='batch-details-for-data-entry'),
    path('batch-time-table/', BatchTimeTableListAPI.as_view(), name='batch-time-table-for-data-entry'),
    path('batch-students/', BatchStudentListAPI.as_view(), name='batch-students-for-data-entry'),
    path('add-class/', AddClassAPI.as_view(), name='add-class-for-data-entry'),
    path('update-batch/', UpdateBatchAPI.as_view(), name='update-batch-for-data-entry'),
    path('class-details/', ClassDetailsAPI.as_view(), name='class-details-for-data-entry'),
    path('update-class/', UpdateClassAPI.as_view(), name='update-class-for-data-entry'),
    path('delete-batch/', DeleteBatchAPI.as_view(), name='delete-batch-for-data-entry'),
    path('delete-class/', DeleteClassAPI.as_view(), name='delete-class-for-data-entry'),
    path('student-list/', StudentListAPI.as_view(), name='student-list-for-data-entry'),
    path('student-details/', StudentDetailsAPI.as_view(), name='student-details-for-data-entry'),
    path('student-paid-quiz-progress/', StudentPaidQuizProgressAPI.as_view(), name='student-paid-quiz-progress-for-data-entry'),
    path('student-paid-practice-progress/', StudentPaidPracticeProgressAPI.as_view(), name='student-paid-practice-progress-for-data-entry'),
    path('student-paid-mock-progress/', StudentPaidMockProgressAPI.as_view(), name='student-paid-mock-progress-for-data-entry'),
    path('student-free-quiz-progress/', StudentFreeQuizProgressAPI.as_view(), name='student-free-quiz-progress-for-data-entry'),
    path('student-free-practice-progress/', StudentFreePracticeProgressAPI.as_view(), name='student-free-practice-progress-for-data-entry'),
    path('student-free-mock-progress/', StudentFreeMockProgressAPI.as_view(), name='student-free-mock-progress-for-data-entry'),
    path('user-list/', UserListAPI.as_view(), name='user-list-for-data-entry'),
    path('add-or-update-student/', AddOrUpdateStudentAPI.as_view(), name='add-or-update-student-for-data-entry'),

    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('leave_application_post/', LeaveRecordCreateView.as_view(), name='leave_application_post'),
    path('instructors/', MentorList.as_view(), name='instructor-list-create'),
    path('change-password/', ChangePasswordAPI.as_view(), name='change-password-for-data-entry'),
    
]
