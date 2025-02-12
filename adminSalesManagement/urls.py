from django.urls import path
from .views import *

urlpatterns = [
    path('login/', SubAdminLoginView.as_view(), name='sales-admin-login'),    
    path('verify-otp/', SubAdminOTPVerificationView.as_view(), name='verify_otp-for-admin-sale'),
    path('resend-otp/', SubAdminResendOTPView.as_view(), name='resend-otp-for-admin-sale'),

    path('course-list/', PaidCourseList.as_view(), name='course-list-for-admin-sale'),
    path('batch-list/', PaidBatchList.as_view(), name='batch-list-for-admin-sale'),
    path('instructor-list/', InstructorList.as_view(), name='instructor-list-for-admin-sale'),
    path('project-list/', ProjectList.as_view(), name='project-list-for-admin-sale'),
    path('add-batch/', AddBatch.as_view(), name='add-batch-for-admin-sale'),
    path('preview-add-batch/', PreviewAddBatch.as_view(), name='preview-add-batch-for-admin-sale'),
    path('batch-details/', BatchDetailsView.as_view(), name='batch-details-for-admin-sale'),
    path('batch-time-table/', BatchTimeTableList.as_view(), name='batch-time-table-for-admin-sale'),
    path('batch-students/', BatchStudentList.as_view(), name='batch-students-for-admin-sale'),
    path('add-class/', AddClass.as_view(), name='add-class-for-admin-sale'),
    path('update-batch/', UpdateBatch.as_view(), name='update-batch-for-admin-sale'),
    path('class-details/', ClassDetails.as_view(), name='class-details-for-admin-sale'),
    path('update-class/', UpdateClass.as_view(), name='update-class-for-admin-sale'),
    path('delete-batch/', DeleteBatch.as_view(), name='delete-batch-for-admin-sale'),
    path('delete-class/', DeleteClass.as_view(), name='delete-class-for-admin-sale'),
    path('batch-student-delete/', BatchStudentDelete.as_view(), name='batch-student-delete-for-admin-sale'),
    path('student-list/', StudentList.as_view(), name='student-list-for-admin-sale'),
    path('student-details/', StudentDetails.as_view(), name='student-details-for-admin-sale'),
    path('student-paid-quiz-progress/', StudentPaidQuizProgress.as_view(), name='student-paid-quiz-progress-for-admin-sale'),
    path('student-paid-practice-progress/', StudentPaidPracticeProgress.as_view(), name='student-paid-practice-progress-for-admin-sale'),
    path('student-paid-mock-progress/', StudentPaidMockProgress.as_view(), name='student-paid-mock-progress-for-admin-sale'),
    path('student-free-quiz-progress/', StudentFreeQuizProgress.as_view(), name='student-free-quiz-progress-for-admin-sale'),
    path('student-free-practice-progress/', StudentFreePracticeProgress.as_view(), name='student-free-practice-progress-for-admin-sale'),
    path('student-free-mock-progress/', StudentFreeMockProgress.as_view(), name='student-free-mock-progress-for-admin-sale'),
    path('user-list/', UserList.as_view(), name='user-list-for-admin-sale'),
    path('add-or-update-student/', AddOrUpdateStudent.as_view(), name='add-or-update-student-for-admin-sale'),

    path('change-password/', ChangePassword.as_view(), name='change-password'),
    path('add-staff/', AddStaff.as_view(), name='add-or-update-staff'),
    path('all-staff/', AllStaffList.as_view(), name='all-staff'),
    path('staff-profile/', StaffDetails.as_view(), name='staff-profile'),
    path('delete-staff/', DeleteStaff.as_view(), name='delete-staff'),
    path('deleted-staff-list/', DeletedStaffList.as_view(), name='deleted-staff-list'),
    path('expense-list/', ExpenseList.as_view(), name='expense-list'),
    path('expense-type-list/', ExpenseTypeList.as_view(), name='expense-type-list'),
    path('add-expense/', AddExpense.as_view(), name='add-expense'),

    
]
