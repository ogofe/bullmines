from .views import (
	site_index_view,
	site_page_view,
)

from django.urls import path

app_name = 'core'

urlpatterns = [
	path('', site_index_view, name="site-index"),
	path('pg/<slug:page_name>/', site_page_view, name="site-page"),
]