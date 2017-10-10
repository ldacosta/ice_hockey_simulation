from enum import auto

from core.action import Action

class HockeyAction(Action):

    NOOP = auto() # no operation
    # move forward
    MOVE_RANDOM_SPEED = auto()
    SPRINT = auto()
    SKATE_CALMLY = auto()
    # spinning around
    SPIN_RANDOMLY = auto()
    # doing something puck-related
    SHOOT = auto()
    PASS = auto()
    CHASE_PUCK = auto()
    GRAB_PUCK = auto()
