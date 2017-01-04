import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from bets.forms import PlaceBetsForm
from bets.models import ProposedBet, AcceptedBet

# Create your views here.

def bets(request):
	return HttpResponseRedirect('/bets/my_bets');

@login_required(login_url='/login/')
def my_bets(request):
	# get the current user
	current_user = request.user

	# get all their proposed bets that have remaining bets and have end dates past now
	your_open_bets = ProposedBet.objects.filter(user=current_user, remaining_wagers__gt=0, end_date__gt=timezone.now())

	# your active bets, i.e. those bets you have open that other users have accepted
	your_active_bets = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__isnull=True)

	return render(request, 'bets/base_my_bets.html', {'nbar': 'my_bets', 'your_open_bets': your_open_bets, 'your_active_bets': your_active_bets})

@login_required(login_url='/login/')
def open_bets(request):
	# get the current user
	current_user = request.user

	# get all open prop bets from other users
	open_bets = ProposedBet.objects.filter(remaining_wagers__gt=0, end_date__gt=timezone.now()).exclude(user=current_user)

	return render(request, 'bets/base_open_bets.html', {'nbar': 'open_bets', 'open_bets': open_bets})

@login_required(login_url='/login/')
def all_bets(request):
	# get all active accepted bets
	all_active_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=True)

	# get all accepted bets, ever
	all_accepted_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=False)

	return render(request, 'bets/base_all_bets.html', {'nbar': 'all_bets', 'all_active_bets': all_active_bets, 'all_accepted_bets': all_accepted_bets})

def place_bets_form_process(request, next_url):
	if request.method == 'POST':
		form = PlaceBetsForm(request.POST)

		if form.is_valid():
			# gather form entries and save to DB
			new_bet = ProposedBet(user=request.user, \
									prop_text = form.cleaned_data['bet'], \
									prop_wager = form.cleaned_data['bet_amount'], \
									max_wagers = form.cleaned_data['qty_allowed'], \
									remaining_wagers = form.cleaned_data['qty_allowed'], \
									end_date = form.cleaned_data['bet_expiration_date'], \
									created_on = timezone.now(), \
									modified_on = timezone.now())
			# save to the db
			new_bet.save()
			
			# save the url to know where to redirect
			response = {'url': next_url}

			# send a message over that the bet is complete
			messages.success(request, 'Bet submitted succesfully.')

			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			# form isn't valid, return to ajax call with error and form with errors
			return render(request, 'bets/place_bets.html', {'place_bets_form': form}, status=400)

	return HttpResponseRedirect('/bets/my_bets')
	

@staff_member_required(login_url='/')
def admin_bets(request):
	return render(request, 'bets/base_admin_bets.html', {'nbar': 'admin_bets'})
