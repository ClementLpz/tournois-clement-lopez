from django.contrib import admin

from .models import Tournoi, Poule, Equipe

admin.site.register(Tournoi)
admin.site.register(Poule)
admin.site.register(Equipe)