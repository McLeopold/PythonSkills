class SkillCalculatorError(Exception):
    pass

class SkillCalculator():
    '''
    Base class for all skill calculator implementations.
    '''

    def __init__(self, supported_options, total_teams_allowed, players_per_team_allowed):
        self.supported_options = supported_options
        self.total_teams_allowed = total_teams_allowed
        self.players_per_team_allowed = players_per_team_allowed

    def calculate_new_ratings(self, game_info, teams_of_player_to_ratings):
        raise NotImplementedError("calculate_new_ratings not implemented")

    def is_supported(self, option):
        return self.supported_options & option == option

    def validate_team_count_and_players_count_per_team(self, teams_of_player_to_ratings):
        SkillCalculator.validate_team_count_and_players_count_per_team_with_ranges(teams_of_player_to_ratings,
                                                                                   self.total_teams_allowed,
                                                                                   self.players_per_team_allowed)

    @staticmethod
    def validate_team_count_and_players_count_per_team_with_ranges(teams, total_teams, players_per_team):
        count_of_teams = 0
        for current_team in teams:
            if len(current_team) not in players_per_team:
                raise SkillCalculatorError("player count is not in range")
        if len(teams) not in total_teams:
            raise SkillCalculatorError("team range is not in range")

class SkillCalculatorSupportedOptions():
    NONE = 0
    PARTIAL_PLAY = 1
    PARTIAL_UPDATE = 2
