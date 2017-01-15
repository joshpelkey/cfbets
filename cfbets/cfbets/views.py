from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from cfbets.forms import SignUpForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from bets.models import ProposedBet, AcceptedBet

def welcome(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/bets/my_bets')
	else:
		return render(request, 'base_welcome.html')

def sign_up(request):
	if request.method == 'POST':
        	form = SignUpForm(request.POST)
		# check the group id
		group_id = request.POST.get('group_id')
		if group_id != '' and group_id != 'cl3ms0n':
			form.add_error('group_id', 'Not a valid group id.')

        	elif form.is_valid():
            		form.save()
            		new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
			if new_user is not None:
            			login(request, new_user)
        			return HttpResponseRedirect("/")
			else:
				return HttpResponseRedirect("/login")

    	else:
        	form = SignUpForm()

	return render(request, 'base_sign_up.html', { 'form': form })

@login_required(login_url='/login/')
def profile(request):
	# get the current user
	current_user = request.user

	# all the form stuff
	if request.method == 'POST':
		user_form = UserForm(request.POST)
		user_profile_form = UserProfileForm(request.POST)
		if user_form.is_valid() and user_profile_form.is_valid():
			# need to save for current user NOT create a new one...
			user_form.save()
			profile = user_profile_form.save(commit = False)
			profile.user = current_user
			profile.save()
			messages.success(request, 'Profile saved successfully.')
			return HttpResponseRedirect("/profile")
	else:
		user_form = UserForm()
		user_profile_form = UserProfileForm()

	# all the status stuff

	# get win/tie/loss stats
	all_prop_bets = ProposedBet.objects.filter(user=current_user)
	total_won_bets = all_prop_bets.filter(won_bet__exact=1).count()
	total_tie_bets = all_prop_bets.filter(won_bet__exact=0).count()
	total_loss_bets = all_prop_bets.filter(won_bet__exact=-1).count()

	return render(request, 'base_profile.html', {'user_form': user_form, 'user_profile_form': user_profile_form, 'total_won_bets': total_won_bets, 'total_tie_bets': total_tie_bets, 'total_loss_bets': total_loss_bets})
