class SkillCalculatorError(Exception):
    pass

class SkillCalculator(object):
    '''
    Base class for all skill calculator implementations.
    '''

    def __init__(self, total_teams_allowed, players_per_team_allowed,
                 allow_partial_play=False, allow_partial_update=False):
        self.total_teams_allowed = total_teams_allowed
        self.players_per_team_allowed = players_per_team_allowed
        self.allow_partial_play = allow_partial_play
        self.allow_partial_update = allow_partial_update

    def calculate_new_ratings(self, game_info, teams):
        raise NotImplementedError

    def calculate_match_quality(self, game_info, match):
        raise NotImplementedError

    def validate_team_count_and_players_count_per_team(self, teams):
        if len(teams) not in self.total_teams_allowed:
            raise SkillCalculatorError("team range is not in range")
        if any(len(team) not in self.players_per_team_allowed for team in teams):
            raise SkillCalculatorError("player count is not in range")
