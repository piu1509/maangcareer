"""
URL configuration for maangcareerers project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT
from .knox_auth import LoginView as CustomKnoxLoginView, SignUpView,ResendOtpAPIView, PasswordResetRequestView, PasswordResetConfirmView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('knox.urls')),
    path('api/login/', CustomKnoxLoginView.as_view()),
    path('api/signup/', SignUpView.as_view()),
    path('api/resend/', ResendOtpAPIView.as_view()),
    path('api/reset_password_link/', PasswordResetRequestView.as_view()),
    path('api/reset_password/', PasswordResetConfirmView.as_view()),
    path('api/', include('django.contrib.auth.urls')),

    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('accounts/', include('allauth.urls')),

    path('course-management/', include('courseManagement.urls')),
    path('free-course-management/', include('freeCourseManagement.urls')),
    path('user-management/', include('userManagement.urls')),
    path('test-management/', include('testsManagement.urls')),
    path('crm/', include('CRM.urls')),
    path('website-management/', include('newWebsiteManagement.urls')),
    path('funnel-date/', include('funneldate.urls')),
    path('mentor-management/', include('mentorManagement.urls')),
    path('notification/', include('notificationManagement.urls')),

    path('data-management/', include('dataManagement.urls')),
    path('sales-management/', include('salesManagement.urls')),
    path('admin-sales-management/', include('adminSalesManagement.urls')),


] + static(MEDIA_URL, document_root=MEDIA_ROOT)