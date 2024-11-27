"""
This file contains a dictionary mapping keywords to
Rule objects, and a function to get and construct them.
"""

from puzzles.puzzle_core.builtin_rules import Nurikabe
from puzzles.puzzle_core.builtin_rules.lookup import Lookup

class RuleLookup(Lookup):
    TABLE = {'nurikabe': Nurikabe}

