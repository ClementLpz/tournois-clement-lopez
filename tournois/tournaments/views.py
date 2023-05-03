from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.utils import timezone
from django.db.models import Q
import re

from .models import Tournament, Pool, Match, Comment, Team
from .forms import CommentForm, ResearchForm

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


def match_date(date) : # Parse date format '2 mai 2005' into '2005-05-02'
    month = ""
    match date[1].lower() :
        case "janvier" | "january" :
            month = "01"
        case "février" | "february" :
            month = "02"
        case "mars" | "march":
            month = "03"
        case "avril" | "april":
            month = "04"
        case "mai" | "may":
            month = "05"
        case "juin" | "june":
            month = "06"
        case "juillet" | "july":
            month = "07"
        case "août" | "august":
            month = "08"
        case "septembre" | "september":
            month = "09"
        case "octobre" | "october":
            month = "10"
        case "novembre" | "november":
            month = "11"
        case "décembre" | "december":
            month = "12"
        case _ :
            month = "01" # Default = January
    
    if (len(date[0]) == 1) : 
        date_str = date[2] + "-" + month + "-0" + date[0]
    else :
        date_str = date[2] + "-" + month + "-" + date[0]

    return date_str

def context_reset(context) : # Reset all (exept research) fields of context

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
