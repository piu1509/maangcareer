# from .views import CourseViewSet, TimeTableViewSet, UserBatchViewSet, PaymentViewSet, NoteViewSet, CertificateViewSet,StudentClassTimeTableViewSet
from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register('list-courses', CourseViewSet, basename='list-courses')
# router.register('list-notes', NoteViewSet, basename='list-notes')
# router.register('list-certificates', CertificateViewSet, basename='list-certificate')
urlpatterns = [
    # path('list-courses/', CourseViewSet.as_view(), name='list-courses'),
    path('course-topics/', CourseTopicListView.as_view(), name='course-topic-list'),
    path('timetable/', TimeTableViewSet.as_view(), name='timetable'),
    path('list-notes/', NoteViewSet.as_view(), name='list-notes'),
    path('list-certificates/', CertificateViewSet.as_view(), name='list-certificates'),
    path('user-batch/', UserBatchViewSet.as_view(), name='user-batch'),
    path('payment-status/', PaymentViewSet.as_view({'post':'create'}), name='payment-status'),
    path('stud-timetable-list/', StudentClassTimeTableViewSet.as_view(), name='stud-timetable-list'),
    path('stud-routine-list/', StudentClassesRoutineViewSet.as_view(), name='stud-routine-list'),
    path('stud-project-assign/<int:b_id>', StudentProjectAssign.as_view(), name='stud-project-assign'),
    path('get_emi/<int:course_id>', CourseEmiDetailsListView.as_view(), name='get_emi'),
    path('emi-details/', EmiDetailsView.as_view(), name='emi-details'),
    path('get-upcoming-dates/', UpcomingDatesView.as_view(), name='get-upcoming-dates'),
    path('student-emi-details/', StudentInstallmentPayment.as_view(), name='student-emi-details'),
    path('student-enrollment/', EnrollStudentToBatch.as_view(), name='student-enrollment'),
    path('delete-batch-on-payment-failure/', DeleteBatch.as_view(), name='delete-batch-on-payment-failure'),
    path('create-payment-order-id/', CreateRazorpayOrder.as_view(), name='create-payment-order-id'),
] + router.urls
