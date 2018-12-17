# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-12-17 21:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('squares', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bets', '0004_auto_20170618_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfileSquaresAudit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_current_balance', models.IntegerField()),
                ('new_current_balance', models.IntegerField()),
                ('original_overall_winnings', models.IntegerField()),
                ('new_overall_winnings', models.IntegerField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('accepted_square', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='squares.SquaresProposed')),
                ('admin_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile_squares_admin', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile_squares_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile Squares Audit',
                'verbose_name_plural': 'User Profile Squares Audits',
            },
        ),
        migrations.AlterModelOptions(
            name='acceptedbet',
            options={'ordering': ['accepted_prop__end_date'], 'verbose_name': 'Accepted Bet', 'verbose_name_plural': 'Accepted Bets'},
        ),
        migrations.AlterModelOptions(
            name='proposedbet',
            options={'ordering': ['end_date'], 'verbose_name': 'Proposed Bet', 'verbose_name_plural': 'Proposed Bets'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'User Profile', 'verbose_name_plural': 'User Profiles'},
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='current_balance',
            new_name='current_bets_balance',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='overall_winnings',
            new_name='overall_bets_winnings',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_squares_balance',
            field=models.IntegerField(default=0, help_text="The user's current squares balance. Every time the users settles up,        the current squares balance is reset."),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='get_assigned_squares_emails',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='get_new_squares_emails',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='overall_squares_winnings',
            field=models.IntegerField(default=0, help_text="The user's overall squares winnings since joining."),
        ),
        migrations.RenameModel(
            old_name='UserProfileAudit',
            new_name='UserProfileBetsAudit',
        ),
    ]