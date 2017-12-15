#!/usr/bin/env python
"""A piece of ice.

"""

from hockey.core.ice_surface.ice_rink import SkatingIce

class IceNxN(SkatingIce):
    """The attacking side of a Hockey Rink."""

    def __init__(self,
                 width: int,
                 height: int,
                 how_many_defense: int,
                 how_many_offense: int):
        """

        Args:
            width: how many divisions on X
            height: how many divisions on Y
            how_many_defense: 
            how_many_offense: 
            one_step_in_seconds: 
            collect_data_every_secs: 
            record_this_many_minutes: 
        """
        assert how_many_defense >= 0 and how_many_offense >= 0
        SkatingIce.__init__(self,
                            width,
                            height,
                            how_many_defense,
                            how_many_offense)

class Ice5x5(IceNxN):
    """The attacking side of a Hockey Rink."""

    def __init__(self,
                 how_many_defense: int,
                 how_many_offense: int):
        """

        Args:
            width: how many divisions on X
            height: how many divisions on Y
            how_many_defense: 
            how_many_offense: 
            one_step_in_seconds: 
            collect_data_every_secs: 
            record_this_many_minutes: 
        """
        IceNxN.__init__(self,
                            5,
                            5,
                            how_many_defense,
                            how_many_offense)
