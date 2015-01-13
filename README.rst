======
skills
======

This is a Python port of the Moserware.Skills project that's available at

http://github.com/moserware/Skills

For more details on how the algorithm works, see 

http://www.moserware.com/2010/03/computing-your-skill.html

To install run the command::

    pip install skills

The match quality function of TrueSkill will run much faster with NumPy than with the provided matrix implementation.  Install with::

    pip install numpy

For details on how to use this project, see the accompanying unit tests with
this project.  You can run the tests by running the commands::

    # test all calculators
    python -m unittest discover
    
    # test just the elo calculator
    python -m unittest skills.testsuite.test_elo


Calculator Objects
==================

These objects should be created and passed into the calculators.  Most of these
objects will also except python tuples or lists and automatically create the
correct objects.

Player
------

Player is an object with a player_id (anything that is hashable) and some
partial play info.  Partial play is used for TrueSkill only.::

    Player(1)
    
    Player("Alice")

Rating
------

Rating is an object with a mean.  GaussianRating includes a stdev and is used
for the TrueSkill and Glicko calculators.  EloRating includes a k_factor and is
used for the Elo calculator.::

    Rating(100)
    
    GaussianRating(25.0, 8.333)
    
    EloRating(1200, 32)

RatingFactory creates a new Rating object of whatever type is needed.
RatingFactory.rating_class can be set to the Rating class desired.
Instantiating one of the calculators will set RatingFactory.rating_class
automatically.::

    RatingFactory.rating_class = GaussianRating
    RatingFactory.ensure_rating((25.0, 8.333))

Team
----

Team is a dictionary of Player objects mapped to Rating objects.  The objects
keys method maps to players, values maps to ratings and items maps to
player_rating.  The constructor can take a dictionary of player to ratings or a
list of player, rating tuples to create a multi-player team.::

    Team({1: (25.0, 8.333),
          2: (25.0, 8.333)})

    Team([(1, (25.0, 8.333)),
          (2, (25.0, 8.333))])

The Team object has convenience functions to find a player or rating by the
Player object's player_id property.::

    Team.rating_by_id(1)

Match
-----

Match is a list of teams and a ranking for each team.  It inherets from list and
includes a rank property, so regular lists can *not* be substituted.::

    Match([Team1, Team2], [1, 2])
    
The constructor is a convenience function that will call ensure team on each
team object passed in.  This allows for easy object construction.::

    Match( [(Player1, Rating1),
            (Player2, Rating2)],
           [1, 2] )

The Match object has convenience functions to find a player or rating in any
Team object by the Player object's player_id property.::

    Match.rating_by_id(1)

Match is synonomous with teams.

Matches
-------

Matches is a list of Match objects.  It inherits from list and a regular
sequence type can be substituted for it.::

    Matches([Match1, Match2])

The constructor is a convenience function that will call ensure_match for each
object in the list.  This allows for easy object construction.::

    Matches([ ([Team1, Team2], [1, 2]),
              ([Team2, Team3], [1, 2]) ])

The following is syntax that uses only tuples and lists to generate a list of
Matches:::

    Matches([([[(1, 1200)],
               [(2, 1200)]],
              [1, 2]),
             ([(2, 1200),
               (3, 1200)],
              [1, 2])])
              
    [Match([{Player(1): Rating(1200.0)}, {Player(2): Rating(1200.0)}],
            rank=[1, 2]),
     Match([{Player(2): Rating(1200.0)}, {Player(3): Rating(1200.0)}],
            rank=[1, 2])]              

