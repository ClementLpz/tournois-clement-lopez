from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.http import HttpResponse

from .models import Tournament, Pool

def tournaments_list(request):
    tournaments_list = get_list_or_404(Tournament)
    context = {'tournaments_list' : tournaments_list}
    return render(request,'tournaments/tournaments_list.html', context)

def tournament_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    context = {'tournament' : tournament}
    return render(request,'tournaments/tournament_details.html', context)

def pool_details(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    teams_ranked = Pool.compute_ranking(pool)
    context = {'pool' : pool, 'teams_ranked' : teams_ranked}
    return render(request,'tournaments/pool_details.html', context)
