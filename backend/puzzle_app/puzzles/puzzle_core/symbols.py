"""
This file implements the "things" that go in grids,
in a vague sense.
A Symbol object has both an internal representation
and an external representation displayed to the frontend.
"""

class Symbol():
    """
    Represents a symbol that is used to fill a grid.
    """

    def __init__(self, short_name: str, file_name: str) -> None:
        self.short_name = short_name
        self.file_name = file_name

    def dump(self):
        """
        Returns a JSON of all the information necessary to reconstruct
        the symbol on the frontend.
        """
        raise NotImplementedError('TODO: implement dump for Symbol class')

    def __str__(self):
        """
        String representation of the symbol for internal use.
        """
        return self.short_name
        

class Number(Symbol):
    """
    Represents a numeric symbol.
    """
    file_prefix = "Num"

    def __init__(self, value: int) -> None:
        self.value = value
        Symbol.__init__(self, str(value), f'{self.file_prefix}_{value}')

class Colored(Symbol):
    """
    Represents a filled cell of a certain color.
    """
    file_prefix = "Color"

    def __init__(self, short_name: str) -> None:
        Symbol.__init__(self, short_name, f'{self.file_prefix}_{short_name}')

class BuiltinSymbols():
    """
    Collection of all the symbols used across puzzles.
    """
    _MAX_NUM = 31
    empty = Symbol('_', 'empty')
    white = Colored('WH')
    black = Colored('BK')

    @staticmethod
    def numeral(n):
        return Number(n)

    @classmethod
    def all_numerals(cls):
        """
        Constructs all the number symbols and returns as a list.
        """
        out = []
        for val in range(cls._MAX_NUM):
            out.append(cls.numeral(val))
        return out

