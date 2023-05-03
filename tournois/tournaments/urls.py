from django.urls import path

from . import views

app_name = 'tournaments'

urlpatterns = [
    # ex: /tournaments/
    path('', views.tournaments_list, name='tournaments_list'),

    # ex: /tournaments/5/
    path('<int:tournament_id>/', views.tournament_details, name='tournament_details'),

    # ex: /tournaments/pool/5
    path('pool/<int:pool_id>/', views.pool_details, name='pool_details'),

    # ex: /tournaments/pool/5/compute_matches
    path('pool/<int:pool_id>/<int:compute_matches>/', views.compute_matches, name='compute_matches'),

    # ex: /tournaments/match/5
    path('match/<int:match_id>/', views.match_details, name='match_details'),
    
    # ex: /tournaments/match_finals/5
    path('match_finals/<int:match_id>/', views.match_details_finals, name='match_details_finals'),

    # ex: /tournaments/match/5/11
    path('match/<int:match_id>/<int:comment_id>/', views.update_comment, name='update_comment'),
    
    # ex: /tournaments/match_finals/5/11
    path('match_finals/<int:match_id>/<int:comment_id>/', views.update_comment_finals, name='update_comment_finals'),
    
    #ex : /tournaments/1/final_round
    path('<int:tournament_id>/final_round/', views.final_round, name='final_round'),
    
    
]