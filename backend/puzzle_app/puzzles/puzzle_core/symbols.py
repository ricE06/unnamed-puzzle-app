"""
This file implements the "things" that go in grids,
in a vague sense.
A Symbol object has both an internal representation
and an external representation displayed to the frontend.
"""

from puzzles.puzzle_core.builtin_rules.lookup import Lookup

class Symbol():
    """
    Represents a symbol that is used to fill a grid.
    """
    builtin_symbols = {}

    def __init__(self, short_name: str, file_name: str) -> None:
        self.short_name = short_name
        self.file_name = file_name
        self.builtin_symbols[short_name] = self
        self.type = self.__class__.__name__

    def dump(self):
        """
        Returns a JSON of all the information necessary to reconstruct
        the symbol on the frontend.
        """
        raise NotImplementedError('TODO: implement dump for Symbol class')

    def __eq__(self, other):
        """
        Magic method to check for equality between Symbols, which is done
        by comparing their short_names. This is because different Symbol
        instances may be created at some point, such as during testing or
        loading certain puzzles. Those should be treated as equal, and
        test cases should pass.
        """
        return self.short_name == other.short_name

    def __hash__(self):
        """
        Simple hash function. Warning: the number 1 and the string `1` are
        treated as the same in this implementation.
        """
        return hash(str(self))


    def __str__(self):
        """
        String representation of the symbol for internal use.
        """
        return self.short_name

    def __repr__(self):
        """
        Internal representation of the symbol for debugging.
        """
        return f'Symbol({self.short_name})'
        

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
    def get_symbol(short_name: str) -> Symbol:
        """
        Returns the symbol object with the correct name.
        Note any symbol object can be retrieved once
        it is initiated `somewhere`.
        """
        if short_name not in Symbol.builtin_symbols:
            raise ValueError(f'Symbol {short_name} is not a built-in symbol!')
        return Symbol.builtin_symbols[short_name]

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


# initialize all the number symbols to be looked up
BuiltinSymbols.all_numerals()


