import random
from django.db import models
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.forms import ValidationError

import datetime
from django.db.models.signals import post_save


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

    """
    A function that adds to the database all the matches possible in a pool
    """

    def all_matches(self):
        n = self.teams.all().count()
        list_all_matches = list(self.teams.all())
        for i in range(n - 1):
            for j in range(i + 1, n):
                match = Match(team1 = list_all_matches[i], 
                              team2 = list_all_matches[j], 
                              pool = self, 
                              date = self.tournament.date,  
                              hour = "10h - 12h", 
                              place = self.tournament.place)
                match.save()

    """
    A function that computes the ranking of the teams in a pool, 
    with the matches results

    :returns: a list with the teams ranked by pool points
    """

    def compute_ranking(self):
        
        teams = self.teams.all()
        computed_pool_points = {}
        ranked_computed_teams = []

        for team in teams :

            for match in Match.objects.filter(pool=self) :
                match.team1.scored=0
                match.team1.conceded=0
                match.team2.scored=0
                match.team2.conceded=0

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

class Place(models.Model):
    name =  models.CharField(max_length=80)
    longitude = models.FloatField(null=False)
    latitude =  models.FloatField(null=False)
    def __str__(self):
        return self.name
    def script(self):
        return {"name": self.name, "latitude": self.latitude, "longitude": self.longitude}
        #return '[{"name":"' + str(self.name) + '", "latitude":"' + str(self.latitude) +'", "longitude":"'+str(self.longitude)+'"}]'
            
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
    localisation = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)
    round = models.IntegerField(default=1)

    def __str__(self):
        return str(self.score1) + " " + str(self.team1) + " vs " + str(self.team2) + " " + str(self.score2)
    
    def winner(self):
        if self.score1 > self.score2:
            return self.team1
        elif self.score2 > self.score1:
            return self.team2
        else:
            return None
    
    #For future improvements     
    def clean(self):
        super().clean()
        if self.score1 == self.score2:
            raise ValidationError("Les scores ne peuvent pas être égaux.")


class Comment(models.Model):

    """
    A comment, by one author, for one match
    """

    author = models.CharField(max_length=200)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Date & hour published', null=True)
    message = models.CharField(max_length=600)

    def __str__(self):
        return self.message
    

class FinalRound(models.Model):
    """
    A final round, with one tournament, and several matches
    """

    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE)
    matches = models.ManyToManyField(Match)  # Many-to-many relationship with Match
    rounds = models.IntegerField(default=1)  # Number of rounds completed so far

    class Meta:
        db_table = "tournaments_finalround"  # Name of the database table

    def __str__(self):
        return "Final Round for: " + str(self.tournament)  # String representation of the instance

    # Create pairings based on the pool ranking. The 1st of a pool must fight the 2nd of another random pool.
    def create_pairings(self):
        print("create_pairing called")
        pool_list = list(self.tournament.pool_set.all())  # Get all the pools for the tournament
        first_teams = []  # List of 1st ranked teams for each pool
        second_teams = []  # List of 2nd ranked teams for each pool

        for pool in pool_list:
            ranked_teams = pool.compute_ranking()  # Compute the ranking of teams for the pool
            first_teams.append(ranked_teams[0])  # Add the 1st ranked team to the first_teams list
            second_teams.append(ranked_teams[1])  # Add the 2nd ranked team to the second_teams list

        random.shuffle(second_teams)  # Shuffle the list of 2nd ranked teams

        for i in range(len(first_teams)):
            match = Match(
                team1=first_teams[i],
                team2=second_teams[i],
                pool=None,
                date=self.tournament.date,
                hour="10h - 12h",
                place=self.tournament.place,
            )
            match.save()  # Save the match to the database
            self.matches.add(match)  # Add the match to the matches many-to-many field
            # print(f"Match créé : {match.team1.name} vs {match.team2.name}")  --Debug

        self.save()  # Save the instance to the database
 
        
    #Useful for the template (since you can have 4, 8, 16, 32 teams)
    def get_total_matches(self):
        print("total matches called")
        pool_list = list(self.tournament.pool_set.all())
        return len(pool_list)
    
    #Helping create the next round match in finalround based on a list of winners from previous rounds
    @staticmethod
    def get_winners_from_previous_round(matches):
        winners = []
        # Print total number of matches
        print(f"Total matches: {len(matches)}") 
        for match in matches:
            # Print info for each match
            print(f"Checking winner for match {match.id}: {match.team1.name} ({match.score1}) vs {match.team2.name} ({match.score2})")
            winner = match.winner()
            if winner is not None:
                winners.append(winner)
                # Print info for winner found
                print(f"Winner found: {winner.name}")
            else:
                # Print info for no winner found
                print(f"No winner found for match {match.id}")
        # Print list of winners found
        print(f"Winners found: {winners}")
        return winners

    def get_next_round_matches(self):
        next_round_matches = []
        # Get list of completed matches
        completed_matches = [m for m in self.matches.all() if m.winner() is not None]
        if len(completed_matches) == self.matches.count():
            used_teams = []
            for match in self.matches.filter(round=self.rounds + 1):
                winner = match.winner()
                if winner and winner not in used_teams:
                    used_teams.append(winner)
                    # Get next round match for winner
                    next_round_match = Match.objects.filter(finalround=self, team1=winner).first()
                    if next_round_match is None:
                        next_round_match = Match.objects.filter(finalround=self, team2=winner).first()
                    if next_round_match:
                        next_round_matches.append(next_round_match)
        return next_round_matches

    def generate_next_round(self):
        print("generate next round called")
        matches = self.matches.all()
        # Get list of winners from previous round
        winners = FinalRound.get_winners_from_previous_round(matches)
        print(f"winner = {winners}")
        print(f"matches ={matches}")

        if len(winners) % 2 != 0:
            print("Erreur : la liste des vainqueurs doit être de longueur paire.")
            return
            
        else : 
            # Increase number of rounds and save
            self.rounds += 1
            self.save()
            if len(winners) >= 2:
                # Get the last two winners and create a match
                winner1, winner2 = winners[-2], winners[-1]
                match = Match(team1=winner1, team2=winner2, pool=None, date=self.tournament.date,
                        hour="10h - 12h", place=self.tournament.place, round=self.rounds)
                match.save()
                self.matches.add(match)
                return self.matches.all()
            else:
                winner1, winner2 = None, None
                
    def compute_ranking(self, Teams):
        
        team = Teams.objects.all()
        computed_pool_points = {}
        ranked_computed_teams = []

        

        for match in self.matches:
            match.team1.scored=0
            match.team1.conceded=0
            match.team2.scored=0
            match.team2.conceded=0

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