#!/usr/bin/env python
"""A piece of ice.

"""


import random

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from geometry.point import Point
from geometry.vector import Vec2d
from geometry.angle import AngleInRadians

from util.base import choose_first_option_by_roulette
from util.geometry.lines import cells_between
from hockey.core.puck import Puck
from typing import Optional, Tuple

from hockey.behaviour.core.rule_based_brain import RuleBasedBrain
from hockey.core.player.base import Player
from hockey.core.player.defense import Defense
from hockey.core.player.forward import Forward
from hockey.core.model import TIME_PER_FRAME

class SkatingIce(Model):
    """The attacking side of a Hockey Rink."""

    def get_random_position(self) -> Point:
        """Returns a random position inside of the half-ice."""
        return Point(random.random() * self.width, random.random() * self.height)

    def __init__(self,
                 width: float,
                 height: float,
                 how_many_defense: int,
                 how_many_offense: int,
                 one_step_in_seconds: float,
                 collect_data_every_secs: float,
                 record_this_many_minutes: int):
        assert one_step_in_seconds > 0 and how_many_defense >= 0 and how_many_offense >= 0 and height > 0 and width > 0
        Model.__init__(self)
        self.HOW_MANY_MINUTES_TO_RECORD = record_this_many_minutes

        self.one_step_in_seconds = one_step_in_seconds
        # every how many steps do I have to collect data:
        self.collect_every_steps = (1 / self.one_step_in_seconds) * collect_data_every_secs
        self.height = height
        self.width = width
        self.schedule = RandomActivation(self)
        # if this was a Grid, the attribute would be called 'self.grid'
        # But because it is continuous, it is called 'self.space'
        self.space = ContinuousSpace(x_max=self.width, y_max=self.height, torus=False)
        # data collector
        self.datacollector = DataCollector(
            model_reporters={
                "steps": lambda m: m.schedule.steps,
                "timestamp": lambda m: m.schedule.steps * m.one_step_in_seconds,
                "puck_is_taken": lambda m: m.puck.is_taken,
                "goals": lambda m: m.goals_scored,
                "shots": lambda m: m.shots,
            },
            agent_reporters={
                "timestamp": lambda agent: agent.model.schedule.steps * agent.model.one_step_in_seconds,
                "pos_x": lambda agent : agent.pos.x,
                "pos_y": lambda agent: agent.pos.y,
                "speed_x": lambda agent: agent.speed.x,
                "speed_y": lambda agent: agent.speed.y,
                "speed_magnitude": lambda agent: agent.speed.norm(),
                "topuck_x": lambda agent: agent.model.vector_to_puck(a_pos = agent.pos).x if type(agent) != Puck else "",
                "topuck_y": lambda agent: agent.model.vector_to_puck(a_pos = agent.pos).y if type(agent) != Puck else "",
                "angle2puck": lambda agent: agent.model.angle_to_puck(a_pos = agent.pos, looking_at = agent.vector_looking_at()) if type(agent) != Puck else "",
                "last_action": lambda agent: agent.last_action if type(agent) != Puck else "",
                "have_puck": lambda agent: agent.have_puck if type(agent) != Puck else "",
                "can_see_puck": lambda agent: agent.can_see_puck() if type(agent) != Puck else "",
                "can_reach_puck": lambda agent: agent.can_reach_puck() if type(agent) != Puck else "",
            }
        )
        #
        self.count_defense = how_many_defense
        self.count_attackers = how_many_offense
        # Set up agents
        # init puck position
        self.puck = Puck(hockey_world_model=self)
        # defensive players: creation and random positioning
        self.defense = [Defense(hockey_world_model=self, brain=RuleBasedBrain()) for _ in range(self.count_defense)]
        # offensive players: creation and random positioning
        self.attack = [Forward(hockey_world_model=self, brain=RuleBasedBrain()) for _ in range(self.count_attackers)]
        # put everyone on the scheduler:
        [self.schedule.add(agent) for agent in [self.puck] + self.defense + self.attack]
        # init
        self.reset()

    def __str__(self):
        result = str(self.puck)
        result += "\nDefensive squad:\n"
        result += "\n".join([str(player) for player in self.defense])
        result += "\nOffensive squad:\n"
        result += "\n player \n".join([str(player) for player in self.attack])
        result += "\n"
        return result


    def reset(self):
        # positioning
        self.reset_agents()
        # number of goals scored, and shots made
        self.goals_scored = 0
        self.shots = 0
        print("Half-ice rink reset")

    def reset_agents(self):
        """Sets the players positions as at the beginning of an iteration."""

        self.release_puck()
        self.puck.speed = Vec2d(0, 0)
        self.set_random_positions_for_agents()
        # align with puck:
        [defense_player.align_with_puck() for defense_player in self.defense]
        [attacker.align_with_puck() for attacker in self.attack]

    def set_random_positions_for_agents(self):
        """Sets the players positions as at the beginning of an iteration."""

        self.space.place_agent(self.puck, pos = Point(0,0))
        [defense_player.reset(to_speed=0.01) for defense_player in self.defense]
        [attack_player.reset(to_speed=0.01) for attack_player in self.attack]
        p_player = Point(self.width - 1, self.height - 1)
        [self.space.place_agent(defense_player, pos = p_player) for defense_player in self.defense]
        [self.space.place_agent(attacker, pos = p_player) for attacker in self.attack]
        # TODO: _this_ is really 'random': (have to puck it back)
        # self.space.place_agent(self.puck, pos = self.get_random_position())
        # [self.space.place_agent(defense_player, pos = self.get_random_position()) for defense_player in self.defense]
        # [self.space.place_agent(attacker, pos = self.get_random_position()) for attacker in self.attack]
        #

    def release_puck(self):
        current_owner = self.who_has_the_puck()
        if current_owner is not None:
            current_owner.release_puck()

    def who_has_the_puck(self) -> Optional[Player]:
        """Returns None in no-one has the puck; otherwise returns the agent that has it."""
        for player in self.defense + self.attack:
            if player.have_puck:
                # print("[ICE] %s has the puck (its pos: %s; puck's: %s)" % (player.unique_id, player.pos, self.puck.pos))
                return player
        return None

    def is_puck_taken(self) -> bool:
        return not (self.who_has_the_puck() is None)


    def collect_data_if_is_time(self):
        num_data_collected = len(self.datacollector.model_vars)
        if self.schedule.steps >= (num_data_collected + 1) * self.collect_every_steps:
            self.datacollector.collect(self)

    def update_running_flag(self):
        self.running  = (self.schedule.steps <= (1 / TIME_PER_FRAME) * (60 * self.HOW_MANY_MINUTES_TO_RECORD))

    def step(self):
        """Run one step of the model. """
        self.schedule.step()
        self.collect_data_if_is_time()
        self.update_running_flag()


if __name__ == "__main__":
    hockey_rink = SkatingIce(width=10, height=3, how_many_offense=5, how_many_defense=5)
    d = Defense(hockey_world_model=hockey_rink, brain=RuleBasedBrain())
    print(hockey_rink)
