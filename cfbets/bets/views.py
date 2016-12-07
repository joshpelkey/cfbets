from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@login_required(login_url='/login/')
def my_bets(request):
	return render(request, 'bets/base_my_bets.html', {'nbar': 'my_bets'})

@login_required(login_url='/login/')
def open_bets(request):
	return render(request, 'bets/base_open_bets.html', {'nbar': 'open_bets'})

@login_required(login_url='/login/')
def all_bets(request):
	return render(request, 'bets/base_all_bets.html', {'nbar': 'all_bets'})

@staff_member_required(login_url='/')
def admin_bets(request):
	return render(request, 'bets/base_admin_bets.html', {'nbar': 'admin_bets'})
