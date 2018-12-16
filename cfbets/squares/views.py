from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from bets.models import ProposedBet, AcceptedBet, UserProfile
from django.contrib.auth.models import User

# Create your views here.

def squares(request):
    return HttpResponseRedirect('/squares/my_squares')

@login_required(login_url='/login/')
def my_squares(request):

    return render(request,
            'squares/squares_base_my_squares.html',
            {'nbar': 'my_squares'})

@login_required(login_url='/login/')
def all_squares(request):

    return render(request,
            'squares/squares_base_all_squares.html',
            {'nbar': 'all_squares'})

@staff_member_required(login_url='/')
def admin_squares(request):
    return render(request, 'squares/squares_base_admin_squares.html')
