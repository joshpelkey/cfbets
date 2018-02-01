from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.sites.shortcuts import get_current_site
from google.appengine.api import mail
from bets.models import ProposedBet, AcceptedBet, UserProfile, UserProfileAudit
import webapp2 as webapp

class DailyEmail(webapp.RequestHandler):
    def get(self):

        # check for new, open prop bets (last 24 hrs)
        yesterday = datetime.now() + timedelta(days=-1)
	new_prop_bets = ProposedBet.objects.filter(remaining_wagers__gt=0, end_date__gt=timezone.now(), won_bet__isnull=True, created_on__gt=yesterday)

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
				email_message += '\nhttps://cfbets.us/bets/open_bets/'

				# send out the email
                                message = mail.EmailMessage(
                                        sender='cfbets <joshpelkey@gmail.com>',
                                        subject="cfbets: New prop bets!")

                                message.to = loop_user.user.email
                                message.body = email_message

                                message.send()

        html = 'Daily email sent'
        self.response.out.write(html)

app = webapp.WSGIApplication([('/tasks/daily_email', DailyEmail)], debug=True)
