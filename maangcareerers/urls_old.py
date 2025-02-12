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
from .settingsimport MEDIA_URL, MEDIA_ROOT
from .knox_auth import LoginView as CustomKnoxLoginView, SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('knox.urls')),
    path('api/login/', CustomKnoxLoginView.as_view()),
    path('api/signup/', SignUpView.as_view()),
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('accounts/', include('allauth.urls')),

    path('course-management/', include('courseManagement.urls')),
    path('crm/', include('CRM.urls')),

] + static(MEDIA_URL, document_root=MEDIA_ROOT)