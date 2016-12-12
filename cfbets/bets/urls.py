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
from django.contrib.auth import views as auth_views
from bets import views

app_name = 'bets'
urlpatterns = [
    url(r'^$', views.bets),
    url(r'^my_bets/', views.my_bets),
    url(r'^open_bets/', views.open_bets),
    url(r'^all_bets/', views.all_bets),
    url(r'^process_place_bets/(?P<next_url>.*$)', views.place_bets_form_process, name='place_bets_form_process'),
    url(r'^admin_bets/', views.admin_bets),
]
