from django.contrib import admin

from .models import Tournament, Pool, Team, Match

admin.site.register(Tournament)
admin.site.register(Pool)
admin.site.register(Team)
admin.site.register(Match)