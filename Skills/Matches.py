from Skills.Match import Match

class Matches(list):

    def __init__(self, matches):
        for match in matches:
            self.append(Match.ensure_match(match))
