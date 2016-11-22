"""cfbets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from cfbets.views import welcome
from bets import views

urlpatterns = [
    url(r'^$', welcome),
    url(r'^login/$', auth_views.login, {'template_name': 'base_login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^mybets/', views.my_bets),
    url(r'^allbets/', TemplateView.as_view(template_name='bets/base_allbets.html')),
    url(r'^reporting/', TemplateView.as_view(template_name='bets/base_reporting.html')), 
    url(r'^adminbets/', TemplateView.as_view(template_name='bets/base_adminbets.html')),
    url(r'^admin/', admin.site.urls),
]
