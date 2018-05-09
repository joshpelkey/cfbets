"""cfbets:bets URL Configuration

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
from bets.views import AllBetsJson, MyCompletedBetsJson, AdminBetsJson

app_name = 'bets'
urlpatterns = [
    url(r'^$', views.bets),
    url(r'^my_bets/', views.my_bets),
    url(r'^open_bets/', views.open_bets),
    url(r'^all_bets/', views.all_bets),
    url(r'^all_bets_json/', AllBetsJson.as_view(), name='all_bets_json'),
    url(r'^my_completed_bets_json/', MyCompletedBetsJson.as_view(), name='my_completed_bets_json'),
    url(r'^admin_bets_json/', AdminBetsJson.as_view(), name='admin_bets_json'),
    url(r'^your_stats/', views.your_stats),
    url(r'^global_stats/', views.global_stats),
    url(r'^process_place_bets/(?P<next_url>.*$)', views.place_bets_form_process, name='place_bets_form_process'),
    url(r'^check_duplicate_bet/', views.check_duplicate_bet),
    url(r'^remove_prop_bet/', views.remove_prop_bet),
    url(r'^accept_prop_bet/', views.accept_prop_bet),
    url(r'^set_prop_bet/', views.set_prop_bet),
    url(r'^undo_prop_bet/', views.undo_prop_bet),
    url(r'^admin_bets/', views.admin_bets),
]
