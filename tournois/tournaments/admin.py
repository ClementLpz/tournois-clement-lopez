from django.contrib import admin

from .models import Tournament, Pool, Team, Match, Comment, Place
class TeamAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # If this is a new object (not yet created)
            form.base_fields.pop('pool_points', None)
            form.base_fields.pop('conceded', None)
            form.base_fields.pop('scored', None)
        return form

admin.site.register(Tournament)
admin.site.register(Pool)
admin.site.register(Team, TeamAdmin)
admin.site.register(Match)
admin.site.register(Comment)
admin.site.register(Place)
