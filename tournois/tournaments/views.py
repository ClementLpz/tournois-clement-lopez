from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.http import HttpResponse

from .models import Tournoi

def tournaments_list(request):
    tournaments_list = get_list_or_404(Tournoi)
    context = {'tournaments_list' : tournaments_list}
    return render(request,'tournaments/tournaments_list.html', context)

def tournament_details(request, tournament_id):
    tournament = get_object_or_404(Tournoi, pk=tournament_id)
    context = {'tournament' : tournament}
    return render(request,'tournaments/tournament_details.html', context)