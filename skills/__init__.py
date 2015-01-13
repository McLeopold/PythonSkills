"""Ranking calculators implementing the Elo, Glicko and TrueSkill algorithms."""

from math import sqrt
from collections import Sequence
from skills.numerics import Gaussian


WIN = 0
DRAW = 1
LOSE = 2


class Calculator(object):
    '''Base class for all skill calculator implementations.'''

    def __init__(self, total_teams_allowed, players_per_team_allowed,
                 allow_partial_play=False, allow_partial_update=False):
        self.total_teams_allowed = total_teams_allowed
        self.players_per_team_allowed = players_per_team_allowed
        self.allow_partial_play = allow_partial_play
        self.allow_partial_update = allow_partial_update

    def new_ratings(self, game_info, match):
        raise NotImplementedError

    def match_quality(self, game_info, match):
        raise NotImplementedError

    def validate_team_and_player_counts(self, match):
        if len(match) not in self.total_teams_allowed:
            raise ValueError("team count is not in {0}"
                             .format(self.total_teams_allowed))
        if any(len(team) not in self.players_per_team_allowed
               for team in match):
            raise ValueError("player count is not in {0}"
                             .format(self.players_per_team_allowed))


class Match(list):
    '''Match is a list of Team objects'''

    def __init__(self, teams=None, rank=None):
        if teams is not None:
            for team in teams:
                self.append(Team.ensure_team(team))
        self.rank = rank

    def __repr__(self):
        if self.rank:
            return "Match(%s, rank=%s)" % (str(list(self)), str(self.rank))
        else:
            return "Match(%s)" % str(list(self))

    def add_team(self, team):
        self.append(Team.ensure_team(team))

    def player_by_id(self, player_id):
        for team in self:
            for player in team.players():
                if player.player_id == player_id:
                    return player

    def rating_by_id(self, player_id):
        for team in self:
            for player, rating in team.player_rating():
                if player.player_id == player_id:
                    return rating

    def player_rating_by_id(self, player_id):
        for team in self:
            for player, rating in team.player_rating():
                if player.player_id == player_id:
                    return player, rating

    def players(self):
        for team in self:
            for players in team.players():
                yield players

    def ratings(self):
        for team in self:
            for ratings in team.ratings():
                yield ratings

    def player_rating(self):
        for team in self:
            for player_rating in team.player_rating():
                yield player_rating

    def sort(self):
        '''
        Performs an in-place sort of the items in accordance to the ranks in non-decreasing order
        '''
        if not self.rank:
            raise AttributeError("Match does not have a ranking")

        rank_sorted, teams_sorted = map(list, zip(*sorted(zip(self.rank, self), key=lambda x: x[0])))

        if rank_sorted != self.rank:
            # in-place update part
            for i, v in enumerate(teams_sorted):
                self[i] = v
            for i, v in enumerate(rank_sorted):
                self.rank[i] = v

    def comparison(self, team1=0, team2=1):
        if not self.rank:
            AttributeError("Match instance does not have a ranking")
        else:
            if self.rank[team1] < self.rank[team2]:
                return WIN
            elif self.rank[team1] > self.rank[team2]:
                return LOSE
            else:
                return DRAW

    @staticmethod
    def ensure_match(match):
        if not hasattr(match, 'rank'):
            return Match(*match)
        else:
            return match


class Matches(list):
    '''Matches is a list of Match objects'''

    def __init__(self, matches):
        for match in matches:
            self.append(Match.ensure_match(match))


class Player(object):
    '''Player object contains a player id and parital play information'''

    DEFAULT_PARTIAL_PLAY_PERCENTAGE = 1.0
    DEFAULT_PARTIAL_UPDATE_PERCENTAGE = 1.0

    def __init__(self, player_id=None,
                       partial_play_percentage=DEFAULT_PARTIAL_PLAY_PERCENTAGE,
                       partial_update_percentage=DEFAULT_PARTIAL_UPDATE_PERCENTAGE):
        if not (0.0001 <= partial_play_percentage <= 1.0):
            raise ValueError("partial_player_percentage is not in the range [0.0001, 1.0]")
        if not (0.0 <= partial_update_percentage <= 1.0):
            raise ValueError("partial_update_percentage is not in the range [0.0, 1.0]")

        self.player_id = player_id
        self.partial_play_percentage = partial_play_percentage
        self.partial_update_percentage = partial_update_percentage

    def __repr__(self):
        if (self.partial_play_percentage != 1.0 or
                self.partial_update_percentage != 1.0):
            return "Player(%s, %s, %s)" % (self.player_id, self.partial_play_percentage, self.partial_update_percentage)
        else:
            return "Player(%s)" % self.player_id
    def __str__(self):
        return str(self.player_id)

    @staticmethod
    def ensure_player(player):
        if (not hasattr(player, 'player_id') or
                not hasattr(player, 'partial_play_percentage') or
                not hasattr(player, 'partial_update_percentage')):
            try:
                return Player(*player)
            except TypeError:
                return Player(player)
        else:
            return player


class Team(dict):
    '''
    Team maps player objects to rating objects
    '''

    def __init__(self, players=None):
        '''
        Construct a team dictionary

        Allows for a dictionary of players to ratings
            or a list of player, rating tuples

        Ensure players and ratings are of the proper class
        Allows for easy creation of team object using dictionaries or lists

            # passing 1 argument assumes 1 player to rating dictionary
            team = Team({1: (mean1, stdev1), 2: (mean2, stdev2)})
            team = Team({player1: rating1, player2: rating2})

            # or 1 list of player, rating tuples
            team = Team([(player1, rating1), (player2, rating2)])
        '''
        if players is not None:
            try:
                player_rating_tuples = players.items()
            except AttributeError:
                player_rating_tuples = players
            try:
                for player, rating in player_rating_tuples:
                    self.add_player(Player.ensure_player(player),
                                    RatingFactory.ensure_rating(rating))
            except (TypeError, ValueError):
                raise TypeError("Improper player dict or list")

    def players(self):
        return list(self.keys())

    def ratings(self):
        return list(self.values())

    def player_rating(self):
        return list(self.items())

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

    def __lt__(self, other):
        '''
        In python3, you can't order dicts anymore. Since we do that in Match.sort
        we'll define a custom team sort based on the current contents for consistency
        '''
        return frozenset(self.items()) < frozenset(other.items())


class Rating(object):
    '''
    Rating contains just a value
    '''

    def __init__(self, mean):
        try:
            self.mean = float(mean)
        except ValueError:
            raise ValueError("Rating mean value must be numeric")

    def __repr__(self):
        return "Rating(%s)" % (self.mean)

    def __str__(self):
        return "mean=%.5f" % (self.mean)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean')):
            try:
                return Rating(rating)
            except TypeError:
                raise TypeError("Rating was not given the correct amount of arguments")
        else:
            return rating


class RatingFactory(object):
    '''
    Factory to generation the correct rating type depending on the calculator
    
    Creating an instance of a calculator will set this automatically
    '''

    rating_class = Rating

    def __new__(self):
        return RatingFactory.rating_class()

    @staticmethod
    def ensure_rating(rating):
        return RatingFactory.rating_class.ensure_rating(rating)


class GaussianRating(Rating):
    '''Rating that includes a mean and standard deviation'''

    rating_class = None

    def __init__(self, mean, stdev):
        Rating.__init__(self, mean)
        try:
            self.stdev = float(stdev)
        except ValueError:
            raise ValueError("GaussianRating stdev value must be numeric")

    def __repr__(self):
        return "GaussianRating(%s, %s)" % (self.mean, self.stdev)

    def __str__(self):
        return "mean=%.5f, stdev=%.5f" % (self.mean, self.stdev)

    def conservative_rating(self, game_info):
        return self.mean - game_info.conservative_stdev_multiplier * self.stdev

    def partial_update(self, prior, full_posterior, update_percentage):
        prior_gaussian = Gaussian(prior.mean, prior.stdev)
        posterior_gaussian = Gaussian(full_posterior.mean, full_posterior.stdev)

        partial_precision_diff = update_percentage * (posterior_gaussian.precision - prior_gaussian.precision)

        partial_precision_mean_diff = update_percentage * (posterior_gaussian.precision_mean - prior_gaussian.precision_mean)

        partial_posterior_gaussian = Gaussian.from_precision_mean(
            prior_gaussian.precision_mean + partial_precision_mean_diff,
            prior_gaussian.precision + partial_precision_diff)

        return Rating(partial_posterior_gaussian.mean,
                      partial_posterior_gaussian.stdev)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'stdev')):
            if isinstance(rating, Sequence):
                try:
                    return GaussianRating(*rating)
                except TypeError:
                    raise TypeError("GaussianRating must be a sequence of "
                                    "length 2 or a GaussianRating object")
            else:
                try:
                    return GaussianRating(rating)
                except TypeError:
                    raise TypeError("GaussianRating was passed the wrong number"
                                    " of arguments")
        else:
            return rating
