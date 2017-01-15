from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from bets.models import UserProfile

class SignUpForm(UserCreationForm):
    # declare the fields you will show
    username = forms.EmailField(label="Username", help_text="Username should be your email address.")
    first_name = forms.CharField(label = "First Name", widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    last_name = forms.CharField(label = "Last Name")
    group_id = forms.CharField(label = "Group ID", help_text="Top secret code to register for this site.")

 
    # this sets the order of the fields
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "group_id", "password1", "password2", )
 
    # this redefines the save function to include the fields you added
    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
 
    	if commit:
        	user.save()
	return user

class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ["first_name", "last_name", "email"]

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ["get_prop_bet_emails", "get_accepted_bet_emails"]
