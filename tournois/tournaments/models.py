from django.db import models

class Tournoi(models.Model):
    """
    A tournament, with several pools, and teams
    """
    name = models.CharField(max_length=200)
    place = models.CharField(max_length=200, null=True)
    date = models.CharField(max_length=200, null=True)
    N_pools = models.IntegerField('Number of pools')
    N_teams_per_pools = models.IntegerField('Number of teams per pools')

    def __str__(self):
        return self.name
