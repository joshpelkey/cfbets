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
	your_open_bets = ProposedBet.objects.filter(user=current_user, remaining_wagers__gt=0, end_date__gt=timezone.now(), won_bet__isnull=True)

	# your active bets, i.e. those bets you have accepted and your bets that other users have accepted
	your_accepted_bets = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__isnull=True)
	your_bets_accepted_by_others = AcceptedBet.objects.filter(accepted_prop__user=current_user, accepted_prop__won_bet__isnull=True) 
	your_active_bets = your_accepted_bets | your_bets_accepted_by_others

	return render(request, 'bets/base_my_bets.html', {'nbar': 'my_bets', 'your_open_bets': your_open_bets, 'your_active_bets': your_active_bets})

@login_required(login_url='/login/')
def open_bets(request):
	# get the current user
	current_user = request.user

	# get all open prop bets from other users
	open_bets = ProposedBet.objects.filter(remaining_wagers__gt=0, end_date__gt=timezone.now(), won_bet__isnull=True).exclude(user=current_user)

	return render(request, 'bets/base_open_bets.html', {'nbar': 'open_bets', 'open_bets': open_bets})

@login_required(login_url='/login/')
def all_bets(request):
	# get all active accepted bets
	all_active_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=True)

	# get all accepted bets, ever
	all_accepted_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=False)

	return render(request, 'bets/base_all_bets.html', {'nbar': 'all_bets', 'all_active_bets': all_active_bets, 'all_accepted_bets': all_accepted_bets})

@login_required(login_url='/login/')
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
	

@login_required(login_url='/login/')
def remove_prop_bet(request):
	if request.method == 'GET' and 'id' in request.GET:
		# get the prop id from the get request
		bet_id = request.GET['id']

		# make sure it's an int
		try:
			int(bet_id)
			is_int = True

		except ValueError:
			is_int = False

		if is_int:

			# figure out if this user can modify this bet id
			try:
				prop_bet = ProposedBet.objects.get(id=bet_id)	
			except ProposedBet.DoesNotExist:
				prop_bet = None

			if prop_bet and request.user == prop_bet.user:
				# ok this user owns this prop, let them 'delete' it by setting remaining bets to zero
				prop_bet.remaining_wagers = 0
				prop_bet.save(update_fields=['remaining_wagers'])
				
				# send a message over that the bet is removed
				messages.success(request, 'Bet removed succesfully.')

			else:
				# send a message over that there was an error
				messages.error(request, 'You don\'t have permission to modify this bet.')

		else:
			# send a message over that there was an error
			messages.error(request, 'Bet ID must be an integer.')
	else:	
		# send a message over that there was an error
		messages.error(request, 'Something went wrong. Try again.')

	return HttpResponseRedirect('/bets/my_bets')

@login_required(login_url='/login/')
def accept_prop_bet(request):
	if request.method == 'GET' and 'id' in request.GET:
		# get the prop id from the get request
		bet_id = request.GET['id']

		# make sure it's an int
		try:
			int(bet_id)
			is_int = True

		except ValueError:
			is_int = False

		if is_int:
			# make sure bet exists
			try:
				prop_bet = ProposedBet.objects.get(id=bet_id)	
			except ProposedBet.DoesNotExist:
				prop_bet = None

			# make sure bet is someone elses and it has bets left and it isn't expired	
			if prop_bet \
				and request.user != prop_bet.user \
				and prop_bet.remaining_wagers > 0 \
				and prop_bet.end_date > timezone.now():
				
				# decrement remaining wagers
				prop_bet.remaining_wagers = prop_bet.remaining_wagers - 1
				prop_bet.save(update_fields=['remaining_wagers'])
				
				# create an accepted bet
				accepted_bet = AcceptedBet (accepted_prop=prop_bet, accepted_user=request.user)
				accepted_bet.save()

				# send a message over that the bet is accepted
				messages.success(request, 'Bet accepted succesfully.')

			else:
				# send a message over that there was an error
				messages.error(request, 'You don\'t have permission to modify this bet.')

		else:
			# send a message over that there was an error
			messages.error(request, 'Bet ID must be an integer.')
	else:	
		# send a message over that there was an error
		messages.error(request, 'Something went wrong. Try again.')

	return HttpResponseRedirect('/bets/open_bets')

@staff_member_required(login_url='/')
def admin_bets(request):
	# get all accepted bets that don't have a winner, but time is up
	expired_accepted_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=True, accepted_prop__end_date__lt=timezone.now())
	expired_prop_bets = ProposedBet.objects.filter(acceptedbet__in=expired_accepted_bets).distinct()

	# get other prop bets w/o winner, but time isn't up
	open_accepted_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=True, accepted_prop__end_date__gt=timezone.now())
	open_prop_bets = ProposedBet.objects.filter(acceptedbet__in=open_accepted_bets).distinct()

	# get all closed prop bets, those with a winner
	closed_accepted_bets = AcceptedBet.objects.filter(accepted_prop__won_bet__isnull=False)
	closed_prop_bets = ProposedBet.objects.filter(acceptedbet__in=closed_accepted_bets).distinct()


	return render(request, 'bets/base_admin_bets.html', {'nbar': 'admin_bets', 'expired_prop_bets': expired_prop_bets, 'open_prop_bets': open_prop_bets, 'closed_prop_bets': closed_prop_bets})
