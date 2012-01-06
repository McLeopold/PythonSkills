class PlayerError(Exception):
    pass

class Player(object):
    '''
    Constructs a player.
    '''

    DEFAULT_PARTIAL_PLAY_PERCENTAGE = 1.0
    DEFAULT_PARTIAL_UPDATE_PERCENTAGE = 1.0

    def __init__(self, player_id=None,
                       partial_play_percentage=DEFAULT_PARTIAL_PLAY_PERCENTAGE,
                       partial_update_percentage=DEFAULT_PARTIAL_UPDATE_PERCENTAGE):
        if not (0.0001 <= partial_play_percentage <= 1.0):
            raise PlayerError("partial_player_percentage is not in the range [0.0001, 1.0]")
        if not (0.0 <= partial_update_percentage <= 1.0):
            raise PlayerError("partial_update_percentage is not in the range [0.0, 1.0]")

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
