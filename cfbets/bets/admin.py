from django.contrib import admin
from bets.models import ProposedBet, AcceptedBet, UserProfile, UserProfileBetsAudit, UserProfileSquaresAudit

# Register your models here.

admin.site.register(ProposedBet)
admin.site.register(AcceptedBet)
admin.site.register(UserProfile)
admin.site.register(UserProfileBetsAudit)
admin.site.register(UserProfileSquaresAudit)
