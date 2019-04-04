import json
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from common.stats import *
from django.conf import settings
from bets.forms import PlaceBetsForm
from bets.models import ProposedBet, AcceptedBet, UserProfile, UserProfileAudit, User
from django.db.models import Sum

# Create your views here.

def bets(request):
    return HttpResponseRedirect('/bets/my_bets')

@login_required(login_url='/login/')
def your_stats(request):

    # get the current user
    current_user = request.user

    # get win, loss, tie stats
    total_wins = get_total_wins(current_user)
    total_losses = get_total_losses(current_user)
    total_ties = get_total_ties(current_user)
    win_percentage = get_win_percentage(current_user)

    # throw it in a dictionary
    win_loss_tie = {
        'wins': total_wins,
        'losses': total_losses,
        'ties': total_ties,
        'win_percentage': win_percentage}

    # get total proposed and total proposed won bets
    total_proposed = get_total_proposed(current_user)

    # get total bets you accepted and total bets won you accepted
    total_accepted = get_total_accepted(current_user)

    # get bet against report
    bet_against_report = get_bet_against_report(current_user)

    # get total bets by week list (both proposed and accepted)
    total_bets_by_week = get_total_bets_by_week(current_user)

    # get total money by week list
    total_money_by_week = get_total_money_by_week(current_user)

    # get week start info
    week_start = get_week_start()

    return render(request,
                  'bets/base_your_stats.html',
                  {'nbar': 'stats',
                   'win_loss_tie': win_loss_tie,
                   'total_proposed': total_proposed,
                   'total_accepted': total_accepted,
                   'bet_against_report': bet_against_report,
                   'week_start': week_start,
                   'total_bets_by_week': total_bets_by_week,
                   'total_money_by_week': total_money_by_week})

@login_required(login_url='/login/')
def global_stats(request):

    # get the current user
    current_user = request.user

    global_stats = get_global_stats
    global_betting_report = get_global_betting_report
    global_bettingest_couples = get_bettingest_couples
    global_total_bets_by_week = get_global_total_bets_by_week

    # get week start info
    week_start = get_week_start()

    return render(request,
                  'bets/base_global_stats.html',
                  {'nbar': 'stats',
                   'global_stats': global_stats,
                   'global_total_bets_by_week': global_total_bets_by_week,
                   'week_start': week_start,
                   'global_betting_report': global_betting_report,
                   'global_bettingest_couples': global_bettingest_couples})

@login_required(login_url='/login/')
def my_bets(request):

    # get the current user
    current_user = request.user

    # get all their proposed bets that have remaining bets and have end dates
    # past now
    your_open_bets = ProposedBet.objects.filter(
        user=current_user,
        remaining_wagers__gt=0,
        end_date__gt=timezone.now(),
        won_bet__isnull=True)

    # your active bets, i.e. those bets you have accepted and your bets that
    # other users have accepted
    your_accepted_bets = AcceptedBet.objects.filter(
        accepted_user=current_user, accepted_prop__won_bet__isnull=True)

    your_bets_accepted_by_others = AcceptedBet.objects.filter(
        accepted_prop__user=current_user, accepted_prop__won_bet__isnull=True)

    your_active_bets = your_accepted_bets | your_bets_accepted_by_others

    your_active_bets_count = your_active_bets.count()

    # your active bets, total money bet
    your_active_bets_total_amount = your_active_bets.aggregate(
        Sum('accepted_prop__prop_wager'))

    your_active_bets_total_amount = your_active_bets_total_amount.values()[0]

    return render(request,
                  'bets/base_my_bets.html',
                  {'nbar': 'my_bets',
                   'your_open_bets': your_open_bets,
                   'your_active_bets': your_active_bets,
                   'your_active_bets_count': your_active_bets_count,
                   'your_active_bets_total_amount': your_active_bets_total_amount})

@login_required(login_url='/login/')
def open_bets(request):

    # used for expiring soon and new bet tags
    tomorrow = timezone.now() + timezone.timedelta(days=1)
    yesterday = timezone.now() + timezone.timedelta(days=-1)

    # get the current user
    current_user = request.user

    # get all open prop bets from other users
    open_bets = ProposedBet.objects.filter(
        remaining_wagers__gt=0,
        end_date__gt=timezone.now(),
        won_bet__isnull=True).exclude(
        user=current_user)

    # get all bets created in past 24 hours
    new_bets = ProposedBet.objects.filter(
        remaining_wagers__gt=0,
        end_date__gt=timezone.now(),
        created_on__gt=yesterday,
        won_bet__isnull=True).exclude(
        user=current_user)

    # get all bets expiring in next 24 hours
    closing_soon_bets = ProposedBet.objects.filter(
        remaining_wagers__gt=0,
        end_date__gt=timezone.now(),
        end_date__lt=tomorrow,
        won_bet__isnull=True).exclude(
        user=current_user)

    return render(request,
                  'bets/base_open_bets.html',
                  {'nbar': 'open_bets',
                   'open_bets': open_bets,
                   'new_bets': new_bets,
                   'closing_soon_bets': closing_soon_bets})

@login_required(login_url='/login/')
def all_bets(request):

    # get all active accepted bets
    all_active_bets = AcceptedBet.objects.filter(
        accepted_prop__won_bet__isnull=True)

    return render(request, 'bets/base_all_bets.html',
                  {'nbar': 'all_bets', 'all_active_bets': all_active_bets})

class MyCompletedBetsJson(BaseDatatableView):
    order_columns = ['accepted_prop__prop_text',
                     'accepted_prop__prop_wager', '', '']

    def get_initial_queryset(self):
        current_user = self.request.user
        your_accepted_bets = AcceptedBet.objects.filter(
            accepted_user=current_user, accepted_prop__won_bet__isnull=False)

        your_bets_accepted_by_others = AcceptedBet.objects.filter(
            accepted_prop__user=current_user, accepted_prop__won_bet__isnull=False)

        your_closed_bets = your_accepted_bets | your_bets_accepted_by_others
        return your_closed_bets.order_by('-accepted_prop__modified_on')

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get(u'search[value]', None)

        if sSearch:
            qs = qs.filter(
                accepted_prop__prop_text__istartswith=sSearch) | qs.filter(
                accepted_user__first_name__istartswith=sSearch) | qs.filter(
                accepted_user__last_name__istartswith=sSearch) | qs.filter(
                accepted_prop__user__first_name__istartswith=sSearch) | qs.filter(
                    accepted_prop__user__last_name__istartswith=sSearch)

        return qs

    def prepare_results(self, qs):
        json_data = []
        current_user = self.request.user

        for item in qs:

            # figure out who the bet was against
            bet_against_user = ''
            if item.accepted_prop.user == current_user:
                bet_against_user = item.accepted_user.get_full_name()
            else:
                bet_against_user = item.accepted_prop.user.get_full_name()

            who_won = ''
            if item.accepted_prop.get_won_bet_display() == "Win":
                who_won = item.accepted_prop.user.get_full_name()
            elif item.accepted_prop.get_won_bet_display() == "Loss":
                who_won = item.accepted_user.get_full_name()
            else:
                who_won = 'push'

            json_data.append([
                item.accepted_prop.prop_text,
                '$' + str(item.accepted_prop.prop_wager),
                bet_against_user,
                who_won
            ])

        return json_data

class AllBetsJson(BaseDatatableView):
    order_columns = [
        'accepted_prop__user',
        'accepted_user',
        'accepted_prop__prop_text',
        'accepted_prop__prop_wager',
        '']

    def get_initial_queryset(self):
        return AcceptedBet.objects.filter(
            accepted_prop__won_bet__isnull=False).order_by('-accepted_prop__modified_on')

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get(u'search[value]', None)

        if sSearch:
            qs = qs.filter(
                accepted_prop__prop_text__istartswith=sSearch) | qs.filter(
                accepted_user__first_name__istartswith=sSearch) | qs.filter(
                accepted_user__last_name__istartswith=sSearch) | qs.filter(
                accepted_prop__user__first_name__istartswith=sSearch) | qs.filter(
                    accepted_prop__user__last_name__istartswith=sSearch)

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:

            who_won = ''
            if item.accepted_prop.get_won_bet_display() == "Win":
                who_won = item.accepted_prop.user.get_full_name()
            elif item.accepted_prop.get_won_bet_display() == "Loss":
                who_won = item.accepted_user.get_full_name()
            else:
                who_won = 'push'

            json_data.append([
                item.accepted_prop.user.get_full_name(),
                item.accepted_user.get_full_name(),
                item.accepted_prop.prop_text,
                '$' + str(item.accepted_prop.prop_wager),
                who_won
            ])

        return json_data

class AdminBetsJson(BaseDatatableView):
    order_columns = ['user', 'prop_text', '', '']

    def get_initial_queryset(self):
        closed_accepted_bets = AcceptedBet.objects.filter(
            accepted_prop__won_bet__isnull=False)
        closed_prop_bets = ProposedBet.objects.filter(
            acceptedbet__in=closed_accepted_bets).distinct().order_by('-modified_on')

        return closed_prop_bets

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get(u'search[value]', None)

        if sSearch:
            qs = qs.filter(
                prop_text__istartswith=sSearch) | qs.filter(
                user__first_name__istartswith=sSearch) | qs.filter(
                user__last_name__istartswith=sSearch)

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:

            completed_bet_info = [
                item.user.get_full_name(),
                item.prop_text,
                item.id]
            json_data.append([
                item.user.get_full_name(),
                item.prop_text,
                item.get_won_bet_display(),
                completed_bet_info
            ])

        return json_data

@login_required(login_url='/login/')
def place_bets_form_process(request, next_url):

    if request.method == 'POST':
        form = PlaceBetsForm(request.POST)

        if form.is_valid():
            # gather form entries and save to DB
            new_bet = ProposedBet(
                user=request.user,
                prop_text=form.cleaned_data['bet'],
                prop_wager=form.cleaned_data['bet_amount'],
                max_wagers=form.cleaned_data['qty_allowed'],
                remaining_wagers=form.cleaned_data['qty_allowed'],
                end_date=form.cleaned_data['bet_expiration_date'],
                created_on=timezone.now(),
                modified_on=timezone.now())
            # save to the db
            new_bet.save()

            # post to slack
            slack_webhook_url = settings.SLACK_WEBHOOK_URL
            slack_data = {"attachments":[{"fallback":"A new bet was posted.", \
                "color":"#36a64f", \
                "pretext":"A new bet was posted, <!here>:", \
                "author_name":request.user.get_full_name(), \
                "title":"($" + str(form.cleaned_data['bet_amount']) + ") " \
                + form.cleaned_data['bet'],"title_link":"https://cfbets.us/bets/open_bets/"}]}

            slack_response = requests.post(slack_webhook_url, json=slack_data)

            # save the url to know where to redirect
            response = {'url': next_url}

            # send a message over that the bet is complete
            messages.success(request, 'Bet submitted succesfully.')

            return HttpResponse(
                json.dumps(response),
                content_type='application/json')
        else:
            # form isn't valid, return to ajax call with error and form with
            # errors
            return render(request, 'bets/place_bets.html',
                          {'place_bets_form': form}, status=400)

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
                # ok this user owns this prop, let them 'delete' it by setting
                # remaining bets to zero
                prop_bet.remaining_wagers = 0
                prop_bet.save(
                    update_fields=[
                        'remaining_wagers',
                        'modified_on'])

                # send a message over that the bet is removed
                messages.success(request, 'Bet removed succesfully.')

            else:
                # send a message over that there was an error
                messages.error(
                    request, 'You don\'t have permission to modify this bet.')

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

            # make sure bet is someone elses and it has bets left and it isn't
            # expired
            if prop_bet \
                    and request.user != prop_bet.user \
                    and prop_bet.remaining_wagers > 0 \
                    and prop_bet.end_date > timezone.now():

                # decrement remaining wagers
                prop_bet.remaining_wagers = prop_bet.remaining_wagers - 1
                prop_bet.save(
                    update_fields=[
                        'remaining_wagers',
                        'modified_on'])

                # create an accepted bet
                accepted_bet = AcceptedBet(
                    accepted_prop=prop_bet, accepted_user=request.user)
                accepted_bet.save()

                # send a message over that the bet is accepted
                messages.success(request, 'Bet accepted successfully.')

                # send an email to the propser, if they have their setting
                # enabled
                current_site = get_current_site(request)
                domain = current_site.domain

                user_profile = UserProfile.objects.get(user=prop_bet.user)
                if user_profile.get_accepted_bet_emails:
                    email_message = 'Accepted Bet:\n' \
                        + '($' + str(prop_bet.prop_wager) + ') ' + prop_bet.prop_text + \
                        '\n\nAccepted By:\n' \
                        + request.user.get_full_name() + \
                        '\n\nhttps://' + domain + '/bets/my_bets/'
                    send_list = []
                    send_list.append(prop_bet.user.email)
                    send_mail(
                        'cfbets: Bet Accepted',
                        email_message,
                        'yojdork@gmail.com',
                        send_list,
                        fail_silently=True,
                    )
            else:
                # send a message over that there was an error
                messages.error(
                    request, 'You don\'t have permission to modify this bet.')

        else:
            # send a message over that there was an error
            messages.error(request, 'Bet ID must be an integer.')
    else:
        # send a message over that there was an error
        messages.error(request, 'Something went wrong. Try again.')

    return HttpResponseRedirect('/bets/open_bets')

@csrf_exempt
@login_required(login_url='/login/')
def check_duplicate_bet(request):

    if request.method == 'POST':
        # get the id in the post
        prop_id = request.POST.get('id')
        response_data = {}
        # check and see if this user has already accepted this bet at least
        # once
        prop_bet = ProposedBet.objects.get(id=prop_id)
        accepted_bets = AcceptedBet.objects.filter(
            accepted_prop=prop_bet, accepted_user=request.user)
        if accepted_bets:
            response_data['is_duplicate'] = 'True'
        else:
            response_data['is_duplicate'] = 'False'

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this should not happen"}),
            content_type="application/json"
        )

@staff_member_required(login_url='/')
def admin_bets(request):

    # get all accepted bets that don't have a winner, but time is up
    expired_accepted_bets = AcceptedBet.objects.filter(
        accepted_prop__won_bet__isnull=True,
        accepted_prop__end_date__lt=timezone.now())
    expired_prop_bets = ProposedBet.objects.filter(
        acceptedbet__in=expired_accepted_bets).distinct()

    # get other prop bets w/o winner, but time isn't up
    open_accepted_bets = AcceptedBet.objects.filter(
        accepted_prop__won_bet__isnull=True,
        accepted_prop__end_date__gt=timezone.now())
    open_prop_bets = ProposedBet.objects.filter(
        acceptedbet__in=open_accepted_bets).distinct()

    return render(request,
                  'bets/base_admin_bets.html',
                  {'nbar': 'admin_bets',
                   'expired_prop_bets': expired_prop_bets,
                   'open_prop_bets': open_prop_bets})

@staff_member_required(login_url='/')
def set_prop_bet(request):

    if request.method == 'GET' and 'id' in request.GET and 'status' in request.GET:

        # get the prop id and status from the get request
        bet_id = request.GET['id']
        status = request.GET['status']

        # make sure betId is an int
        try:
            int(bet_id)
            is_int = True

        except ValueError:
            is_int = False

        if is_int and status in ('Win', 'Loss', 'Tie'):
            win_loss_choices = {'Win': 1, 'Loss': -1, 'Tie': 0}

            # get the prop bet
            # make sure bet exists
            try:
                prop_bet = ProposedBet.objects.get(id=bet_id)
            except ProposedBet.DoesNotExist:
                prop_bet = None

            # make sure bet exists and won_bet is null
            if prop_bet and prop_bet.won_bet is None:
                # mark the prop with the appropriate winner
                prop_bet.won_bet = win_loss_choices[status]
                prop_bet.save(update_fields=['won_bet', 'modified_on'])

                # update winnings for the winner and loser, including the audit table
                # get all accepted bets and loop them
                current_admin_user = request.user
                proposer_profile = UserProfile.objects.get(user=prop_bet.user)
                wager = prop_bet.prop_wager
                accepted_bets = AcceptedBet.objects.filter(
                    accepted_prop=prop_bet)
                for bet in accepted_bets:
                    # get the proposee's user profile
                    proposee_profile = UserProfile.objects.get(
                        user=bet.accepted_user)

                    # if proposer won, proposee lost
                    if status == 'Win':
                        # update proposer
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposer_profile.current_balance += wager
                        proposer_profile.overall_winnings += wager
                        proposer_profile.save()

                        # update audit for propser
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_profile.current_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_profile.overall_winnings)
                        proposer_profile_audit.save()

                        # update proposee
                        proposee_orig_balance = proposee_profile.current_balance
                        proposee_orig_winnings = proposee_profile.overall_winnings
                        proposee_profile.current_balance -= wager
                        proposee_profile.overall_winnings -= wager
                        proposee_profile.save()

                        # update audit for propsee
                        proposee_profile_audit = UserProfileAudit(
                            user=bet.accepted_user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposee_orig_balance,
                            new_current_balance=proposee_profile.current_balance,
                            original_overall_winnings=proposee_orig_winnings,
                            new_overall_winnings=proposee_profile.overall_winnings)
                        proposee_profile_audit.save()

                    # if proposer lost, proposee won
                    elif status == 'Loss':
                        # update proposer
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposer_profile.current_balance -= wager
                        proposer_profile.overall_winnings -= wager
                        proposer_profile.save()

                        # update audit for propser
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_profile.current_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_profile.overall_winnings)
                        proposer_profile_audit.save()

                        # update proposee
                        proposee_orig_balance = proposee_profile.current_balance
                        proposee_orig_winnings = proposee_profile.overall_winnings
                        proposee_profile.current_balance += wager
                        proposee_profile.overall_winnings += wager
                        proposee_profile.save()

                        # update audit for propsee
                        proposee_profile_audit = UserProfileAudit(
                            user=bet.accepted_user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposee_orig_balance,
                            new_current_balance=proposee_profile.current_balance,
                            original_overall_winnings=proposee_orig_winnings,
                            new_overall_winnings=proposee_profile.overall_winnings)
                        proposee_profile_audit.save()

                    # if push
                    elif status == 'Tie':
                        # Add Audit entries
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposee_orig_balance = proposee_profile.current_balance
                        proposee_orig_winnings = proposee_profile.overall_winnings

                        # update audit for propser
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_orig_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_orig_winnings)
                        proposer_profile_audit.save()

                        # update audit for propsee
                        proposee_profile_audit = UserProfileAudit(
                            user=bet.accepted_user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposee_orig_balance,
                            new_current_balance=proposee_orig_balance,
                            original_overall_winnings=proposee_orig_winnings,
                            new_overall_winnings=proposee_orig_winnings)
                        proposee_profile_audit.save()

                # send a message over that the bet is marked succesfully
                messages.success(request, 'Bet marked succesfully.')

            else:
                messages.error(
                    request, 'You don\'t have permission to modify this bet.')

        else:
            # send a message over that there was an error
            messages.error(
                request, 'Something went wrong with the GET request URL.')

    return HttpResponseRedirect('/bets/admin_bets')

@staff_member_required(login_url='/')
def undo_prop_bet(request):

    if request.method == 'GET' and 'id' in request.GET:
        # get the prop id and status from the get request
        bet_id = request.GET['id']

        # make sure betId is an int
        try:
            int(bet_id)
            is_int = True

        except ValueError:
            is_int = False

        if is_int:
            # get the prop bet
            # make sure bet exists
            try:
                prop_bet = ProposedBet.objects.get(id=bet_id)
            except ProposedBet.DoesNotExist:
                prop_bet = None

            # make sure bet exists and won_bet is null
            if prop_bet and prop_bet.won_bet is not None:
                # remember who won
                original_win_loss = prop_bet.won_bet

                # set won_bet back to none
                prop_bet.won_bet = None
                prop_bet.save(update_fields=['won_bet', 'modified_on'])

                # save some info
                current_admin_user = request.user
                proposer_profile = UserProfile.objects.get(user=prop_bet.user)
                wager = prop_bet.prop_wager
                accepted_bets = AcceptedBet.objects.filter(
                    accepted_prop=prop_bet)

                for bet in accepted_bets:
                    # get the proposee's user profile
                    proposee_profile = UserProfile.objects.get(
                        user=bet.accepted_user)

                    # update winnings for original winner and loser and the audit table
                    # if the proposer won
                    if original_win_loss == 1:
                        # update proposer
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposer_profile.current_balance -= wager
                        proposer_profile.overall_winnings -= wager
                        proposer_profile.save()

                        # update audit for propser
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_profile.current_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_profile.overall_winnings)
                        proposer_profile_audit.save()

                        # update proposee
                        proposee_orig_balance = proposee_profile.current_balance
                        proposee_orig_winnings = proposee_profile.overall_winnings
                        proposee_profile.current_balance += wager
                        proposee_profile.overall_winnings += wager
                        proposee_profile.save()

                        # update audit for propsee
                        proposee_profile_audit = UserProfileAudit(
                            user=bet.accepted_user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposee_orig_balance,
                            new_current_balance=proposee_profile.current_balance,
                            original_overall_winnings=proposee_orig_winnings,
                            new_overall_winnings=proposee_profile.overall_winnings)
                        proposee_profile_audit.save()

                    # if the proposee won
                    elif original_win_loss == -1:
                        # update proposer
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposer_profile.current_balance += wager
                        proposer_profile.overall_winnings += wager
                        proposer_profile.save()

                        # update audit for propser
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_profile.current_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_profile.overall_winnings)
                        proposer_profile_audit.save()

                        # update proposee
                        proposee_orig_balance = proposee_profile.current_balance
                        proposee_orig_winnings = proposee_profile.overall_winnings
                        proposee_profile.current_balance -= wager
                        proposee_profile.overall_winnings -= wager
                        proposee_profile.save()

                        # update audit for propsee
                        proposee_profile_audit = UserProfileAudit(
                            user=bet.accepted_user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposee_orig_balance,
                            new_current_balance=proposee_profile.current_balance,
                            original_overall_winnings=proposee_orig_winnings,
                            new_overall_winnings=proposee_profile.overall_winnings)
                        proposee_profile_audit.save()

                    # if it was a tie
                    elif original_win_loss == 0:
                        # Add Audit entries
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposee_orig_balance = proposee_profile.current_balance
                        proposee_orig_winnings = proposee_profile.overall_winnings

                        # update audit for propser
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_orig_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_orig_winnings)
                        proposer_profile_audit.save()

                        # update audit for propsee
                        proposee_profile_audit = UserProfileAudit(
                            user=bet.accepted_user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposee_orig_balance,
                            new_current_balance=proposee_orig_balance,
                            original_overall_winnings=proposee_orig_winnings,
                            new_overall_winnings=proposee_orig_winnings)
                        proposee_profile_audit.save()

                # send a message over that the bet is undone
                messages.success(request, 'Bet undone succesfully.')
            else:
                # send a message over that there was an error
                messages.error(
                    request, 'You don\'t have permission to modify this bet.')

        else:
            # send a message over that there was an error
            messages.error(request, 'Bet ID must be an integer.')

    return HttpResponseRedirect('/bets/admin_bets')
