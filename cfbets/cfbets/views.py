from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from cfbets.forms import SignUpForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

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
def account_settings(request):
	return render(request, 'base_account_settings.html')
