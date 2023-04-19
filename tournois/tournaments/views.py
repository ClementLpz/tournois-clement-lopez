from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.http import HttpResponse

from .models import Tournament, Pool, Match, Comment
from .forms import CommentForm

def user_authentication(request, context):
    if request.user.is_authenticated:
        username = request.user
    else :
        username = None
    
    context['username'] = username
    return context

def tournaments_list(request):
    tournaments_list = get_list_or_404(Tournament)
    context = {'tournaments_list' : tournaments_list}
    return render(request,'tournaments/tournaments_list.html', user_authentication(request, context))

def tournament_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    context = {'tournament' : tournament}
    return render(request,'tournaments/tournament_details.html', user_authentication(request, context))

def pool_details(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    teams_ranked = Pool.compute_ranking(pool)
    context = {'pool' : pool, 'teams_ranked' : teams_ranked}
    return render(request,'tournaments/pool_details.html', user_authentication(request, context))

def match_details(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    context = {'match' : match}

    if request.method == 'GET':
        form = CommentForm()
    elif request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(message = form.cleaned_data['message'], 
                              match = match, 
                              date = "01/01/2001", 
                              hour = "00h00", 
                              author = request.user)
            comment.save()                  
            context['form'] = form
            return render(request,'tournaments/match_details.html', user_authentication(request, context))
    
    return render(request,'tournaments/match_details.html', user_authentication(request, context))
