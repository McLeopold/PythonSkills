from Skills.Team import Team

class Teams(list):
    def __init__(self, *teams):
        for team in teams:
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
