from django.db import models
from django.shortcuts import get_object_or_404

class Tournament(models.Model):
    """
    A tournament, with several pools, and teams
    """
    name = models.CharField(max_length=200)
    place = models.CharField(max_length=200, null=True)
    date = models.CharField(max_length=200, null=True)
    N_pools = models.IntegerField('Number of pools')
    N_teams_per_pools = models.IntegerField('Number of teams per pools')

    class Meta:
        db_table = "tournaments_tournoi"

    def __str__(self):
        return self.name

class Team(models.Model):
    """
    A team, with several pools/matches
    """
    name = models.CharField(max_length=200)
    coach_name = models.CharField(max_length=200)
    team_members = models.CharField(max_length=2000)
    pool_points = models.IntegerField('Number of pool points', null=True)
    scored = models.IntegerField('Number of goals scored', null=True)
    conceded = models.IntegerField('Number of goals conceded', null=True)

    class Meta:
        db_table = "tournaments_equipe"

    def __str__(self):
        return self.name

class Pool(models.Model):
    """
    A pool, with one tournament, and several teams/matches
    """
    number = models.IntegerField('Number of the pool')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)

    class Meta:
        db_table = "tournaments_poule"

    def __str__(self):
        return "Pool number " + str(self.number) + " : " + str(self.tournament)

    def all_matches(self):
        n = self.teams.size()
        for i in range(n - 1):
            for j in range(i + 1, n):
                match = get_object_or_404(Match)
                match.team1 = self.teams[i]
                match.team2 = self.teams[j]
                match.pool = self
                match.date = "01/01/2001"
                match.hour = "10h - 12h"
                match.place = self.tournament.place
                match.save()

    def compute_ranking(self):
        teams = self.teams.all()
        computed_pool_points = {}
        ranked_computed_teams = []

        for team in teams :

            for match in Match.objects.all() :

                if match.team1 == team :
                    team.scored += match.score1
                    team.conceded += match.score2

                    if (match.score1 == match.score2) :
                        team.pool_points += 1
                    elif (match.score1 > match.score2) :
                        team.pool_points += 3

                if match.team2 == team :
                    team.scored += match.score2
                    team.conceded += match.score1

                    if (match.score1 == match.score2) :
                        team.pool_points += 1
                    elif (match.score2 > match.score1) :
                        team.pool_points += 3

            computed_pool_points[team] = team.pool_points

        for k, v in sorted(computed_pool_points.items(), key=lambda x: -x[1]):
            ranked_computed_teams.append(k)

        return ranked_computed_teams

            
class Match(models.Model):
    """
    A match, several by pools, involving two teams
    """
    date = models.CharField(max_length=200)
    hour = models.CharField(max_length=200)
    place = models.CharField(max_length=200)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_set')
    score1 = models.IntegerField(default=0)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_set')
    score2 = models.IntegerField(default=0)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.score1) + " " + str(self.team1) + " vs " + str(self.team2) + " " + str(self.score2)