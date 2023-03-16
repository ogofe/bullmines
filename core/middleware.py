from .models import UserProfile
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class ClientMiddleware(MiddlewareMixin):
	def process_request(self, request):
		if request.user.is_authenticated:
			try:
				request.client = UserProfile.objects.get(user=request.user)
			except Exception as e:
				request.client = None


class ReferralMiddleware(MiddlewareMixin):
	def process_request(self, request):
		referral = request.GET.get('ref_code')
		if referral:
			referree = UserProfile.objects.get(referral_code=referral)
			if request.user:
				referree.referrals.add(request.user)
				referree.save()
			else:
				request.referree = referree


class LoggerMiddleware:

	def __init__(self, get_response):
	    self.get_response = get_response

	def __call__(self, request):
		try:
			response = self.get_response(request)
			return response
		except Exception as e:
			logger.error("Unhandled Error:", e)
