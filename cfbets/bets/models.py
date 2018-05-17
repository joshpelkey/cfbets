from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Proposed Bet holds all user's prop bets, which may or may not get accepted.

class ProposedBet (models.Model):
    user = models.ForeignKey(User)
    prop_text = models.CharField(max_length=256)
    prop_wager = models.IntegerField()
    max_wagers = models.IntegerField()
    remaining_wagers = models.IntegerField()
    end_date = models.DateTimeField()

    # win / loss / tie choices
    WIN = 1
    LOSS = -1
    TIE = 0
    WIN_LOSS_TIE_CHOICES = ((WIN, 'Win'), (LOSS, 'Loss'), (TIE, 'Tie'))

    won_bet = models.IntegerField(
        choices=WIN_LOSS_TIE_CHOICES,
        null=True,
        blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['end_date']
        verbose_name = 'Proposed Bet'
    verbose_name_plural = 'Proposed Bets'

    def __unicode__(self):
        return "{id: %d, user: '%s', prop: '%s', wager: '%d'}" % (
            self.id, self.user.get_full_name(), self.prop_text, self.prop_wager)

# Accepted bet holds all prop bets that are accepted by another user
class AcceptedBet (models.Model):
    accepted_prop = models.ForeignKey(ProposedBet)
    accepted_user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['accepted_prop__end_date']
        verbose_name = 'Accepted Bet'
    verbose_name_plural = 'Accpeted Bets'

    def __unicode__(self):
        return "{id: %d, proposer: '%s', proposee: '%s', prop_bet: '%s', wager: '%d'}" % (self.id, self.accepted_prop.user.get_full_name(
        ), self.accepted_user.get_full_name(), self.accepted_prop.prop_text, self.accepted_prop.prop_wager)

# User Profile table holds some user info specific to this betting app

class UserProfile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_balance = models.IntegerField(
        default=0,
        help_text='The user\'s current balance. Every time the user settles up, the current balance is reset to zero.')
    overall_winnings = models.IntegerField(
        default=0, help_text='The user\'s overall winnings since joining.')
    get_prop_bet_emails = models.BooleanField(default=True)
    get_accepted_bet_emails = models.BooleanField(default=True)
    last_payment = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
    verbose_name_plural = 'User Profiles'

    def __str__(self):
        return "%s Profile" % (self.user.get_full_name())

# hook user profile to user table, so that it's created when a user is created
#

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

#
# end user profile hooks

# User Profile Audit creates an audit trail each time a user's winnings
# are updated due to an accepted bet being closed.

class UserProfileAudit (models.Model):
    user = models.ForeignKey(User, related_name='user_profile_user')
    admin_user = models.ForeignKey(User, related_name='user_profile_admin')
    accepted_bet = models.ForeignKey(AcceptedBet)
    original_current_balance = models.IntegerField()
    new_current_balance = models.IntegerField()
    original_overall_winnings = models.IntegerField()
    new_overall_winnings = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile Audit'
    verbose_name_plural = 'User Profile Audits'

    def __str__(self):
        return "{id: %d, user: '%s', bet: '%s', orig_winnings: '%d', new_winnings: '%d'}" % (
            self.id, self.user.get_full_name(), self.accepted_bet, self.original_overall_winnings, self.new_overall_winnings)
