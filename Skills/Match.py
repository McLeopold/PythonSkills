from Skills.Team import Team

class MatchError(Exception):
    pass

class Match(list):
    WIN = 0
    DRAW = 1
    LOSE = 2

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
            raise MatchError("Match does not have a ranking")

        rank_sorted, teams_sorted = map(list, zip(*sorted(zip(self.rank, self))))

        if rank_sorted != self.rank:
            # in-place update part
            for i, v in enumerate(teams_sorted):
                self[i] = v
            for i, v in enumerate(rank_sorted):
                self.rank[i] = v

    def comparison(self, team1=0, team2=1):
        if not self.rank:
            MatchError("Match instance does not have a ranking")
        else:
            if self.rank[team1] < self.rank[team2]:
                return self.WIN
            elif self.rank[team1] > self.rank[team2]:
                return self.LOSE
            else:
                return self.DRAW

    @staticmethod
    def ensure_match(match):
        if not hasattr(match, 'rank'):
            return Match(*match)
        else:
            return match
