from django import forms
from django.utils import timezone
import datetime as dt

class NewGameForm(forms.Form):
    team_a = forms.CharField(label='Team A', max_length=255,
            widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    team_b = forms.CharField(label='Team B', max_length=255,
            widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    price_per_square = forms.IntegerField(label='Price per square (USD)', initial=1,
            min_value=1, max_value=20,
            widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    use_shit_payout = forms.BooleanField(initial=True, required=False)

    squares_expiration_date = forms.DateTimeField(
        label='Expiration (mm/dd/yyyy 24hr eastern time)',
        help_text='Default is one week from today. Squares will no longer be available for others to buy after this datetime.',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off'}))

    def clean_squares_expiration_date(self):
        squares_expiration_date = self.cleaned_data['squares_expiration_date']

        if squares_expiration_date < timezone.now():
            raise forms.ValidationError("Datetime can't be in the past.")

        return squares_expiration_date
