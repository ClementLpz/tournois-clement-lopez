from django.shortcuts import render
from django.http import HttpResponse

def tournaments_list(request):
    return HttpResponse("List of tournaments coming soon.")