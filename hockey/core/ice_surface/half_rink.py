#!/usr/bin/env python
"""A piece of ice.

"""

from geometry.angle import AngleInRadians
from geometry.point import Point
from geometry.vector import Vec2d
from mesa.datacollection import DataCollector
from typing import Optional, Tuple

from hockey.core.folder_manager import FolderManager
from hockey.behaviour.core.rule_based_brain import RuleBasedBrain
from hockey.core.ice_surface.ice_rink import SkatingIce
from hockey.core.player.defense import Defense
from hockey.core.puck import Puck
from util.geometry.lines import cells_between


class HockeyHalfRink(SkatingIce):
    """The attacking side of a Hockey Rink."""

    WIDTH_HALF_ICE = 5 # 100 # TODO!
    HEIGHT_ICE = 5 # 85 # TODO!
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
        """
        assert how_many_defense >= 0 and how_many_offense >= 0
        SkatingIce.__init__(self,
                            width,
                            height,
                            how_many_defense,
                            how_many_offense)
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
                "pos_x": lambda agent: agent.pos.x,
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
        # init
        self.reset()

    def reset(self):
        SkatingIce.reset_agents(self)
        # number of goals scored, and shots made
        self.goals_scored = 0
        self.shots = 0
        print("Half-ice rink reset")

    def __str__(self):
        result = SkatingIce.__str__(self)
        result += "\nGoals scored: %d; shots = %d" % (self.goals_scored, self.shots)
        result += "\n"
        return result

    def save_activity(self, folder_manager: FolderManager):
        latest_model_file = folder_manager.newest_model_file()
        # max_tick = 0
        max_step = 0
        max_goals = 0
        max_shots = 0
        max_timestamp = 0
        if (latest_model_file is not None) and os.path.exists(latest_model_file):
            # update max's
            model_df = pd.read_csv(latest_model_file)
            # max_tick = max(max_tick, model_df["Unnamed: 0"].max())
            max_step = model_df["steps"].max()
            max_goals = model_df["goals"].max()
            max_shots = model_df["shots"].max()
            max_timestamp = model_df["timestamp"].max()
            print("Updating max_steps to %d, max_goals to %d, max_shots to %d, max_timestamp to %.2f" % (max_step, max_goals, max_shots, max_timestamp))
        _, full_model_file_name = folder_manager.suggest_model_file_name()
        print("[Model file] Chosen '%s'" % (full_model_file_name))
        # agents
        _, full_agents_file_name = folder_manager.suggest_agents_file_name()
        print("[Agents file] Chosen '%s'\n" % (full_agents_file_name))
        # update data
        model_df = self.datacollector.get_model_vars_dataframe()
        model_df["goals"] += max_goals
        model_df["shots"] += max_shots
        model_df["steps"] += max_step
        model_df["timestamp"] += max_timestamp
        agents_df = self.datacollector.get_agent_vars_dataframe()
        agents_df["timestamp"] += max_timestamp
        # ok, now save
        model_df.to_csv(full_model_file_name)
        agents_df.to_csv(full_agents_file_name)
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
