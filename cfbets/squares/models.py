from __future__ import unicode_literals

from django.db import models
from django_mysql.models import ListCharField
from django.contrib.auth.models import User

# SquaresProposed holds all squares games...that have been proposed. amirite

class SquaresProposed(models.Model):
    user = models.ForeignKey(User)
    team_a = models.CharField(max_length=256)
    team_b = models.CharField(max_length=256)
    price_per_square = models.IntegerField()
    remaining_squares = models.IntegerField(default=100)
    end_date = models.DateTimeField()
    closed = models.BooleanField(default=False)
    assigned_squares = models.TextField(null=True, blank=True)

    use_shit_payout = models.BooleanField()
    shit_22_user = models.ForeignKey(User, related_name='shit_22_user',
            null=True, blank=True)
    shit_55_user = models.ForeignKey(User, related_name='shit_55_user',
            null=True, blank=True)
    shit_99_user = models.ForeignKey(User, related_name='shit_99_user',
            null=True, blank=True)
    q1_winning_user = models.ForeignKey(User, related_name='q1_winning_user',
            null=True, blank=True)
    q2_winning_user = models.ForeignKey(User, related_name='q2_winning_user',
            null=True, blank=True)
    q3_winning_user = models.ForeignKey(User, related_name='q3_winning_user',
            null=True, blank=True)
    q4_winning_user = models.ForeignKey(User, related_name='q4_winning_user',
            null=True, blank=True)

    q1_winning_square = models.IntegerField(null=True, blank=True)
    q2_winning_square = models.IntegerField(null=True, blank=True)
    q3_winning_square = models.IntegerField(null=True, blank=True)
    q4_winning_square = models.IntegerField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
         verbose_name = 'Squares Proposed'
         verbose_name_plural = 'Squares Proposed'

    def __unicode__(self):
        return "{id: '%d', user: '%s', team_a: '%s', team_b: '%s', pps: '%d'}" % (
                self.id, self.user.get_full_name(), self.team_a, self.team_b, self.price_per_square)

class SquaresAccepted(models.Model):
    squares_game = models.ForeignKey(SquaresProposed)
    accepted_user = models.ForeignKey(User)
    num_squares = models.IntegerField()
    assigned_squares = ListCharField(
            base_field=models.CharField(max_length=2),
            size=100,
            max_length=(100*3) # 100 2-digit numbers+comma max
            )

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
         verbose_name = 'Squares Accepted'
         verbose_name_plural = 'Squares Accepted'

    def __unicode__(self):
        return "{id: '%d', user: '%s', game: '%s', num_squares: '%d'}" % (
                self.id, self.user.get_full_name(), self.squares_game, self.num_squares)
