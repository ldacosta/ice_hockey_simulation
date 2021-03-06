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

class HockeyHalfRinkContinuous(Model):
    """The attacking side of a Hockey Rink."""

    WIDTH_HALF_ICE = 3 # 10 # 100 # TODO!
    HEIGHT_ICE = 3 # 10 # 85 # TODO!
    GOALIE_X = WIDTH_HALF_ICE - 11
    GOALIE_WIDTH = 6
    GOALIE_Y_BOTTOM = HEIGHT_ICE / 2 - GOALIE_WIDTH / 2
    GOALIE_Y_TOP = GOALIE_Y_BOTTOM + GOALIE_WIDTH
    GOALIE_CENTER = Point(GOALIE_X, (GOALIE_Y_TOP + GOALIE_Y_BOTTOM) / 2)
    GOALIE_POST_1 = Point(GOALIE_X, GOALIE_Y_BOTTOM)
    GOALIE_POST_2 = Point(GOALIE_X, GOALIE_Y_TOP)
    OFF_FACEOFF_X = GOALIE_X - 20
    BLUE_LINE_X = 25
    NEUTRAL_FACEOFF_X = BLUE_LINE_X - 2
    FACEOFF_TOP_Y = (HEIGHT_ICE - 44) / 2
    FACEOFF_BOTTOM_Y = FACEOFF_TOP_Y + 44

    def get_random_position(self) -> Point:
        """Returns a random position inside of the half-ice."""
        return Point(random.random() * self.width, random.random() * self.height)

    def __init__(self, how_many_defense: int, how_many_offense: int, one_step_in_seconds: float, collect_data_every_secs: float, record_this_many_minutes: int):
        assert one_step_in_seconds > 0 and how_many_defense >= 0 and how_many_offense >= 0
        Model.__init__(self)
        self.HOW_MANY_MINUTES_TO_RECORD = record_this_many_minutes

        self.one_step_in_seconds = one_step_in_seconds
        # every how many steps do I have to collect data:
        self.collect_every_steps = (1 / self.one_step_in_seconds) * collect_data_every_secs
        self.height = HockeyHalfRink.HEIGHT_ICE
        self.width = HockeyHalfRink.WIDTH_HALF_ICE
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
        self.goal_position = (HockeyHalfRink.GOALIE_X,(HockeyHalfRink.GOALIE_Y_BOTTOM, HockeyHalfRink.GOALIE_Y_TOP))
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
        result += "\nGoals scored: %d; shots = %d" % (self.goals_scored, self.shots)
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
        p_player = Point(HockeyHalfRink.WIDTH_HALF_ICE - 1,HockeyHalfRink.HEIGHT_ICE - 1)
        [self.space.place_agent(defense_player, pos = p_player) for defense_player in self.defense]
        [self.space.place_agent(attacker, pos = p_player) for attacker in self.attack]
        # TODO: _this_ is really 'random': (have to puck it back)
        # self.space.place_agent(self.puck, pos = self.get_random_position())
        # [self.space.place_agent(defense_player, pos = self.get_random_position()) for defense_player in self.defense]
        # [self.space.place_agent(attacker, pos = self.get_random_position()) for attacker in self.attack]
        #


    def puck_request_by(self, agent):
        """
        TODO: has to return True / False!
        
        Args:
            agent: 

        Returns:

        """
        current_owner = self.who_has_the_puck()
        if current_owner is None:
            self.give_puck_to(agent)
        else:
            power_holder = current_owner.power
            power_requester = agent.power
            if not choose_first_option_by_roulette(weight_1=power_holder, weight_2=power_requester):
                # print("[puck_request_by(%s)]: owner (strength %.2f) lost the puck to me (strength %.2f)" % (agent.unique_id, power_holder, power_requester))
                self.give_puck_to(agent)

    def prob_of_scoring_from_distance(self, distance_to_goal: float) -> float:
        # based on http://www.omha.net/news_article/show/667329-the-science-of-scoring
        if distance_to_goal <= 10:
            return 0.21
        elif distance_to_goal <= 20:
            return 0.34
        elif distance_to_goal <= 30:
            return 0.18
        elif distance_to_goal <= 40:
            return 0.11
        elif distance_to_goal <= 50:
            return 0.07
        elif distance_to_goal <= 60:
            return 0.05
        else:
            return 0.00

    def prob_of_scoring_from(self, a_pos: Point) -> float:
        """Probability of scoring from a certain point on the half-ice."""
        if a_pos.x > self.GOALIE_X:
            # behind the goal. Pas de chance.
            return 0.0
        else:
            return self.prob_of_scoring_from_distance(self.distance_to_goal(a_pos))

    def distance_to_goal(self, a_pos: Point) -> float:
        return Vec2d.from_to(from_pt=a_pos, to_pt=self.GOALIE_CENTER).norm()

    def distance_to_goal_posts(self, a_pos: Point) -> Tuple[float, float]:
        """Distance, in feet, to both goal posts"""
        return (a_pos.distance_to(another_point=self.GOALIE_POST_1),
                a_pos.distance_to(another_point=self.GOALIE_POST_2))

    def distance_to_closest_goal_post(self, a_pos: Point) -> float:
        """Distance, in feet, to closest goal post"""
        return min(self.distance_to_goal_posts(a_pos))

    def distance_to_puck(self, a_pos: Point) -> float:
        return Vec2d.from_to(from_pt=a_pos, to_pt=self.puck.pos).norm()

    def release_puck(self):
        current_owner = self.who_has_the_puck()
        if current_owner is not None:
            current_owner.release_puck()

    def give_puck_to(self, agent):
        if not agent.have_puck:
            self.release_puck()
            agent.have_puck = True
            self.puck.is_taken = True
            self.space.place_agent(self.puck, pos=agent.pos)

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
        # self.schedule.steps
        num_data_collected = len(self.datacollector.model_vars['goals'])
        if self.schedule.steps >= (num_data_collected + 1) * self.collect_every_steps:
            self.datacollector.collect(self)

    def update_running_flag(self):
        self.running  = (self.schedule.steps <= (1 / TIME_PER_FRAME) * (60 * self.HOW_MANY_MINUTES_TO_RECORD))

    def step(self):
        """Run one step of the model. """
        goals_before = self.goals_scored
        shots_before = self.shots
        self.schedule.step()
        self.collect_data_if_is_time()
        if self.shots > shots_before:
            self.puck.prob_of_goal = 0.0
        if self.goals_scored > goals_before:
            print("[half-rink] Goal scored! (now %d in total). Resetting positions of agents" % (self.goals_scored))
            self.reset_agents()
        self.update_running_flag()

    def vector_to_puck(self, a_pos: Point) -> Vec2d:
        return Vec2d.from_to(from_pt=a_pos, to_pt=self.puck.pos)

    def angle_to_puck(self, a_pos: Point, looking_at: Vec2d) -> AngleInRadians:
        """
        Angle to puck, defined in [0, 2Pi]. If puck is at the right of the vector
        defined by a straight line right in front of me, then this angle will be in [Pi, 2Pi]
        If it's at my left, the angle is in [0,Pi]
        """
        return looking_at.angle_to(self.vector_to_puck(a_pos))

    def vectors_to_goal(self, a_pos: Point) -> Tuple[Vec2d, Vec2d]:
        return (Vec2d.from_to(from_pt=a_pos, to_pt=self.GOALIE_POST_1),
                Vec2d.from_to(from_pt=a_pos, to_pt=self.GOALIE_POST_2))

    def angles_to_goal(self, a_pos: Point, looking_at: Vec2d) -> Tuple[AngleInRadians, AngleInRadians]:
        """
        Angle to puck, defined in [0, 2Pi]. If puck is at the right of the vector
        defined by a straight line right in front of me, then this angle will be in [Pi, 2Pi]
        If it's at my left, the angle is in [0,Pi]
        """
        v1, v2 = self.vectors_to_goal(a_pos)
        return (looking_at.angle_to(v1), looking_at.angle_to(v2))

    def min_angle_to_goal(self, a_pos: Point, looking_at: Vec2d) -> AngleInRadians:
        """
        Angle to puck, defined in [0, 2Pi]. If puck is at the right of the vector
        defined by a straight line right in front of me, then this angle will be in [Pi, 2Pi]
        If it's at my left, the angle is in [0,Pi]
        """
        return min(self.angles_to_goal(a_pos, looking_at))

    def first_visible_goal_point_from(self, a_position: Point) -> Optional[Point]:
        """From a certain position, can I see the goal?"""

        x, y = a_position
        # do I see _any_ part of the goal?
        goal_x = self.goal_position[0]
        if x > goal_x:
            # if I am behind the goal, I can't see any of its points
            return None
        y_in_goal = self.goal_position[1][0] - 1
        found_clear_path = False
        while (not found_clear_path) and (y_in_goal < self.goal_position[1][1]):
            y_in_goal += 1
            #
            cells_on_way = cells_between(a_position.as_tuple(), (goal_x, y_in_goal))
            # let's visit all cells to see if it's free
            free_path = True
            idx_cell_in_way = -1
            max_idx_cells_in_way = len(cells_on_way) - 1
            while free_path and idx_cell_in_way < max_idx_cells_in_way:
                idx_cell_in_way += 1
                x_in_way, y_in_way = cells_on_way[idx_cell_in_way]
                free_path = True # TODO. Was (in discrete space): self.grid.is_cell_empty(pos=(x_in_way, y_in_way))
            found_clear_path = free_path
        if found_clear_path:
            return Point(goal_x, y_in_goal)
        else:
            return None

    def clear_path_to_goal_from(self, a_position: Point) -> bool:
        """From a certain position, can I see the goal?"""
        return not (self.first_visible_goal_point_from(a_position) is None)


if __name__ == "__main__":
    hockey_rink = HockeyHalfRink(how_many_offense=5, how_many_defense=5)
    d = Defense(hockey_world_model=hockey_rink, brain=RuleBasedBrain())
    print(d)
    # while True:
    #     hockey_rink.step()
