from django.shortcuts import render, get_list_or_404
from django.http import HttpResponse

from .models import Tournoi

def tournaments_list(request):
    tournaments_list = get_list_or_404(Tournoi)
    context = {'tournaments_list' : tournaments_list}
    return render(request,'tournaments/tournaments_list.html', context)