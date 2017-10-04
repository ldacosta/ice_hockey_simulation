# -*- coding: utf-8 -*-
"""
Test for base utilities
========================

TODO:

"""
import unittest

from util.base import choose_by_roulette, choose_first_option_by_roulette

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
