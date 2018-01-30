from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from bets.models import UserProfile
from django.contrib.auth import (
            authenticate, get_user_model, password_validation,
            )
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext, ugettext_lazy as _
from google.appengine.api import mail
from django.conf import settings

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

class UserProfileForm(forms.Form):
	first_name = forms.CharField(label = "First Name", max_length=255)
	last_name = forms.CharField(label = "Last Name", max_length=255)
	email = forms.EmailField(label="Email", disabled=True, required=False)
	get_prop_bet_emails = forms.BooleanField(required=False)
	get_accepted_bet_emails = forms.BooleanField(required=False)

class MyPasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        email_subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        email_subject = ''.join(email_subject.splitlines())
        email_body = loader.render_to_string(email_template_name, context)

        #email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        #if html_email_template_name is not None:
        #    html_email = loader.render_to_string(html_email_template_name, context)
        #    email_message.attach_alternative(html_email, 'text/html')

        DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        email_message = mail.EmailMessage(
                sender=DEFAULT_FROM_EMAIL,
                subject=email_subject)

        email_message.to=to_email
        email_message.body=email_body

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)
