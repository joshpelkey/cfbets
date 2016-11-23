from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect

def welcome(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/my_bets')
	else:
		return render(request, 'base_welcome.html')
