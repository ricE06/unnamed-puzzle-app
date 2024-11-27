"""
This file contains a dictionary mapping keywords to
Rule objects, and a function to get and construct them.
"""

from puzzles.puzzle_core.builtin_rules import Nurikabe

class Lookup():
    """
    Class constants:
        TABLE: a dictionary mapping keywords to classes
    Static methods:
        construct_rule(keyword: str): returns an instance of the appropriate class
            associated with `keyword`
    """
    TABLE = {}

    @classmethod
    def get_cls(cls, obj_name: str, raw_str: bool = False):
        """
        Returns the class associated with `obj_name`.
        If it does not exist in TABLE, raises a ValueError.
        Args:
            obj_name: str, name of the class/object to look up in TABLE
            raw_str: bool. If set to True, then will be case-sensitive.
        """
        if not raw_str: obj_name = obj_name.lower()
        if obj_name not in cls.TABLE:
            raise ValueError(f'{obj_name} is not a valid builtin object!')
        return cls.TABLE[obj_name]

class RuleLookup(Lookup):
    TABLE = {'nurikabe': Nurikabe}

