from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
	authenticate,
	login,
	logout
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from pathlib import Path
from .models import (
	Account as User,
	UserProfile,
	Transaction,
	Deposit,
	Withdrawal,
	Notification,
	Investment,
	InvestmentPackage
)
from .utils import (
	post_signup_signal,
	send_signup_email,
	paginate_objects
)
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.conf import settings



BITCOIN_RECV_ADDRESS = settings.BITCOIN_RECV_ADDRESS

TEMPLATES_DIR = settings.BASE_DIR / 'templates/site/pages/'

def get_template(temp):
	template = TEMPLATES_DIR / temp
	return '%s.html' % template


def normalizeSlug(slug: str) -> str:
	slug = slug.replace('_', ' ').title()
	return slug


# Views

def site_index_view(request):
	ctx = {
		'page_name': 'Crypto Investing Simplified'
	}
	return render(request, 'site/home.html', ctx)


def site_page_view(request, page_name):
	template = get_template(page_name)
	ctx = {
		'page_name': normalizeSlug(page_name),
	}
	return render(request, template, ctx)


def login_user_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard:home')

	error = None
	User = get_user_model()
	_next = request.GET.get('next', None)

	if request.method == 'POST':
		data = request.POST
		email = data.get('email', None)
		pswd = data.get('password', None)

		# attempt login
		user = authenticate(username=email, password=pswd)

		if user is not None:
			if hasattr(user, 'userprofile'):
				login(request, user)
				if _next:
					return redirect(_next)
				return redirect('dashboard:home')
			else:
				return redirect('admin:index')

		else:
			error = 'invalid email or password'

	ctx = {
		'page_name': 'Login',
		'error': error
	}
	return render(request, 'auth/login.html', ctx)


def password_reset_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard:home')

	error = None
	User = get_user_model()
	_next = request.GET.get('next', None)

	if request.method == 'POST':
		data = request.POST
		email = data.get('email', None)
		pswd = data.get('password', None)

		# if user is not None:
		# 	if hasattr(user, 'userprofile'):
		# 		login(request, user)
		# 		if _next:
		# 			return redirect(_next)
		# 		return redirect('dashboard:home')
		# 	else:
		# 		return redirect('admin:index')

		# else:
		# 	error = 'invalid email or password'

	ctx = {
		'page_name': 'Password Reset',
		'error': error
	}
	return render(request, 'auth/password-reset.html', ctx)


def logout_view(request):
	logout(request)
	return redirect('dashboard:login')


def register_user_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard:home')

	error = None
	if request.method == 'POST':
		data = request.POST
		# attempt signup
		user = User(
			full_name = data.get('full_name'),
			email = data.get('email'),
			last_login=datetime.now(),
		)
		user.set_password(data.get('password'))
		user.save()

		profile = UserProfile(
			user = user,
			bitcoin_address = data.get('bitcoin-addr', None),
		)
		profile.save()

		post_signup_signal.connect(send_signup_email)
		post_signup_signal.send(sender=profile)

		messages.success(request, "Welcome %s" % data.get('full_name'))
		login(request, user)
		return redirect('dashboard:home')

	ctx = {
		'page_name': 'Register',
		'error': error
	}
	return render(request, 'auth/register.html', ctx)


@login_required(login_url='dashboard:login')
def dashboard_home_view(request):
	ctx = {
		'page_name': 'Dashboard',
		'active_nav': 'dashboard',
		'recent_transactions': Transaction.objects.filter(client=request.client)[:7],
		'recent_earnings': Investment.objects.filter(user=request.client)[:7],
		'bitcoin_recv_address': BITCOIN_RECV_ADDRESS,
	}
	return render(request, 'mines/home.html', ctx)



@login_required(login_url='dashboard:login')
@csrf_exempt
def deposit_and_withdraw_view(request):
	params = request.GET

	if request.method == "POST":
		data = request.POST

		if params.get('transaction') == 'deposit':
			deposit = Deposit(
				user = request.client,
				amount = data['amount'],
				crypto_ticker = 'BTC',
			)
			deposit.save()
			messages.success(request, "Deposit Transaction Pending")

		elif params.get('transaction') == 'withdrawal':
			if data['amount'] >= int(request.client.fiat_balance):
				messages.error(request, "You have insufficient balance for this withdrawal")
				return redirect(request.META['HTTP_REFERER'])
			
			messages.success(request, "Withdrawal Transaction Pending")
			withdrawal = Withdrawal(
				user=request.client,
				amount=data['amount'],
			)
			withdrawal.save()

		transaction = Transaction(
			amount=data['amount'],
			client=request.client,
			transaction_type=params['transaction']
		)
		transaction.save()

		return redirect(request.META['HTTP_REFERER'])
	return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='dashboard:login')
def dashboard_earnings_view(request):
	queryset = Investment.objects.filter()
	paginator = paginate_objects(queryset)
	page_num = request.GET.get('page', 1)
	page = paginator.page(page_num)
	earnings = page.object_list
	packages = InvestmentPackage.objects.all()

	if request.method == "POST":
		data = request.POST
		package = packages.get(id=data['package'])

		if package.capital > request.client.fiat_balance:
			messages.error(request, 'Insufficient funds for selected package')
		else:
			request.client.fiat_balance -= package.capital
			request.client.save()


			# create transaction
			transaction = Transaction(
				transaction_type='investment',
				amount=package.capital,
				status='confirmed',
				client=request.client
			)
			transaction.save()

			investment = Investment(
				package_id=package,
				user=request.client,
				transaction=transaction
			)
			investment.save()
			messages.success(request, 'Investment Successful!')

			# create Notification
			Notification.objects.create(
				to=request.client,
				title="Investment Success",
				message="Your investment of %s was successful" % package.capital
			)

		return redirect(request.META['HTTP_REFERER'])

	ctx = {
		'page_name': 'Dashboard',
		'active_nav': 'earnings',
		'earnings': earnings,
		'page': page,
		'packages': packages
	}
	return render(request, 'mines/earnings.html', ctx)



@login_required(login_url='dashboard:login')
def dashboard_history_view(request):
	queryset = Transaction.objects.filter(client=request.client)
	paginator = paginate_objects(queryset)
	page_num = request.GET.get('page', 1)
	page = paginator.page(page_num)
	transactions = page.object_list
	ctx = {
		'page_name': 'Dashboard',
		'active_nav': 'history',
		'transactions': transactions,
		'page': page,

	}
	return render(request, 'mines/history.html', ctx)



@login_required(login_url='dashboard:login')
def dashboard_packages_view(request):
	packages = InvestmentPackage.objects.all()
	ctx = {
		'page_name': 'Investment Packages',
		'active_nav': 'earnings',
		'packages': packages,

	}
	return render(request, 'mines/packages.html', ctx)



@login_required(login_url='dashboard:login')
def dashboard_profile_view(request):
	if request.method == "POST":
		data = request.POST
	ctx = {
		'page_name': 'My Profile',
		'active_nav': None
	}
	return render(request, 'mines/profile.html', ctx)


@csrf_exempt
def setup_wallet(request):
	if request.method == 'POST':
		data = request.POST
		profile = UserProfile.objects.get(user=request.user)

		profile.bitcoin_address = data['address']
		profile.wallet_provider = data['provider']
		profile.save()

		messages.success(request, "Your wallet has been updated")
		return redirect(request.META['HTTP_REFERER'])
	return redirect(request.META['HTTP_REFERER'])