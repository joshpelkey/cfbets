from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from cfbets.forms import SignUpForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from bets.models import ProposedBet, AcceptedBet, UserProfile
from common.stats import *
from django.contrib.auth.models import User

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
            new_user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])

            if new_user is not None:
                login(request, new_user)
                return HttpResponseRedirect("/")

            else:
                return HttpResponseRedirect("/login")

    else:
        form = SignUpForm()

    return render(request, 'base_sign_up.html', {'form': form})

@login_required(login_url='/login/')
def profile(request):

    # get the current user
    current_user = User.objects.get(id=request.user.id)

    # get the current user profile
    current_user_profile = UserProfile.objects.get(user=current_user)

    # all the form stuff
    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST)
        if user_profile_form.is_valid():
            # save data for current user / user profile
            current_user.first_name = user_profile_form.cleaned_data['first_name']
            current_user.last_name = user_profile_form.cleaned_data['last_name']
            current_user_profile.get_prop_bet_emails = user_profile_form.cleaned_data[
                'get_prop_bet_emails']
            current_user_profile.get_accepted_bet_emails = user_profile_form.cleaned_data[
                'get_accepted_bet_emails']
            current_user.save(update_fields=['first_name', 'last_name'])
            current_user_profile.save(
                update_fields=[
                    'get_prop_bet_emails',
                    'get_accepted_bet_emails'])

            messages.success(request, 'Profile saved successfully.')
            return HttpResponseRedirect("/profile")
    else:
        user_profile_form = UserProfileForm(
            initial={
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'email': current_user.email,
                'get_prop_bet_emails': current_user_profile.get_prop_bet_emails,
                'get_accepted_bet_emails': current_user_profile.get_accepted_bet_emails})

    total_won_bets = get_total_wins(current_user)
    total_loss_bets = get_total_losses(current_user)
    total_tie_bets = get_total_ties(current_user)

    return render(request,
                  'base_profile.html',
                  {'user_profile_form': user_profile_form,
                   'total_won_bets': total_won_bets,
                   'total_tie_bets': total_tie_bets,
                   'total_loss_bets': total_loss_bets})
