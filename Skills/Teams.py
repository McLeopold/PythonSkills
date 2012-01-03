from Skills.Team import Team

class TeamsError(Exception):
    pass

class Teams(list):
    # The actual values for the enum were chosen so that they also correspond to
    # the multiplier for updates to means.
    WIN = 1
    DRAW = 0
    LOSE = -1

    def __init__(self, *teams, **kwds):
        for team in teams:
            self.append(Team.ensure_team(team))
        self.rank = kwds['rank'] if 'rank' in kwds else None

    def __repr__(self):
        if self.rank:
            return "Teams(%s, rank=%s)" % (str(list(self)), str(self.rank))
        else:
            return "Teams(%s)" % str(list(self))

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

    def sort(self):
        '''
        Performs an in-place sort of the items in accordance to the ranks in non-decreasing order
        '''
        if not self.rank:
            raise TeamsError("Teams does not have a ranking")

        rank_sorted, teams_sorted = map(list, zip(*sorted(zip(self.rank, self))))

        if rank_sorted != self.rank:
            # in-place update part
            for i, v in enumerate(teams_sorted):
                self[i] = v
            for i, v in enumerate(rank_sorted):
                self.rank[i] = v

    def comparison(self, winner=True):
        if not self.rank:
            TeamsError("Teams instance does not have a ranking")
        elif len(self.rank) != 2:
            TeamsError("Teams instance does not have exactly 2 teams")
        else:
            if self.rank[0] < self.rank[1]:
                return self.WIN if winner else self.LOSE
            elif self.rank[0] > self.rank[1]:
                return self.LOSE if winner else self.WIN
            else:
                return self.DRAW

    @staticmethod
    def FreeForAll(*players, **kwds):
        return Teams(*[[player] for player in players], **kwds)
