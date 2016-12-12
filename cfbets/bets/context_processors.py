# bets/context_processors.py
from bets.forms import PlaceBetsForm
from django.core.urlresolvers import reverse
from bets import views

def place_bets_form_context_processor(request):
	return {
		'place_bets_form': PlaceBetsForm(),
		'place_bets_form_url': reverse('bets:place_bets_form_process', kwargs={'next_url': request.path})
	}
