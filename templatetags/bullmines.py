from django.template import Library

register = Library()

@register.filter
def split(value, arg):
	return