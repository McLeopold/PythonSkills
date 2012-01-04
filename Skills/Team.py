from Player import Player
from Rating import RatingFactory

class TeamError(Exception):
    pass

class Team(dict):
    def __init__(self, player=None, rating=None):
        '''
        Construct a team dictionary
        
        Allows for a default player and rating
            or a dictionary of players to ratings
            or a list of player, rating tuples
        
        Ensure players and ratings are of the proper class
        Allows for easy creation of team object using dictionaries or lists
        
            # passing 2 arguments assumes 1 player and 1 rating
            team = Team(player_id, (mean, stdev))
            team = Team(player, rating)
            
            # passing 1 argument assumes 1 player to rating dictionary
            team = Team({1: (mean1, stdev1), 2: (mean2, stdev2)})
            team = Team({player1: rating1, player2: rating2})
            
            # or 1 list of player, rating tuples
            team = Team([(player1, rating1), (player2, rating2)])
        '''
        self.players = self.keys
        self.ratings = self.values
        self.player_rating = self.items
        if player is not None:
            if rating is None:
                try:
                    player_rating_tuples = player.items()
                except AttributeError:
                    player_rating_tuples = player
                try:
                    for p, rating in player_rating_tuples:
                        self.add_player(Player.ensure_player(p), RatingFactory.ensure_rating(rating))
                except (TypeError, ValueError):
                    raise TeamError("Improper player dict or list")
            else:
                self.add_player(Player.ensure_player(player), RatingFactory.ensure_rating(rating))

    def add_player(self, player, rating):
        self[Player.ensure_player(player)] = RatingFactory.ensure_rating(rating)
        return self

    def player_by_id(self, player_id):
        for player in self.keys():
            if player.player_id == player_id:
                return player

    def rating_by_id(self, player_id):
        for player, rating in self.items():
            if player.player_id == player_id:
                return rating

    def player_rating_by_id(self, player_id):
        for player, rating in self.items():
            if player.player_id == player_id:
                return player, rating

    @staticmethod
    def ensure_team(team):
        if (not hasattr(team, 'players') or
                not hasattr(team, 'ratings') or
                not hasattr(team, 'player_rating')):
            return Team(team)
        else:
            return team
