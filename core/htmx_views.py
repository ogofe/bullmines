from django.shortcuts import redirect, render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def post_deposit_flow(request):
	response =  """
					<div></div>
				"""
	print("GET: ", request.GET)
	if request.method == "POST":
		print("POST: ", request.POST)
	return HttpResponse(content=response, content_type='text/html')


@csrf_exempt
def pre_deposit_flow(request):
	response =  """
				
				"""
	print("GET: ", request.GET)
	if request.method == "POST":
		print("POST: ", request.POST)
	return HttpResponse(content=response, content_type='text/html')


@csrf_exempt
def pre_withdrawal_flow(request):
	response =  """
					<div></div>
				"""
	return HttpResponse(content=response)


@csrf_exempt
def post_withdrawal_flow(request):
	response =  """
					<div></div>
				"""
	return HttpResponse(content=response)





