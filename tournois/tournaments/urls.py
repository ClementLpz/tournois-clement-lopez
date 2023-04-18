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
]