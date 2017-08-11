from django.contrib import admin
from bets.models import ProposedBet, AcceptedBet, UserProfile, UserProfileAudit

# Register your models here.

admin.site.register(ProposedBet)
admin.site.register(AcceptedBet)
admin.site.register(UserProfile)
admin.site.register(UserProfileAudit)
