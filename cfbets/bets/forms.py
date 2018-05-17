from django import forms
from django.utils import timezone
import datetime as dt


class PlaceBetsForm(forms.Form):
    bet = forms.CharField(label='Bet', max_length=500, widget=forms.TextInput(
        attrs={'placeholder': 'E.g. Clemson -48.5 over USCjr', 'autocomplete': 'off'}))

    bet_amount = forms.IntegerField(
        label='Bet Amount (USD)',
        initial=5,
        min_value=1,
        max_value=20,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off'}))

    qty_allowed = forms.IntegerField(
        label='Qty Allowed',
        initial=2,
        min_value=1,
        max_value=10,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off'}))

    bet_expiration_date = forms.DateTimeField(
        label='Expiration (mm/dd/yyyy 24hr eastern time)',
        help_text='Default is one week from today. Bet will no longer be available for others to accept after this datetime.',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off'}))

    def clean_bet_expiration_date(self):
        bet_expiration_date = self.cleaned_data['bet_expiration_date']

        if bet_expiration_date < timezone.now():
            raise forms.ValidationError("Datetime can't be in the past.")

        return bet_expiration_date
