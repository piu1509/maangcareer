# from .views import NoticeViewSet, ProfileViewSet,ProfilePasswordUpdate,StudentProfileInfo,ProfileDetailsUpdate
from .views import *
from django.urls import path

urlpatterns = [
    # path('notice/', NoticeViewSet.as_view(), name='notice'),
    path('profile/<pk>', ProfileViewSet.as_view(), name='profile'),

    # Profile
    path('profilepasswordupdate/', ProfilePasswordUpdate.as_view(), name='profilepasswordupdate'),
    path('studentprofileinfo/', StudentProfileInfo.as_view(), name='studentprofileinfo'),
    path('profiledetailsupdate/', ProfileDetailsUpdate.as_view(), name='profiledetailsupdate'),
    path('terms-condition/', TermsAndConditionView.as_view(), name='terms-condition'),
    # Notification
    # path('allnotifications/', AllNotifications.as_view(), name='all_notifications'),
    # path('notifications/mark-as-read/', MarkAsRead.as_view(), name='mark_as_read'),

    path('profile-data/', ProfileView.as_view(), name='profile-data'),
    path('profile-edit/', ProfileEditView.as_view(), name='profile-edit'),

]