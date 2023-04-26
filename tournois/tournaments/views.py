from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from math import log2
from django.contrib import messages
from .models import Tournament, Pool, Match, Comment, FinalRound
from .forms import CommentForm

def user_authentication(request, context):

    """
    Add the username to the context if the user is authenticated
    :param request: The incoming request
    :param context: The context to add the username
    """

    if request.user.is_authenticated:
        username = request.user
    else :
        username = None
    
    context['username'] = username
    return context
def tournaments_list(request):

    """
    Get all tournaments from database
    :param request: The incoming request
    """

    tournaments_list = get_list_or_404(Tournament)
    context = {'tournaments_list' : tournaments_list}
    return render(request,'tournaments/tournaments_list.html', user_authentication(request, context))

def tournament_details(request, tournament_id):

    """
    Get pools of the selected tournament from database
    :param request: The incoming request
    :param tournament_id: The id of the selected tournament
    """

    tournament = get_object_or_404(Tournament, pk=tournament_id)
    context = {'tournament' : tournament}
    return render(request,'tournaments/tournament_details.html', user_authentication(request, context))

def compute_matches(request, pool_id, compute_matches):

    """
    Get matchs of the selected pool from database. 
    Also computes the ranking of teams in the pool.
    :param request: The incoming request
    :param pool_id: The id of the selected pool
    """

    pool = get_object_or_404(Pool, pk=pool_id)
    if (compute_matches == 1):
        Pool.all_matches(pool)
    teams_ranked = Pool.compute_ranking(pool)
    context = {'pool' : pool, 'teams_ranked' : teams_ranked}
    return render(request,'tournaments/pool_details.html', user_authentication(request, context))


def pool_details(request, pool_id):

    """
    Get matchs of the selected pool from database. 
    Also computes the ranking of teams in the pool.
    :param request: The incoming request
    :param pool_id: The id of the selected pool
    """

    pool = get_object_or_404(Pool, pk=pool_id)
    teams_ranked = Pool.compute_ranking(pool)
    context = {'pool' : pool, 'teams_ranked' : teams_ranked}
    return render(request,'tournaments/pool_details.html', user_authentication(request, context))

def match_details(request, match_id):

    """
    Get comments of the selected match from database.
    Allow an authenticated user to POST a new comment on the match.
    :param request: The incoming request
    :param match_id: The id of the selected match
    """

    match = get_object_or_404(Match, pk=match_id)
    context = {'match' : match}

    if request.method == 'GET':
        form = CommentForm()
    elif request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(message = form.cleaned_data['message'], 
                              match = match, 
                              pub_date = timezone.now(), 
                              author = request.user)
            comment.save()                  
            context['form'] = form
    
    return render(request,'tournaments/match_details.html', user_authentication(request, context))

def update_comment(request, match_id, comment_id):

    """
    Allow an authenticated user to MODIFY a comment he posted.
    :param request: The incoming request
    :param match_id: The id of the selected match
    :param comment_id: The id of the comment to modify
    """

    match = get_object_or_404(Match, pk=match_id)
    context = {'match' : match}

    comment = get_object_or_404(Comment, pk=comment_id)
    comment.pub_date = timezone.now()
    if request.method == 'GET':
        form = CommentForm(instance=comment)
    elif request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('tournaments:match_details', match_id)
    
    context['form'] = form
    return render(request, 'tournaments/match_details.html', user_authentication(request, context))

def final_round(request, tournament_id, force=False, erase=False):
    print("début")
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    final_round, created = FinalRound.objects.get_or_create(tournament=tournament)
    if erase:
        print("erase")
        FinalRound.objects.filter(tournament=tournament).delete()
    if created or force:
        print("créé")
        final_round.create_pairings()
        final_round.refresh_from_db()  # Récupérer les données mises à jour depuis la base de données

    if request.method == 'POST' and request.user.is_authenticated and request.user.is_superuser:
        for match in final_round.matches.all():
            match_id = str(match.id)
            score1 = request.POST.get(f'team1_score-{match_id}')
            score2 = request.POST.get(f'team2_score-{match_id}')
            if score1 is not None and score2 is not None:
                match.score1 = int(score1)
                match.score2 = int(score2)
                match.save()
                # Nouveau code pour vérifier si tous les matchs du tour précédent sont terminés
                completed_matches = [m for m in final_round.matches.all() if m.winner() is not None]
                if len(completed_matches) == final_round.matches.count():
                    final_round.generate_next_round()
                    final_round.refresh_from_db()

    print(list(final_round.matches.all()))
    next_round_matches = final_round.get_next_round_matches()
    context = {
        'final_round': final_round,
        'final_round_matches': final_round.matches.all(),
        'next_round_matches': next_round_matches,
        'log2': log2,
        'range': range
    }
    return render(request, 'tournaments/final_round.html', user_authentication(request, context))
