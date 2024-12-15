"""
This file contains a dictionary mapping keywords to
Rule objects, and a function to get and construct them.
"""

import inspect
from puzzles.puzzle_core.builtin_rules.nurikabe import (
        Nurikabe, 
        NoTwoByTwoSquare,
        RegionSizesEqualNumbers,
        Implicates,
        SingleConnectedRegion
)
from puzzles.puzzle_core.builtin_rules.lookup import Lookup
from puzzles.puzzle_core.rules import Rule

class RuleLookup(Lookup):
    TABLE = {name.lower(): rule for name, rule in globals().items() 
             if inspect.isclass(rule) and issubclass(rule, Rule)}
