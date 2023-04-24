from django.contrib import admin

from .models import Tournament, Pool, Team, Match, Comment, FinalRound

admin.site.register(Tournament)
admin.site.register(Pool)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Comment)
admin.site.register(FinalRound)