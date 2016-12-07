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
from cfbets.views import welcome, sign_up, account_settings
from bets import views

urlpatterns = [
    url(r'^$', welcome),
    url(r'^login/$', auth_views.login, {'template_name': 'base_login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^sign_up/$', sign_up),
    url(r'^account_settings/', account_settings),
    url(r'^my_bets/', views.my_bets),
    url(r'^open_bets/', views.open_bets),
    url(r'^all_bets/', views.all_bets),
    url(r'^admin_bets/', views.admin_bets),
    url(r'^admin/', admin.site.urls),
]
