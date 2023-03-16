from .views import (
	login_user_view,
	register_user_view,
	dashboard_home_view,
	logout_view,
	dashboard_profile_view,
	dashboard_earnings_view,
	deposit_and_withdraw_view,
	dashboard_history_view,
	dashboard_packages_view,
	setup_wallet,
	password_reset_view,
)
from django.urls import path, include
import core.htmx_views as htmx

app_name = 'dashboard'

urlpatterns = [
	path('logout/', logout_view, name="logout"),
	path('login/', login_user_view, name="login"),
	path('register/', register_user_view, name="register"),
	path('password/reset/', password_reset_view, name='password-reset'),

	path('setup/', setup_wallet, name="setup-wallet"),
	path('wallet/', deposit_and_withdraw_view, name="wallet"),
	path('earnings/packages/', dashboard_packages_view, name="packages"),
	path('earnings/', dashboard_earnings_view, name="earnings"),
	path('history/', dashboard_history_view, name="history"),
	path('me/', dashboard_profile_view, name="profile"),
	path('', dashboard_home_view, name="home"),

	# htmx views

	path('htmx/before-deposit/', htmx.pre_deposit_flow, name='htmx-deposit-before'),
	path('htmx/after-deposit/', htmx.post_deposit_flow, name='htmx-deposit-after'),
]