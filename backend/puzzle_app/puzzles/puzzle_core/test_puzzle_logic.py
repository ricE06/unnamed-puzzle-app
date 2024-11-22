"""
This file contains tests for the internal logic behind puzzles.
Tests that should go here include:
    proper storage of puzzles
    proper loading of a puzzles from text files
    proper loading of puzzles from json files
    correctly checking solution correctness for
    every single rule
    string representation of puzzles
    superrule behavior
"""
import pytest
from typing import cast
from puzzles.puzzle_core import Puzzle, RectGrid, BuiltinSymbols

class Test_Puzzles_Debug():
    """
    Tests the testing tools. So meta!
    """

    @pytest.fixture
    def example_tiny(self):
        grid = RectGrid(3, 2)
        white = BuiltinSymbols.white
        self.tiny = Puzzle(grid, [white], [], [white], white)

    def test_print_puzzle(self, example_tiny):
        exp = "\nWH WH \nWH WH \nWH WH \n"
        assert str(self.tiny) == exp

    def test_multiple_symbols_1(self, example_tiny):
        grid: RectGrid = cast(RectGrid, self.tiny.grid)
        grid.add_symbol(2, 0, BuiltinSymbols.black)
        exp = "\nWH    WH    \nWH    WH    \nWH-BK WH    \n"
        assert str(self.tiny) == exp

    def test_multiple_symbols_2(self, example_tiny):
        grid: RectGrid = cast(RectGrid, self.tiny.grid)
        grid.add_symbol(2, 0, BuiltinSymbols.black)
        grid.add_symbol(1, 1, BuiltinSymbols.empty) # this one is shorter
        grid.add_symbol(2, 1, BuiltinSymbols.black) 
        grid.add_symbol(2, 1, BuiltinSymbols.black) 
        exp = "\nWH       WH       \nWH       WH-_     \nWH-BK    WH-BK-BK \n"
        assert str(self.tiny) == exp

    def test_replace_symbol(self, example_tiny):
        grid: RectGrid = cast(RectGrid, self.tiny.grid)
        grid.replace_symbols(2, 0, [BuiltinSymbols.black])
        exp = "\nWH WH \nWH WH \nBK WH \n"
        assert str(self.tiny) == exp

    def test_numeric_symbols(self):
        grid = RectGrid(3, 2)
        all_nums = BuiltinSymbols.all_numerals()
        puz = Puzzle(grid, all_nums, [], all_nums, BuiltinSymbols.numeral(0))
        exp = "\n0 0 \n0 0 \n0 0 \n"
        assert str(puz) == exp
        grid.replace_symbols(0, 1, [BuiltinSymbols.numeral(4)])
        exp = "\n0 4 \n0 0 \n0 0 \n"
        assert str(puz) == exp
        grid.replace_symbols(1, 0, [BuiltinSymbols.numeral(14)])
        exp = "\n0  4  \n14 0  \n0  0  \n"
        print(exp)
        assert str(puz) == exp

class Test_Puzzle_Construct():
    """
    Tests the constructor for both text and json formats.
    """
