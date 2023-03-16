import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


def random_char(lim=5):
	return f'{os.urandom(lim).hex()}'


class AccountManager(BaseUserManager):
	def create_staff_user(self, email, password, **kwargs):
		user = self.create_user(
			email=email,
			password=password,
			is_staff=True,
			**kwargs
		)
		return user

	def create_superuser(self, email, password, **kwargs):
		user = self.create_user(
			email=email,
			password=password,
			is_staff=True,
			is_superuser=True,
			**kwargs
		)
		return user

	def create_user(self, email, password=None, **kwargs):
		user = self.model(
			email=email,
			**kwargs
		)

		if password:
			user.set_password(password)
		else:
			user.set_unusable_password()

		user.save()
		return user



class Account(AbstractBaseUser):
    full_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = AccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
    	return self.full_name

    def get_full_name(self):
    	return self.full_name

    def get_all_permissions(self):
    	return []


    def has_module_perms(self, perms):
    	if self.is_staff:
    		return True
    	return False


    def has_perms(self, perms):
    	if self.is_staff:
    		return True
    	return False

    def has_perm(self, perm):
    	if self.is_staff:
    		return True
    	return False


class Notification(models.Model):
	to = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now=True)
	title = models.CharField(max_length=200, blank=True, null=True)
	message = models.TextField(blank=True, null=True)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return self.title




class UserProfile(models.Model):
	user = models.OneToOneField("Account", on_delete=models.CASCADE)
	fiat_balance = models.DecimalField(decimal_places=2, max_digits=1000, default=0)
	referrals = models.ManyToManyField("self", blank=True)
	referral_code = models.CharField(max_length=100, blank=True, null=True)
	bitcoin_address = models.CharField(max_length=100, blank=True, null=True)
	wallet_provider = models.CharField(max_length=100, blank=True, null=True)

	class Meta:
		ordering = ('-id',)
		verbose_name = 'Client'

	@property
	def notifications(self):
		return Notification.objects.filter(to=self)

	def __str__(self):
		return self.user.get_full_name()


	def referral_count(self):
		return self.referrals.count()



class Deposit(models.Model):
	user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
	amount = models.DecimalField(decimal_places=2, max_digits=1000)
	crypto_ticker = models.CharField(max_length=10, blank=True) # BTC, MATIC
	date = models.DateTimeField(auto_now=True)
	confirmed = models.BooleanField(default=False)
	transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, blank=True, null=True)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return "%s deposit $%d" % (self.user, self.amount)


class Transaction(models.Model):
	TRANSACTIONS = (
		('deposit', 'Deposit'),
		('withdrawal', 'Withdrawal'),
		('investment', 'Investment'),
	)

	TRANSACTION_STATUS = (
		('confirmed', 'Confirmed'),
		('pending', 'Pending'),
	)


	transaction_type = models.CharField(max_length=50, choices=TRANSACTIONS, default='deposit')
	date = models.DateTimeField(auto_now=True)
	amount = models.DecimalField(decimal_places=2, max_digits=1000)
	status = models.CharField(max_length=100, blank=True, null=True, default='pending', choices=TRANSACTION_STATUS)
	client = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
	transaction_id = models.CharField(max_length=20, blank=True, null=True, default=random_char)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return '%s - %s - %s' % (self.get_transaction_type_display(), self.client, self.amount)


class Withdrawal(models.Model):
	date = models.DateTimeField(auto_now=True)
	amount = models.DecimalField(decimal_places=2, max_digits=1000)
	status = models.CharField(max_length=100, blank=True, null=True, default='Confirmed')
	user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
	approved = models.BooleanField(default=False)
	transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, blank=True, null=True)

	class Meta:
		ordering = ('-id',)


class Investment(models.Model):
	package_id = models.ForeignKey("InvestmentPackage", on_delete=models.CASCADE)
	user = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
	date_created = models.DateField(auto_now=True)
	transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, blank=True, null=True)

	class Meta:
		ordering = ('-id',)


	def __str__(self):
		return self.package.name


class InvestmentPackage(models.Model):
	name = models.CharField(max_length=200, help_text="Package name. eg Bronze Starter")
	capital = models.IntegerField(help_text="Investment amount required")
	roi = models.DecimalField(max_digits=20000, decimal_places=2, help_text='Return on Investment in Percentage')
	duration = models.IntegerField(help_text="Duration of payout in days")

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return self.name

	def sample(self):
		return self.capital * (self.roi / 100)
