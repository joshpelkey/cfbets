from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='/login/')
def my_bets(request):
	return render(request, 'bets/base_mybets.html')
