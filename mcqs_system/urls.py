"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from accounts import views 
from accounts.views import home 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'), 
    path('accounts/', include("accounts.urls"), name='accounts'),
    path('create/', include("create_test.urls"), name='create_test'),  
    path('question-bank/', include('question_bank.urls'), name='question_bank'),
    path('attempt_test/', include('attempt_test.urls'), name='attempt_test'),
    path('performance-analytics/', include('performance_analytics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

