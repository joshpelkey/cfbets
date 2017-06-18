####################################
# utility helpers for cfbets to use
####################################

from itertools import combinations
from bets.models import ProposedBet, AcceptedBet, UserProfile, User
from django.db.models import Sum

def get_total_wins(current_user):
	all_won_prop_bets = ProposedBet.objects.filter(user=current_user, won_bet__exact=1).count()
	all_won_accepted_bets = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__exact=-1).count()

	total_won_bets = all_won_prop_bets + all_won_accepted_bets
	return total_won_bets


def get_total_losses(current_user):
	all_loss_prop_bets = ProposedBet.objects.filter(user=current_user, won_bet__exact=-1).count()
	all_loss_accepted_bets = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__exact=1).count()

	total_loss_bets = all_loss_prop_bets + all_loss_accepted_bets
	return total_loss_bets

def get_total_ties(current_user):
	all_tie_prop_bets = ProposedBet.objects.filter(user=current_user, won_bet__exact=0).count()
	all_tie_accepted_bets = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__exact=0).count()

	total_tie_bets = all_tie_prop_bets + all_tie_accepted_bets
	return total_tie_bets

def get_win_percentage(current_user):
	total_wins = get_total_wins(current_user)
	total_losses = get_total_losses(current_user)
	total_plays = total_wins + total_losses
	if (total_plays):
		win_percentage = int(round((total_wins / float(total_plays)) * 100))
	else:
		win_percentage = 0

	return win_percentage
	

def get_total_proposed(current_user):
	total_proposed = ProposedBet.objects.filter(user=current_user, won_bet__isnull=False).count()
	total_won = ProposedBet.objects.filter(user=current_user, won_bet__exact=1).count()
	# get win percentage
	if(total_proposed):
		win_percentage = int(round(total_won / float(total_proposed) * 100))
	else:
		win_percentage = 0

	total_proposed_won = {'total_proposed': total_proposed, 'total_won': total_won, 'win_percentage': win_percentage}
	return total_proposed_won

def get_total_accepted(current_user):
	total_accepted = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__isnull=False).count()
	total_won = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__won_bet__exact=-1).count()
	# get win percentage
	if(total_accepted):
		win_percentage = int(round(total_won / float(total_accepted) * 100))
	else:
		win_percentage = 0

	total_accepted_won = {'total_accepted': total_accepted, 'total_won': total_won, 'win_percentage': win_percentage}
	return total_accepted_won

def get_bet_against_report(current_user):
	bet_against_report = []

	users = User.objects.exclude(id=current_user.id)
	for u in users:
		name = u.first_name + ' ' + u.last_name

		# get bets where you accepted and the other user proposed
		bets_you_accepted = AcceptedBet.objects.filter(accepted_user=current_user, accepted_prop__user=u, accepted_prop__won_bet__isnull=False)

		# get bets where you proposed and they accepted
		bets_they_accepted = AcceptedBet.objects.filter(accepted_user=u, accepted_prop__user=current_user, accepted_prop__won_bet__isnull=False)

		# count up total bets
		total_bets = bets_you_accepted.count() + bets_they_accepted.count()

		# how many you won
		total_proposed_won = bets_they_accepted.filter(accepted_prop__won_bet__exact=1)
		total_accepted_won = bets_you_accepted.filter(accepted_prop__won_bet__exact=-1)
		all_wins = total_proposed_won | total_accepted_won
		total_won = all_wins.count()
		if (total_won):
			amount_won = all_wins.aggregate(Sum('accepted_prop__prop_wager'))
			amount_won = amount_won.values()[0]
		else:
			amount_won = 0

		# how many you lost
		total_proposed_lost = bets_they_accepted.filter(accepted_prop__won_bet__exact=-1)
		total_accepted_lost = bets_you_accepted.filter(accepted_prop__won_bet__exact=1)
		all_losses = total_proposed_lost | total_accepted_lost
		total_lost = all_losses.count()
		if (total_lost):
			amount_lost = all_losses.aggregate(Sum('accepted_prop__prop_wager'))
			amount_lost = amount_lost.values()[0]
		else:
			amount_lost = 0

		# how many you tied 
		total_proposed_tie = bets_they_accepted.filter(accepted_prop__won_bet__exact=0)
		total_accepted_tie = bets_you_accepted.filter(accepted_prop__won_bet__exact=0)
		all_ties = total_proposed_tie | total_accepted_tie
		total_tie = all_ties.count()

		# get balance
		balance = amount_won - amount_lost
	
		bet_against_report.append({'name': name, 'total_bets': total_bets, 'total_won': total_won, 'total_lost': total_lost, 'total_tie': total_tie, 'balance': balance})

	return bet_against_report

	

def get_global_stats():
	global_total_proposed = ProposedBet.objects.count()
	global_total_accepted = AcceptedBet.objects.values('accepted_prop').distinct().count()

	# get total monies bet
	global_total_money = AcceptedBet.objects.aggregate(Sum('accepted_prop__prop_wager'))

	# get total monies won
	global_total_money_won = UserProfile.objects.filter(overall_winnings__gt=0).aggregate(Sum('overall_winnings'))

	# put in dictionary
	global_stats = {'total_proposed': global_total_proposed, 'total_accepted': global_total_accepted, 'total_money': global_total_money.values()[0], 'total_money_won': global_total_money_won.values()[0]}
	return global_stats

def get_global_betting_report():
	global_betting_report =[] 

	users = User.objects.all()
	for user in users:
		name = user.first_name + ' ' + user.last_name
		total_won = get_total_wins(user)
		total_lost = get_total_losses(user)
		total_tie = get_total_ties(user)
		total_bets = total_won + total_lost + total_tie
		win_percentage = get_win_percentage(user)

		global_betting_report.append({'name': name, 'total_bets': total_bets, 'total_won': total_won, 'total_lost': total_lost, 'total_tie': total_tie, 'win_percentage': win_percentage})

	return global_betting_report

def get_bettingest_couples():
	# get list of users
	users = User.objects.values('id', 'first_name', 'last_name')

	# use itertools to get all combinations
	global_bettingest_couples = []
	for combo in combinations(users, 2):
		# for each combo, check how many bets they have with eachother 
		num_bets = get_couple_bet_number(combo[0]['id'], combo[1]['id'])

		# append to list of dictionaries
		# e.g. L = [{num_bets: 5, users: ['John Doe', 'Jane Doe']}]
		user1_name = combo[0]['first_name'] + ' ' + combo[0]['last_name']
		user2_name = combo[1]['first_name'] + ' ' + combo[1]['last_name']
		users_names = [user1_name, user2_name]
		entry = {'num_bets': num_bets, 'users': users_names}
		global_bettingest_couples.append(entry)

	# pare down to top 5
	pared_global_bettingest_couples = sorted(global_bettingest_couples, key=lambda k: k['num_bets'], reverse=True)[:10]

	return pared_global_bettingest_couples

def get_couple_bet_number(user1_id, user2_id):
	# get user objects
	user1 = User.objects.get(id__exact=user1_id)
	user2 = User.objects.get(id__exact=user2_id)

	# find all bets where user1 and user2 bet eachother
	num_bets_user1_accepted = AcceptedBet.objects.filter(accepted_user=user1, accepted_prop__user=user2).count()
	num_bets_user2_accepted = AcceptedBet.objects.filter(accepted_user=user2, accepted_prop__user=user1).count()

	return num_bets_user1_accepted + num_bets_user2_accepted
