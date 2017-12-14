#!/usr/bin/env python
"""Provides Geometry for a particle moving on a container (ie, with walls).

"""

import numpy as np
from typing import Optional, Tuple

from geometry.point import Point
from geometry.vector import Vec2d
from util.base import FEET_IN_METER, GRAVITY_ACCELERATION

__author__ = "Luis Da Costa"
__email__ = "dacosta.le@gmail.com"

class Container(object):

    def __init__(self, height: float, width: float):
        """
        Defines a container with coordinate system going from (0,0) to (width, height).
        A particle can be at coordintes 0 and MAX (ie, both extremes must be valid points).
        Args:
            height: of container.
            width: of container.
        """
        self.width = width
        self.height = height

    def handle_walls(self,
                     length_of_movement: float,
                     particle_diameter: float,
                     curr_position: float,
                     curr_speed: float,
                     min_value: float,
                     max_value: float) -> Tuple[float, float]:
        """
        
        Args:
            length_of_movement: how ling is this particle moving, in seconds.
            curr_position: 
            curr_speed: 
            min_value: 
            max_value: 
            goal_on_max: 

        Returns:

        """
        # some definitions
        half_size = particle_diameter / 2
        min_valid_position = min_value + half_size
        max_valid_position = max_value - half_size
        #
        new_position = curr_position + curr_speed * length_of_movement
        new_speed = curr_speed
        if new_position <= min_valid_position:
            new_position = 2 * min_valid_position - new_position
            new_speed *= -1
        elif new_position >= max_valid_position:
            # formula is: (max_value - self.size) - (new_position - (max_value - self.size))
            new_position = 2 * max_valid_position - new_position
            new_speed *= -1

        # print("initial position = %.2f, new_position = %.2f, min_valid_position: %.2f, max_valid_position = %.2f" % (curr_position, new_position, min_valid_position, max_valid_position))
        if new_position >= min_valid_position and new_position <= max_valid_position:
            # all good
            return (new_position, new_speed)
        else:
            # rebounding again!
            if new_position <= min_valid_position:
                # distance travelled by the particle
                d = (max_valid_position - curr_position + 1) + (max_valid_position - min_valid_position)
                # time it took to travel:
                t = abs(d / curr_speed)
                # print("\tTravelled a distance of %.2f in %.2f time units" % (d, t))
                # so let's make it rebound again!
                return self.handle_walls(length_of_movement = length_of_movement - t,
                     particle_diameter = particle_diameter,
                     curr_position = min_valid_position,
                     curr_speed = new_speed,
                     min_value = min_value,
                     max_value = max_value)
            elif new_position >= max_valid_position:
                # print("new_position >= max_valid_position")
                # distance travelled by the particle
                d = (curr_position - min_valid_position + 1) + (max_valid_position - min_valid_position)
                # time it took to travel:
                t = abs(d / curr_speed)
                # print("\tTravelled a distance of %.2f in %.2f time units" % (d, t))
                # so let's make it rebound again!
                return self.handle_walls(length_of_movement = length_of_movement - t,
                     particle_diameter = particle_diameter,
                     curr_position = max_valid_position,
                     curr_speed = new_speed,
                     min_value = min_value,
                     max_value = max_value)

    # was: move_by_bouncing_from_walls
    def particle_move(self,
                      for_how_long: float,
                      particle_diameter: float,
                      particle_pos: Point,
                      particle_speed_vector: Vec2d,
                      friction_constant_opt: Optional[float] = None) -> Tuple[Point, Vec2d]:
        """
        All size units should be consistent with the units of the container.
        All time units are 'seconds'.
        
        Args:
            for_how_long: how ling is this particle moving, in seconds.
            particle_diameter: particle size (eg, diameter), in unts
            particle_pos: on units of the container.
            particle_speed_vector: on units of container/second.
            prob_of_score_on_goal_opt: 
            friction_constant_opt: 

        Returns:

        """

        # First, apply deceleration because of friction
        if friction_constant_opt is not None:
            friction = friction_constant_opt
            # for reference: https://www.youtube.com/watch?v=y1kqH63-828
            if particle_speed_vector.x != 0:
                new_speed_x = np.sign(particle_speed_vector.x) * \
                              max(0.0, (abs(particle_speed_vector.x*FEET_IN_METER) - GRAVITY_ACCELERATION*friction)/FEET_IN_METER)
                particle_speed_vector.x = new_speed_x
            if particle_speed_vector.y != 0:
                new_speed_y = np.sign(particle_speed_vector.y) * \
                              max(0.0, (abs(particle_speed_vector.y*FEET_IN_METER) - GRAVITY_ACCELERATION*friction)/FEET_IN_METER)
                particle_speed_vector.y = new_speed_y
        #
        curr_x, curr_y = particle_pos

        (new_x, new_speed_x) = self.handle_walls(
                         length_of_movement = for_how_long,
                         particle_diameter = particle_diameter,
                         curr_position = particle_pos.x,
                         curr_speed = particle_speed_vector.x,
                         min_value = 0,
                         max_value = self.width)
        (new_y, new_speed_y) = self.handle_walls(
                         length_of_movement = for_how_long,
                         particle_diameter = particle_diameter,
                         curr_position = particle_pos.y,
                         curr_speed = particle_speed_vector.y,
                         min_value = 0,
                         max_value = self.height)
        # If you need debugging info, un-comment this:
        # print("[%s] current: pos => (%f,%f), speed => (%f,%f); in %f seconds, moving to: pos => (%f,%f), new speed => (%f,%f)" %
        #       (self.unique_id, particle_pos[0], particle_pos[1], particle_speed_vector[0], particle_speed_vector[1], TIME_PER_FRAME, new_x, new_y, new_speed_x, new_speed_y))
        new_speed_vector = Vec2d.origin_to(Point(new_speed_x, new_speed_y))
        new_pos = Point(new_x, new_y)
        return (new_pos, new_speed_vector)

