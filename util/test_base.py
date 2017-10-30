# -*- coding: utf-8 -*-
"""
Test for base utilities
========================

TODO:

"""
import unittest
from random import random
from util.base import choose_by_roulette, choose_first_option_by_roulette, random_between

class TestUtilities(unittest.TestCase):
    """Testing definitions."""

    def setUp(self):
        """Initialization"""
        pass

    def test_roulette(self):
        """Test roulette choosing."""
        # if there is a negative weight, error:
        self.assertRaises(AssertionError, lambda: choose_by_roulette(weights=[-3, 0]))
        #
        self.assertEqual(choose_by_roulette(weights=[3, 0]), 0)
        self.assertEqual(choose_by_roulette(weights=[0, 3]), 1)
        self.assertEqual(choose_by_roulette(weights=[3, 0, 0, 0]), 0)
        #
        self.assertTrue(choose_first_option_by_roulette(3, 0))
        self.assertFalse(choose_first_option_by_roulette(0, 3))
        self.assertRaises(AssertionError, lambda: choose_first_option_by_roulette(0, -3))

    def test_random_in_range(self):
        """Get random numbers on a range."""
        for _ in range(10): # repeat this test several times
            a = random() / random()
            if random() < 0.5:
                a *= -1
            b = random() / random()
            if random() < 0.5:
                b *= -1
            the_min = min(a, b)
            the_max = max(a, b)
            in_between = random_between(the_min, the_max)
            assert (in_between >= the_min) and (in_between <= the_max)



