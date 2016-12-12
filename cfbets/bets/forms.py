from django import forms
from django.utils import timezone

class PlaceBetsForm(forms.Form):
	qty_allowed = forms.IntegerField(label='Qty Allowed', initial=2, min_value=1, max_value=10)
	bet = forms.CharField(label='Bet', max_length=500, widget=forms.TextInput(attrs={'placeholder': 'E.g. Clemson -48.5 over USCjr', 'size': '50'}))
	bet_amount = forms.IntegerField(label='Bet Amount (USD)', initial=5, min_value=1, max_value=20)
	bet_expiration_date = forms.DateTimeField(label='Expiration Date/Time', help_text='Bet will no longer be available for others to accept after this datetime.')

	def clean_bet_expiration_date(self):
		bet_expiration_date = self.cleaned_data['bet_expiration_date']
		if bet_expiration_date < timezone.now():
			raise forms.ValidationError("Datetime can't be in the past.")
		return bet_expiration_date
