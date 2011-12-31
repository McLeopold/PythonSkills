class PartialPlay():

    @staticmethod
    def partial_play_percentage(player):
        if player.partial_play_percentage:
            return max(0.0001, player.partial_play_percentage)
        else:
            return 1.0
