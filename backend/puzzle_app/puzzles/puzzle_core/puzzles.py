"""
This file implements the general Puzzle object.
This is what ends up being stored and sent to the frontend.
"""
import json
from typing import Any, Optional
from puzzles.puzzle_core.grids import Grid
from puzzles.puzzle_core.rules import Rule
from puzzles.puzzle_core.symbols import Symbol, BuiltinSymbols

class Puzzle():
    """
    A class for an entire puzzle that the user can solve.

    Instance attributes:
        grid: the Grid object the puzzle is played on
        rules: the Rule objects that the puzzle must obey
        editlayers: a list of dictionaries describing what states
            can the user edit to solve the puzzle

    Instance methods:
        __repr__: display the puzzle grid for debugging
        dump: get a JSON representation of the puzzle
    """

    def __init__(self, grid: Grid, 
                 symbols: list[Symbol],
                 rules: list[Rule],
                 editlayers: Optional[list[dict[str, Any]]] = None,
                 default_symbol: Optional[Symbol] = None) -> None:
        self.grid = grid
        self.symbols = symbols
        self.editlayers = editlayers if editlayers is not None else []
        self.rules = rules
        if default_symbol is not None:
            for vertex in grid:
                vertex.symbols = [default_symbol]

    def __str__(self):
        nl = '\n'
        return f"{nl.join(map(str, self.rules))}\n{self.grid}"

    def __repr__(self):
        return str(self)

    def dump(self):
        """
        Returns a JSON representation of the puzzle to
        pass to the frontend and database.
        """
        return json.dumps(self, default=lambda x: x.__dict__)

