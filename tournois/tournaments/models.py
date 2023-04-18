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

class Equipe(models.Model):
    """
    A team, with several pools/matches
    """
    name = models.CharField(max_length=200)
    coach_name = models.CharField(max_length=200)
    team_members = models.CharField(max_length=2000)

    def __str__(self):
        return self.name

class Poule(models.Model):
    """
    A pool, with one tournament, and several teams/matches
    """
    number = models.IntegerField('Number of the pool')
    tournament = models.ForeignKey(Tournoi, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Equipe)

    def __str__(self):
        return "Pool number " + str(self.number) + " : " + str(self.tournament)

class Match(models.Model):
    """
    A match, several by pools, involving two teams
    """
    date = models.CharField(max_length=200)
    hour = models.CharField(max_length=200)
    place = models.CharField(max_length=200)
    team1 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='team1_set')
    score1 = models.IntegerField(default=0)
    team2 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='team2_set')
    score2 = models.IntegerField(default=0)
    pool = models.ForeignKey(Poule, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.score1) + " " + str(self.team1) + " vs " + str(self.team2) + " " + str(self.score2)