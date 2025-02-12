from django.urls import path
from salesManagement.views import *

urlpatterns = [
    path('login/', SalesPersonLoginView.as_view(), name='sales-person-login'),   
    path('verify-otp/', SalesPersonOTPVerificationView.as_view(), name='verify_otp-for-sales-person'),
    path('resend-otp/', SalesPersonResendOTPView.as_view(), name='resend-otp-for-sales-person'),
    path('user-profile/', UserProfileView.as_view(), name='user-profile-for-sales-person'),
    path('add-leave/', LeaveRecordCreateView.as_view(), name='add-leave-for-sales-person'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password-for-sales-person'),
    
]
