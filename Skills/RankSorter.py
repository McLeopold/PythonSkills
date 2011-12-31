class RankSorter():
    '''
    Helper class to sort ranks in non-decreasing order
    '''

    def __init__(self, teams, team_ranks):
        '''
        Performs an in-place sort of the items in accordance to the ranks in non-decreasing order
        '''
        teams_result, team_ranks_result = zip(*sorted(zip(team_ranks, teams)))

        # in-place update part
        for i, v in enumerate(teams_result):
            teams[i] = v
        for i, v in enumerate(team_ranks_result):
            team_ranks[i] = v

        return teams_result, team_ranks_result
