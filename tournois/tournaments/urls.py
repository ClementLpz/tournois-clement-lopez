from django.urls import path

from . import views

app_name = 'tournaments'

urlpatterns = [
    # ex: /tournaments/
    path('', views.tournaments_list, name='tournaments_list'),
]