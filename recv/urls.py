"""KickServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
import os
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


urlpatterns = [

    path('',views.index, name='index'),
    path('upload',views.upload, name='upload'),
    path('useradd',views.useradd,name='useradd'),
    path('usercheck',views.usercheck,name='usercheck'),
    path('viewdoctor',views.viewdoctor,name='viewdoctor'),
    path('viewweek',views.viewweek,name='viewweek'),
    path('kakaologin',views.kakaologin, name='kakaologin'),
    path('login',views.loginpage,name='loginpage'),
    path('savedoctorconfig',views.savedoctorconfig,name='savedoctorconfig'),
    path('confirm_doctor',views.confirm_doctor,name='confirm_doctor'),
    path('childpage',views.childpage,name='childpage'),
    path('sendmessage',views.sendmessage,name='sendmessage'),
    path('sendcontent',views.sendcontent,name='sendcontent'),
    path('viewcontents',views.viewcontents,name='viewcontents'),
    path('getnowweek',views.getnowweek,name='getnowweek'),
    path('setnowweek',views.setnowweek,name='setnowweek'),
    path('getallweeks',views.getallweeks,name='getallweeks'),
    path('testurl',views.testurl,name='testurl'),
    path('connect_doctor',views.connect_doctor, name='connect_doctor'),
    path('logout',views.logout,name='logout'),
    path('profile',views.profile,name='profile'),
    path('edit_profile',views.edit_profile,name='edit_profile'),
    path('error',views.error,name='error'),
    path('wallet',views.wallet,name='wallet'),
    path('get_week_content',views.get_week_content,name='get_week_content'),
    path('hint',views.hint,name='hint'),
    path('reply_status',views.reply_status,name='reply_status'),
    path('send_to_child_log',views.send_to_child_log,name='send_to_child_log'),
    path('send_to_doctor_log',views.send_to_doctor_log,name='send_to_doctor_log'),
    path('send_to_doctor',views.send_to_doctor,name='send_to_doctor'),
    path('doctor_result',views.doctor_result,name='doctor_result'),
] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
