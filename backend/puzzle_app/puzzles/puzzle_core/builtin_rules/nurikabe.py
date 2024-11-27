"""
This file contains Rules and SuperRules for nurikabe.
"""
from puzzles.puzzle_core.rules import Rule, SuperRule
# import BuiltinSymbols during __init__ to avoid circular import

class Nurikabe(Rule):

    def __init__(self, symbol: str):
        """
        Creates a Nurikabe rule instance.
        Args:
            symbol (str): the short_name of the built-in symbol, NOT
                the Symbol object itself. `symbol` should be provided
                exactly in a text file.
        """
        from puzzles.puzzle_core.symbols import BuiltinSymbols
        self.symbol = BuiltinSymbols.get_symbol(symbol)
        Rule.__init__(self)

    def check(self, solution) -> bool:
        return True
