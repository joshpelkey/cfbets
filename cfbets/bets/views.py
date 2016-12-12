import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from bets.forms import PlaceBetsForm

# Create your views here.

def bets(request):
	return HttpResponseRedirect('/bets/my_bets');

@login_required(login_url='/login/')
def my_bets(request):
	if request.method == 'POST':
        	form = PlaceBetsForm(request.POST)
		if form.is_valid():
			# do something
			return HttpResponseRedirect('/account_settings')
		else:
			return render(request, 'bets/base_my_bets.html', {'nbar': 'my_bets', 'form': form})
	else:
		form = PlaceBetsForm()

	return render(request, 'bets/base_my_bets.html', {'nbar': 'my_bets', 'form': form})

@login_required(login_url='/login/')
def open_bets(request):
	return render(request, 'bets/base_open_bets.html', {'nbar': 'open_bets'})

@login_required(login_url='/login/')
def all_bets(request):
	return render(request, 'bets/base_all_bets.html', {'nbar': 'all_bets'})

def place_bets_form_process(request, next_url):
	if request.method == 'POST':
        	form = PlaceBetsForm(request.POST)
		if form.is_valid():
			# do something with this form eventually
			response = {'message': 'Bet placed succesfully!', 'url': next_url}
			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			# form isn't valid, return to ajax call with error and form with errors
			return render(request, 'bets/place_bets.html', {'form': form}, status=400)

	return HttpResponseRedirect('/bets/my_bets')
	

@staff_member_required(login_url='/')
def admin_bets(request):
	return render(request, 'bets/base_admin_bets.html', {'nbar': 'admin_bets'})
