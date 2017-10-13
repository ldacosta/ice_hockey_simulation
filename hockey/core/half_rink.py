import random

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from geometry.point import Point
from geometry.vector import Vec2d

from util.base import choose_first_option_by_roulette
from util.geometry.lines import cells_between
from hockey.core.puck import Puck
from typing import Optional

from hockey.behaviour.core.rule_based_brain import RuleBasedBrain
from hockey.core.player.base import Player
from hockey.core.player.defense import Defense
from hockey.core.player.forward import Forward

class HockeyHalfRink(Model):
    """The attacking side of a Hockey Rink."""

    WIDTH_HALF_ICE = 100
    HEIGHT_ICE = 85
    GOALIE_X = WIDTH_HALF_ICE - 11
    GOALIE_WIDTH = 6
    GOALIE_Y_BOTTOM = HEIGHT_ICE / 2 - GOALIE_WIDTH / 2
    GOALIE_Y_TOP = GOALIE_Y_BOTTOM + GOALIE_WIDTH
    GOALIE_CENTER = Point(GOALIE_X, (GOALIE_Y_TOP + GOALIE_Y_BOTTOM) / 2)
    OFF_FACEOFF_X = GOALIE_X - 20
    BLUE_LINE_X = 25
    NEUTRAL_FACEOFF_X = BLUE_LINE_X - 2
    FACEOFF_TOP_Y = (HEIGHT_ICE - 44) / 2
    FACEOFF_BOTTOM_Y = FACEOFF_TOP_Y + 44

    def get_random_position(self) -> Point:
        """Returns a random position inside of the half-ice."""
        return Point(random.random() * self.width, random.random() * self.height)

    def __init__(self, how_many_defense: int, how_many_offense: int):
        Model.__init__(self)
        self.height = HockeyHalfRink.HEIGHT_ICE
        self.width = HockeyHalfRink.WIDTH_HALF_ICE
        self.schedule = RandomActivation(self)
        # if this was a Grid, the attribute would be called 'self.grid'
        # But because it is continuous, it is called 'self.space'
        self.space = ContinuousSpace(x_max=self.width, y_max=self.height, torus=False) # SingleGrid(height=self.height, width=self.width, torus=False)
        # TODO: properly set up the DataCollector
        # self.datacollector = DataCollector(
        #     {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]})# For testing purposes, agent's individual x and y
        self.datacollector = DataCollector()
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
        # positioning
        self.reset_positions_of_agents()
        # number of goals scored
        self.goals_scored = 0
        print("[Grid] Success on initialization")

    def reset_positions_of_agents(self):
        """Sets the players positions as at the beginning of an iteration."""

        self.space.place_agent(self.puck, pos = self.get_random_position())
        [self.space.place_agent(defense_player, pos = Point(self.GOALIE_X, self.get_random_position().y)) for defense_player in self.defense]
        [self.space.place_agent(attacker, pos = Point(self.BLUE_LINE_X, self.get_random_position().y)) for attacker in self.attack]


    def puck_request_by(self, agent):
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

    def give_puck_to(self, agent):
        current_owner = self.who_has_the_puck()
        if current_owner is not None:
            current_owner.release_puck()
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

    def step(self):
        '''
        Run one step of the model. 
        Halt the model if:
        * A Goal happened.
        * A "degagement" happened
        '''
        goals_before = self.goals_scored
        self.schedule.step()
        self.datacollector.collect(self)
        if self.goals_scored > goals_before:
            print("[half-rink] Goal scored! (now %d in total). Resetting positions of agents" % (self.goals_scored))
            self.reset_positions_of_agents()

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
            cells_on_way = cells_between(tuple(map(round, a_position.as_tuple())), (goal_x, y_in_goal))
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
