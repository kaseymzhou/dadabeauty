from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def test(request):
    return HttpResponse('test is ok')