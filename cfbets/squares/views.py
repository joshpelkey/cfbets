import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from squares.models import SquaresProposed, SquaresAccepted
from squares.forms import NewGameForm
from django.contrib.auth.models import User

# Create your views here.

def squares(request):
    return HttpResponseRedirect('/squares/my_squares')

@login_required(login_url='/login/')
def my_squares(request):

    current_user = request.user

    # get available squares, i.e. those games that are not expired yet and have
    # squares remaining
    available_squares = SquaresProposed.objects.filter(remaining_squares__gt=0,
            end_date__gt=timezone.now())

    # get all your squares that are not yet expired
    my_open_squares = SquaresAccepted.objects.filter(accepted_user=current_user,
            squares_game__end_date__gt=timezone.now())

    # create a nice dictionary that sums up your total squares for each game
    # proposed
    my_open_squares_sum = my_open_squares.values('squares_game__team_a',
    'squares_game__team_b', 'squares_game__price_per_square',
    'squares_game__end_date').annotate(Sum('num_squares'))

    # sqaures games you are participating in that are either in progress or
    # awaiting an admin to set winners
    my_active_squares = SquaresAccepted.objects.filter(accepted_user=current_user,
            squares_game__remaining_squares__exact=0, squares_game__closed=False)

    # create a nice dictionary that sums up your total squares for each game
    # proposed that are in progress or awaiting winners
    my_active_squares_sum = my_active_squares.values('squares_game__team_a',
    'squares_game__team_b', 'squares_game__price_per_square',
    'squares_game__end_date').annotate(Sum('num_squares'))

    # get closed squares that you particpated in
    my_closed_squares = SquaresAccepted.objects.filter(accepted_user=current_user,
            squares_game__closed=True)

    # create a nice dictionary that sums up total squares for each closed game
    # that you particpated in
    my_closed_squares_sum = my_closed_squares.values('squares_game__team_a',
    'squares_game__team_b', 'squares_game__price_per_square',
    'squares_game__end_date').annotate(Sum('num_squares'))

    return render(request,
            'squares/squares_base_my_squares.html',
            {'nbar': 'my_squares',
                'available_squares': available_squares,
                'my_open_squares': my_open_squares_sum,
                'my_active_squares': my_active_squares_sum,
                'my_closed_squares': my_closed_squares_sum})

@login_required(login_url='/login/')
def all_squares(request):

    # get available squares, i.e. those games that are not expired yet and have
    # squares remaining
    available_squares = SquaresProposed.objects.filter(remaining_squares__gt=0,
            end_date__gt=timezone.now())

    # get active games (and make sure we've assigned some squares already)
    active_squares = SquaresProposed.objects.filter(remaining_squares__exact=0,
            assigned_squares__isnull=False, closed=False)

    # get closed games
    closed_squares = SquaresProposed.objects.filter(remaining_squares__exact=0,
            closed=True)

    return render(request,
            'squares/squares_base_all_squares.html',
            {'nbar': 'all_squares',
                'available_squares': available_squares,
                'active_squares': active_squares,
                'closed_squares': closed_squares})

@staff_member_required(login_url='/')
def admin_squares(request):

    # get the current user
    current_user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        new_game_form = NewGameForm(request.POST)

        if new_game_form.is_valid():
            # save data for new squares game
            new_game = SquaresProposed(
                    user = current_user,
                    team_a = new_game_form.cleaned_data['team_a'],
                    team_b = new_game_form.cleaned_data['team_b'],
                    price_per_square = new_game_form.cleaned_data['price_per_square'],
                    use_shit_payout = new_game_form.cleaned_data['use_shit_payout'],
                    end_date = new_game_form.cleaned_data['squares_expiration_date'],
                    created_on = timezone.now(),
                    modified_on = timezone.now())

            #save to the db
            new_game.save()

            # save the url to know where to redirect
            response = {'url': '/squares/admin_squares'}

            # send a message over that the game is proposed
            messages.success(request, 'New squares game proposed!')

            return HttpResponse(
                    json.dumps(response),
                    content_type='application/json')

        else:
            # form not valid, do something about it
            return render(request, 'squares/new_game.html',
                    {'new_game_form': new_game_form}, status=400)

    else:
        # not a POST, display the form instead
        new_game_form = NewGameForm()

    return render(request, 'squares/squares_base_admin_squares.html',
            {'new_game_form': new_game_form})
