"""
This file implements the general Puzzle object.
This is what ends up being stored and sent to the frontend.
"""
import json
from typing import Optional
from puzzles.puzzle_core.grids import Grid
from puzzles.puzzle_core.rules import Rule
from puzzles.puzzle_core.symbols import Symbol, BuiltinSymbols

class Puzzle():
    """
    A class for an entire puzzle that the user can solve.

    Instance attributes:
        grid: the Grid object the puzzle is played on
        symbols: a list of symbols that can be used to solve 
            the puzzle
        rules: the Rule objects that the puzzle must obey

    Instance methods:
        __repr__: display the puzzle grid for debugging
        dump: get a JSON representation of the puzzle
    """

    def __init__(self, grid: Grid, 
                 symbols: list[Symbol],
                 rules: list[Rule],
                 editable_symbols: list[Symbol],
                 default_symbol: Optional[Symbol] = BuiltinSymbols.empty) -> None:
        self.grid = grid
        self.symbols = symbols
        self.editable_symbols = editable_symbols
        self.rules = rules
        for vertex in grid:
            vertex.symbols.append(default_symbol)

    def __str__(self):
        return f"{'\n'.join(map(str, self.rules))}\n{self.grid}"

    def dump(self):
        """
        Returns a JSON representation of the puzzle to
        pass to the frontend and database.
        """
        return json.dumps(self, default=lambda x: x.__dict__)
