"""
This file contains Rules and SuperRules for nurikabe.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from puzzles.puzzle_core.puzzles import Puzzle
    from puzzles.puzzle_core.grids import RectGrid, RectVertex

from puzzles.puzzle_core.rules import Rule, SuperRule
from puzzles.puzzle_core.symbols import Symbol, BuiltinSymbols, Number



class Nurikabe(SuperRule):

    def __init__(self, white_symbol: Symbol = BuiltinSymbols.white, 
                 black_symbol: Symbol = BuiltinSymbols.black, **kwargs):
        """
        Creates a Nurikabe rule instance.
        Args:
            white_symbol (optional, str): the short_name of the symbol corresponding to a white square
            black_symbol (optional, str): the short_name of the symbol corresponding to a black square

        See `https://puzz.link/rules.html?nurikabe` for a description
        of the rules and examples.
        """
        print(white_symbol.__repr__(), black_symbol)
        self.white_symbol = white_symbol
        self.black_symbol = black_symbol
        rules = [NoTwoByTwoSquare(self.black_symbol),
                 SingleConnectedRegion(self.black_symbol),
                 Implicates(BuiltinSymbols.all_numerals(), [self.white_symbol]),
                 RegionSizesEqualNumbers(self.white_symbol)]
        SuperRule.__init__(self, rules)

class NoTwoByTwoSquare(Rule):
    """
    Rule to enforce that there exist no 2x2 squares of a certain
    symbol in a RectGrid-like grid.

    Instance attributes:
        symbol: Symbol object to enforce this rule on. For example,
            if `self.symbol = Colored('BK')`, then this rule will enforce
            that the black squares do not form 2x2s. 

    Correct examples:
        X . X    X X X
        X X .    X . X
        X . .    X X X
    
    Incorrect examples:
        X X .    . . .
        X X .    X X X
        . X X    X X X
    """
    def __init__(self, symbol: Symbol, **kwargs):
        self.symbol = symbol
        Rule.__init__(self)

    def check(self, solution: Puzzle) -> bool:
        grid: RectGrid = solution.grid
        for x in range(grid.width-1):
            for y in range(grid.height-1):
                square_coords = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
                vertices = [grid.get_vertex(*coords) for coords in square_coords]
                # passing is True if and only if at least one vertex DOESN'T contain self.symbol
                passing = max((self.symbol not in vertex.symbols) for vertex in vertices)
                if not passing:
                    self.error_msg = f"Square detected with top-left coordinates ({x}, {y})!"
                    return False
        return True

class SingleConnectedRegion(Rule):
    """
    Rule to enforce that all vertices that contain a certain symbol
    are all connected to each other in a grid.

    Instance attributes:
        symbol: Symbol object to enforce this rule on.

    Correct examples:
        X . X   . . .
        X . X   . . X
        X X X   . . .

    Incorrect examples:
        X . X   . X X
        X . X   X . X
        X . X   . X .
    """

    def __init__(self, symbol: Symbol, **kwargs):
        self.symbol = symbol
        Rule.__init__(self)

    def check(self, solution: Puzzle) -> bool:
        grid: RectGrid = solution.grid

        # find the first instance of the symbol to
        # start the graph search
        def find_first_inst():
            for vertex in grid.vertices:
                if self.symbol in vertex.symbols:
                    return vertex
            return None
        
        seed: None|RectVertex = find_first_inst()
        if seed is None: return True # there is no region to speak of

        in_region = set(grid.region(seed, self.symbol))
        for vertex in grid.vertices:
            if vertex not in in_region and self.symbol in vertex.symbols:
                # there exists a vertex with the symbol NOT in this region
                self.error_msg = f"The square at {vertex.coords} is not part of a singular connected region!"
                return False 
        return True

class Implicates(Rule):
    """
    Rule to enforce that if at least one of `self.subset_symbols` 
    if present in a vertex, then at least one of `self.superset_symbols`
    must also be present.

    Instance attributes:
        subset_symbols: list[Symbol], the symbols that trigger the rule
        superset_symbols: list[Symbol], at least one of these symbols must
            be present if the vertex also has a symbol in subset_symbols. 

    Correct examples (with (`x`, `y`) being subset and (`X`, `Y`) being superset):
        X x-X
        Y Y-x

    Incorrect examples (there is an `X` without an `x`):
        X x
        . x-Y
    """

    def __init__(self, subset_symbols, superset_symbols, **kwargs):
        self.subset_symbols = subset_symbols
        self.superset_symbols = superset_symbols
        Rule.__init__(self)

    def _intersection(self, list1, list2):
        return [val for val in list1 if val in list2]

    def check(self, solution: Puzzle) -> bool:
        grid = solution.grid
        for vertex in grid.vertices:
            if not self._intersection(vertex.symbols, self.subset_symbols):
                continue
            if not self._intersection(vertex.symbols, self.superset_symbols):
                # contains something in subset but not in superset, fail
                self.error_msg = f"Square at {vertex.coords} must contain one of {self.superset_symbols}!"
                return False
        return True

class RegionSizesEqualNumbers(Rule):
    """
    Superrule to enforce that each numeric symbol must be in a region
    of equal size, and that each region contains exactly one number. 

    Instance attributes: 
        allowed_symbol: Symbol, represent the symbols that can be
            used to determine a region. For example, 1-WH-r could be
            the symbols in a vertex, but if allowed_symbols is [WH],
            then the region is determined by vertices with WH, not r.
    
    Correct examples:
        3-X X   1-X .    X .
        .   X   .   1-X  . X

    Incorrect examples:
        2-X X   0-X .
        X   X   .   .
    """
    
    def __init__(self, allowed_symbol: Symbol, **kwargs):
        self.allowed_symbol = allowed_symbol
        Rule.__init__(self)

    def check(self, solution: Puzzle) -> bool:
        grid: RectGrid = solution.grid
        visited = [] # list of all visited vertices
        for vertex in grid.vertices:
            for symbol in vertex.symbols:
                if isinstance(symbol, Number):
                    valid = self.check_one(grid, vertex, symbol.value, visited)
                    if not valid:
                        return False

        # check that no other regions exist
        visited = set(visited)
        for vertex in grid.vertices:
            if vertex not in visited:
                if self.allowed_symbol in vertex.symbols:
                    self.error_msg = "There exists a region without a number!"
                    return False
        return True
    
    def check_one(self, grid: RectGrid, seed: RectVertex, 
                  size: int, visited: list[RectVertex]):
        reg: list[RectVertex] = grid.region(seed, self.allowed_symbol)
        visited.extend(reg)
        # check size
        if len(reg) != size:
            self.error_msg = f"The number at {seed.coords} has an incorrect region size!"
            return False
        # check only one number
        num_count = 0
        for vertex in reg:
            for symbol in vertex.symbols:
                if not isinstance(symbol, Number): continue
                num_count += 1
                if num_count > 1:
                    self.error_msg = f"A region contains more than one number!"
                    return False
        return True
        

