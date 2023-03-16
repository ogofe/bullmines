from django.contrib import admin
from .models import (
	UserProfile, Deposit, Account,
	Withdrawal, Transaction, Notification,
	Investment, InvestmentPackage,
)
from .utils import send_signup_email as send_email
from django.contrib import messages



class ProfileAdmin(admin.ModelAdmin):
	list_display = [
		'__str__',
		'fiat_balance',
		'referral_count',
		'bitcoin_address'
	]

	actions = [
		'send_signup_email',
	]

	def send_signup_email(self, request, profiles):
		profiles = list(profiles)
		if len(profiles) > 1:
			return messages.error(request, "You can send a welcome message to one user at a time.")

		try:
			profile = profiles[0]
			send_email(profile)
			messages.success(request, "Email sent to %s" % profile.user.email)
		except Exception as e:
			messages.error(request, e)


class TransactionAdmin(admin.ModelAdmin):
	list_display = [
		'transaction_type',
		'client',
		'amount',
		'date',
		'status',
	]


class DepositAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'amount',
	]

	actions = [
		'confirm_selected_deposit',
	]


	def confirm_selected_deposit(self, request, deposits, **kwargs):
		deposits.update(confirmed=True)
		for deposit in deposits:
			if not deposit.confirmed == True:
				deposit.user.fiat_balance += deposit.amount
				deposit.user.save()

			if deposit.transaction:
				deposit.transaction.status = 'confirmed'
				deposit.transaction.save()

			Notification.objects.create(
				to=deposit.user,
				title="Deposit confirmed!",
				message="Your deposit of %d has been confirmed!" % deposit.amount
			)

		messages.success(request, 'Deposits Confirmed!')


# class ProfileAdmin(admin.ModelAdmin):
# 	list_display = [
# 		'__str__',
# 		'fiat_balance',
# 		'referral_count',
# 		'bitcoin_address'
# 	]


admin.site.register(Deposit, DepositAdmin)
admin.site.register(Account)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(Investment)
admin.site.register(InvestmentPackage)
admin.site.register(Withdrawal)
admin.site.register(Transaction, TransactionAdmin)


# admin.site.site_index_header = "Bull Mines | Admin"