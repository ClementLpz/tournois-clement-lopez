import math
from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .models import Tournament, Pool, Match, Comment, Team, FinalRound
from .forms import CommentForm, ResearchForm
import json
import re
from django.core import serializers
from math import log2
from django.contrib import messages

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

def match_date(date):

    """
    Format the date to match the date attribute of Match model
    :param date: The date to format
    """

    month = ""
    if date[1].lower() in ["janvier", "january"]:
        month = "01"
    elif date[1].lower() in ["février", "february"]:
        month = "02"
    elif date[1].lower() in ["mars", "march"]:
        month = "03"
    elif date[1].lower() in ["avril", "april"]:
        month = "04"
    elif date[1].lower() in ["mai", "may"]:
        month = "05"
    elif date[1].lower() in ["juin", "june"]:
        month = "06"
    elif date[1].lower() in ["juillet", "july"]:
        month = "07"
    elif date[1].lower() in ["août", "august"]:
        month = "08"
    elif date[1].lower() in ["septembre", "september"]:
        month = "09"
    elif date[1].lower() in ["octobre", "october"]:
        month = "10"
    elif date[1].lower() in ["novembre", "november"]:
        month = "11"
    elif date[1].lower() in ["décembre", "december"]:
        month = "12"
    else:
        month = "01" # January by default

    if (len(date[0]) == 1):
        date_str = date[2] + "-" + month + "-0" + date[0]
    else:
        date_str = date[2] + "-" + month + "-" + date[0]

    return date_str

def context_reset(context) :

    """
    Reset all (exept research) fields of context
    :param context: The incoming context
    """

    context['teams'] = []
    context['tournaments'] = []
    context['multi_search'] = []
    context['matchs_tournament'] = []
    context['matchs_team'] = [] 
    context['matchs_pool'] = []
    context['matchs_date'] = []
    context['matchs_scores'] = []
    context['matchs_goal'] = []

    return context

def context_fill(context, form, key_word, date_search, date_2_search, score_search, pool_search, goal_search, multisearch) :

    """
    Fill in the context with every research filters
    :param context: The incoming context
    :param form: The research form
    :param key_word: If multisearching, one of the keywords of the research
    :param date_search: The date pattern to match for the research content
    :param date_2_search: The second date pattern to match for the research content
    :param score_search: The score pattern to match for the research content
    :param pool_search: The pool number pattern to match for the research content
    :param goal_search: The number of goals pattern to match for the research content
    :param multisearch: Boolean to know if we use multi-searching
    """

    # To keep the previous filtered objects in memory
    if multisearch :
        pk_multi_search_list = [obj.pk for obj in context['multi_search']]

    # If the key word matches the date 1 pattern 'xx/xx/xxxx'
    if (date_search != None) : 
        date = [s for s in date_search.group().split("/")]
        date_str = date[2] + "-" + date[1] + "-" + date[0]

        if multisearch :
            context['multi_search'] = Match.objects.filter(pk__in = pk_multi_search_list).filter(date = date_str)
        else :
            context['matchs_date'] = Match.objects.filter(date = date_str)

    # If the key word matches the date 2 pattern 'x(x) word xxxx'
    elif (date_2_search != None) : 
        date = [s for s in date_2_search.group().split(" ")]
        date_str = match_date(date)

        if multisearch :
            context['multi_search'] = Match.objects.filter(pk__in = pk_multi_search_list).filter(date = date_str)
        else :
            context['matchs_date'] = Match.objects.filter(date = date_str)

    # If the key word matches the score pattern 'x-x'
    elif (score_search != None) :
        score = [int(s) for s in score_search.group().split("-")]

        if multisearch :
            context['multi_search'] = Match.objects.filter(pk__in = pk_multi_search_list).filter(Q(score1 = score[0]) & Q(score2 = score[1]))
        else :
            context['matchs_scores'] = Match.objects.filter(Q(score1 = score[0]) & Q(score2 = score[1]))

    # If the key word matches the pool pattern 'Pool xx'
    elif (pool_search != None) :
        pool_num = int(pool_search.group().split(" ")[-1])

        if multisearch :
            context['multi_search'] = Match.objects.filter(pk__in = pk_multi_search_list).filter(pool__number = pool_num)
        else :
            context['matchs_pool'] = Match.objects.filter(pool__number = pool_num)

    # If the key word matches the goal pattern 'Goal xx'
    elif (goal_search != None) :
        goal = int(goal_search.group().split(" ")[-1])

        if multisearch :
            context['multi_search'] = Match.objects.filter(pk__in = pk_multi_search_list).filter(Q(score1 = goal) | Q(score2 = goal))
        else :
            context['matchs_goal'] = Match.objects.filter(Q(score1 = goal) | Q(score2 = goal))

    # If the key word doesn't match any pattern
    else :
        if multisearch :
            context['multi_search'] = Match.objects.filter(pk__in = pk_multi_search_list).filter(Q(team1__name__contains = key_word) | Q(team2__name__contains = key_word) | Q(pool__tournament__name__contains = key_word))
        else :
            context['teams'] = Team.objects.filter(name__contains = form.cleaned_data['research']).order_by('name')
            context['tournaments'] = Tournament.objects.filter(name__contains = form.cleaned_data['research']).order_by('name')
            context['matchs_team'] = Match.objects.filter(Q(team1__name__contains = form.cleaned_data['research']) | Q(team2__name__contains = form.cleaned_data['research']))
            context['matchs_tournament'] = Match.objects.filter(pool__tournament__name__contains = form.cleaned_data['research'])

    return context

def research(request):

    """
    Analyze and filter information coming from the research bar
    :param request: The incoming request
    """

    if request.method == 'GET':
        form = ResearchForm()
        context = {'form' : form}
    elif request.method == 'POST':
        form = ResearchForm(request.POST)
        context = {'form' : form}
        if form.is_valid():

            context['research'] = re.split(' \+ |\+', form.cleaned_data['research'])

            # Define matching patterns
            date_format = re.compile(r'\d{2}/\d{2}/\d{4}')
            date_2_format =  re.compile(r'\d+ \w+ \d{4}')
            score_format = re.compile(r'\d-\d')
            pool_format = re.compile(r'Pool \d+')
            goal_format = re.compile(r'Goal \d+')
            everything_format = re.compile(r'All')

            # Pattern All
            everything_search = everything_format.search(form.cleaned_data['research'])
            if (everything_search != None) : 

                context = context_reset(context)

                context['teams'] = Team.objects.all().order_by('name')
                context['tournaments'] = Tournament.objects.all().order_by('name')
                context['multi_search'] = Match.objects.order_by('pool__tournament__name', 'pool', 'team1__name')

            # Uni-search
            elif (len(context['research']) == 1) :
                
                context = context_reset(context)

                score_search = score_format.search(form.cleaned_data['research'])
                date_search = date_format.search(form.cleaned_data['research'])
                date_2_search = date_2_format.search(form.cleaned_data['research'])
                pool_search = pool_format.search(form.cleaned_data['research'])
                goal_search = goal_format.search(form.cleaned_data['research'])

                context = context_fill(context, form, "", date_search, date_2_search, score_search, pool_search, goal_search, False)

            # Multi-search
            else :

                context = context_reset(context)
                context['multi_search'] = Match.objects.all()

                for key_word in context['research'] :

                    date_search = date_format.search(key_word)
                    date_2_search = date_2_format.search(key_word)
                    score_search = score_format.search(key_word)
                    pool_search = pool_format.search(key_word)
                    goal_search = goal_format.search(key_word)

                    context = context_fill(context, form, key_word, date_search, date_2_search, score_search, pool_search, goal_search, True)

    return render(request,'tournaments/research.html', user_authentication(request, context))

def tournament_details(request, tournament_id):

    """
    Get pools of the selected tournament from database
    :param request: The incoming request
    :param tournament_id: The id of the selected tournament
    """

    tournament = get_object_or_404(Tournament, pk=tournament_id)
    context = {'tournament' : tournament, 'tournament_id' : tournament_id}
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
    matches = Match.objects.filter(pool__id=pool_id).order_by('id')
    labels = []
    data = []

    for match in matches:
        labels.append(str(match.team1) + ' vs ' + str(match.team2))
        data.append(match.score1 + match.score2)

    chart = {
        'labels': labels,
        'data': data,
    }

    pool = get_object_or_404(Pool, pk=pool_id)
    teams_ranked = Pool.compute_ranking(pool)

    
    teams_ranked = Pool.compute_ranking(pool)
    matchs = pool.match_set.all()
    loc  = []
    for match in matchs:
        if match.localisation is not None:
            loc.append(match.localisation)

    serialized_localisation = serializers.serialize("json", loc)

    
    # If "reset_pairings" was clicked, erase all matches from the final round
    if request.method == "POST" and "reset_matchs" in request.POST:
        matches = Match.objects.all().filter(pool__number = pool.number)
        for match in matches :
            match.delete()

    context = {'pool' : pool, 'teams_ranked' : teams_ranked, 'chart_data':json.dumps(chart), 'serialized_localisation': serialized_localisation}

    return render(request,'tournaments/pool_details.html', user_authentication(request, context))

def match_details(request, match_id):

    """
    Get comments of the selected match from database.
    Allow an authenticated user to POST a new comment on the match.
    :param request: The incoming request
    :param match_id: The id of the selected match
    """


    match = get_object_or_404(Match, pk=match_id)
    
    if match.localisation is not None:
        serialized_localisation = serializers.serialize("json", {match.localisation})
    else:
        serialized_localisation=None
    context = {'match' : match, 'serialized_localisation': serialized_localisation}

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

    comment_ordered = Comment.objects.order_by('-pub_date').filter(match = match)
    context['comment_ordered'] = comment_ordered  
    return render(request,'tournaments/match_details.html', user_authentication(request, context))

#Almost like match_details but another render since it's a finalround match and that created problems with the Ariane wire
def match_details_finals(request, match_id):
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
    
    comment_ordered = Comment.objects.order_by('-pub_date').filter(match = match)
    context['comment_ordered'] = comment_ordered  
    return render(request,'tournaments/match_details_finals.html', user_authentication(request, context))
    
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
        comment_ordered = Comment.objects.order_by('-pub_date').filter(match = match)
        context['comment_ordered'] = comment_ordered  
    elif request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            comment_ordered = Comment.objects.order_by('-pub_date').filter(match = match)
            context['comment_ordered'] = comment_ordered  
            return redirect('tournaments:match_details', match_id)
    
    context['form'] = form
    return render(request, 'tournaments/match_details.html', user_authentication(request, context))

#Almost like update_comments but another render since it's a finalround match and that created problems with the Ariane wire
def update_comment_finals(request, match_id, comment_id):

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
            return redirect('tournaments:match_details_finals', match_id)
    
    context['form'] = form
    return render(request, 'tournaments/match_details_finals.html', user_authentication(request, context))


def final_round(request, tournament_id):
    force = False
    erase = False

    # Check if the "reset_pairings" button was clicked
    if request.method == "POST" and "reset_pairings" in request.POST:
        force = True
        erase = True

    # Get the tournament object
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    # Get the final round for this tournament, creating a new one if necessary
    final_round, created = FinalRound.objects.get_or_create(tournament=tournament)

    # Get the total number of matches in the final round
    TOTAL_MATCHES = final_round.get_total_matches()
    print(TOTAL_MATCHES)

    # Check if the number of matches is valid (a power of 2 and no more than 32)
    if (not math.log2(TOTAL_MATCHES).is_integer()) or (TOTAL_MATCHES > 32):
        messages.error(request, "The total number of matches must be a power of 2 and inferior to 32.")
        return redirect('tournaments:pool_details')

    else:
        print("entering else")

        # If "reset_pairings" was clicked, erase all matches from the final round
        if erase:
            print("erase")
            matches = final_round.matches.all()
            for match in matches:
                match.delete()
            final_round.matches.clear()
            FinalRound.objects.filter(tournament=tournament).delete()

        # If this is a new final round or "force" is True, create new pairings for the final round
        if created or force:
            print("créé")
            final_round = FinalRound.objects.create(tournament=tournament)
            final_round.create_pairings()
            final_round.refresh_from_db()

        # If the user is authenticated and a superuser, update the scores for each match
        if request.method == 'POST' and request.user.is_authenticated and request.user.is_superuser:
            for match in final_round.matches.all():
                match_id = str(match.id)
                score1 = request.POST.get(f'team1_score-{match_id}')
                score2 = request.POST.get(f'team2_score-{match_id}')
                if score1 is not None and score2 is not None:
                    match.score1 = int(score1)
                    match.score2 = int(score2)
                    match.save()
                    print(f"Updated scores for match {match_id}: {score1}-{score2}")
            final_round.generate_next_round()
            final_round.refresh_from_db()

        # Get the list of matches for the final round and the next round, if any
        print(list(final_round.matches.all()))
        next_round_matches = final_round.get_next_round_matches()
        matches = list(final_round.matches.all())

        
        # Creating arraylists for columns in template
        match_col1 = []
        match_col2 = []
        match_col3 =[]
        match_col4=[]
        match_col5=[]
        match_col6=[]
        
        #1+1/2+1/4+1/8+1/16 : at each round, you can add half the previous value
        for idx, match in enumerate(final_round.matches.all()):
            if idx < TOTAL_MATCHES:
                match_col1.append(match)
            elif TOTAL_MATCHES <= idx < (TOTAL_MATCHES * 1.5):
                match_col2.append(match)
            
            elif TOTAL_MATCHES<=idx <(TOTAL_MATCHES*1.75):
                match_col3.append(match)
                
            elif TOTAL_MATCHES<=idx <(TOTAL_MATCHES*1.875):
                match_col4.append(match)
                
            elif TOTAL_MATCHES<=idx <(TOTAL_MATCHES*1.9375):
                match_col5.append(match)
            
            elif TOTAL_MATCHES<=idx <(TOTAL_MATCHES*1.96875):
                match_col6.append(match)
                
        unplayed_matches1 = [match for match in match_col1 if match.score1 == 0 and match.score2 == 0]
        can_enter_column2_scores = len(unplayed_matches1) == 0 
        
        unplayed_matches2 = [match for match in match_col2 if match.score1 == 0 and match.score2 == 0]
        can_enter_column3_scores = len(unplayed_matches2) == 0 
        
        unplayed_matches3 = [match for match in match_col3 if match.score1 == 0 and match.score2 == 0]
        can_enter_column4_scores = len(unplayed_matches3) == 0 
        
        unplayed_matches4 = [match for match in match_col4 if match.score1 == 0 and match.score2 == 0]
        can_enter_column5_scores = len(unplayed_matches4) == 0 
        
        unplayed_matches5 = [match for match in match_col5 if match.score1 == 0 and match.score2 == 0]
        can_enter_column6_scores = len(unplayed_matches5) == 0 
                            
        context = {
            'final_round': final_round,
            'match_col1': match_col1,
            'match_col2': match_col2,
            'match_col3' : match_col3,
            'match_col4' : match_col4,
            'match_col5' : match_col5,
            'match_col6' :match_col6,
            'tournament_id': tournament_id,
            'next_round_matches': final_round.get_next_round_matches(),
            #Enables dynamic display of modification options for the superuser
            'can_enter_column2_scores': can_enter_column2_scores,
            'can_enter_column3_scores': can_enter_column3_scores,
            'can_enter_column4_scores': can_enter_column4_scores,
            'can_enter_column5_scores': can_enter_column5_scores,
            'can_enter_column6_scores': can_enter_column6_scores,
            'log2': log2,
            'range': range
        }
        return render(request, 'tournaments/final_round.html', user_authentication(request, context))


# This view generates a scatter plot of the teams in a pool based on their ranking.
def scatter_plot(request, pool_id):
    pool = Pool.objects.get(id=pool_id)
    teams_ranked = Pool.compute_ranking(pool)
    context = {'teams_ranked' : teams_ranked, 'pool': pool} 
    return render(request, 'tournaments/scatter_plot.html', context)

# This view generates a bar plot of the total number of goals scored by each team in a pool.
def goals_per_team_plot(request, pool_id):
    pool = Pool.objects.get(id=pool_id)
    teams_ranked = Pool.compute_ranking(pool)
    context = {'teams_ranked' : teams_ranked, 'pool': pool}
    return render(request, 'tournaments/goals_per_team_plot.html', context)

# This view generates a bar plot of the total number of goals scored in each match of a pool.
def goals_per_match_plot(request, pool_id):
    matches = Match.objects.filter(pool__id=pool_id).order_by('id')
    labels = []
    data = []

    for match in matches:
        labels.append(str(match.team1) + ' vs ' + str(match.team2))
        data.append(match.score1 + match.score2)

    chart = {
        'labels': labels,
        'data': data,
    }

    return render(request, 'tournaments/goals_per_match_plot.html', {'chart_data':json.dumps(chart)})
