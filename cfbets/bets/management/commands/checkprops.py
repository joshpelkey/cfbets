from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from bets.models import ProposedBet, AcceptedBet, UserProfile, UserProfileAudit

class Command(BaseCommand):
    help = 'Checks for new prop bets and emails users'

    def handle(self, *args, **options):

        # get site domain
        current_site = get_current_site(request)
        domain = current_site.domain

        # check for new, open prop bets (last 24 hrs)
        yesterday = datetime.now() + timedelta(days=-1)
        new_prop_bets = ProposedBet.objects.filter(
            remaining_wagers__gt=0,
            end_date__gt=timezone.now(),
            won_bet__isnull=True,
            created_on__gt=yesterday)

        # if there are new props, send to those users that want to see them
        if new_prop_bets:
            users = UserProfile.objects.filter(get_prop_bet_emails=True)
            for loop_user in users:
                # only show props from others
                other_props = new_prop_bets.exclude(user=loop_user.user)
                if other_props:
                    email_message = ''
                    for prop_bet in other_props:
                        email_message += '' + prop_bet.user.get_full_name() + \
                            ' ($' + str(prop_bet.prop_wager) + \
                            '): ' + prop_bet.prop_text + '\n'

                    # put the site url in there
                    email_message += '\nhttps://' + domain + '/bets/open_bets/'

                    # send out the email
                    send_list = []
                    send_list.append(loop_user.user.email)
                    send_mail(
                        'cfbets: New prop bets!',
                        email_message,
                        'yojdork@gmail.com',
                        send_list,
                        fail_silently=True,
                    )

            self.stdout.write(self.style.SUCCESS('Sent prop emails.'))

        else:
            self.stdout.write(self.style.SUCCESS('No new prop bets.'))
