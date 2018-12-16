from __future__ import unicode_literals

from django.db import models
from django_mysql.models import ListCharField
from django.contrib.auth.models import User

# SquaresProposed holds all squares games...that have been proposed. amirite

class SquaresProposed(models.Model):
    user = models.ForeignKey(User)
    team_a = models.CharField(max_length=256)
    team_b = models.CharField(max_length=256)
    per_square_cost = models.IntegerField()
    remaining_squares = models.IntegerField(default=100)
    end_date = models.DateTimeField()
    closed = models.BooleanField(default=False)
    assigned_squares = models.TextField()
    use_shit_payout = models.BooleanField()
    shit_22_user = models.ForeignKey(User, related_name='shit_22_user')
    shit_55_user = models.ForeignKey(User, related_name='shit_55_user')
    shit_99_user = models.ForeignKey(User, related_name='shit_99_user')
    q1_winning_user = models.ForeignKey(User, related_name='q1_winning_user')
    q2_winning_user = models.ForeignKey(User, related_name='q2_winning_user')
    q3_winning_user = models.ForeignKey(User, related_name='q3_winning_user')
    q4_winning_user = models.ForeignKey(User, related_name='q4_winning_user')
    q1_winning_square = models.IntegerField()
    q2_winning_square = models.IntegerField()
    q3_winning_square = models.IntegerField()
    q4_winning_square = models.IntegerField()

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
         verbose_name = 'Squares Proposed'
         verbose_name_plural = 'Squares Proposed'

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
