"""
This file implements classes related to puzzle rules.
"""
from abc import ABC, abstractmethod
# from puzzles.puzzle_core.puzzles import Puzzle

class Rule(ABC): # abstract class
    """
    Abstract class to implement a rule.

    Class methods:
        check(solution): returns True if
            solution satisfies the constraints described
            by the Rule object, False otherwise. If False,
            this method should write to `self.error_msg` with
            an informative error message (such as where the mistake occured).
            
    """
    description = "Unknown rule."

    def __init__(self):
        self.type = self.__class__.__name__
        self.error_msg = f"Something wrong happened, but this rule {self.type} doesn't have an error\
message implemented."

    @abstractmethod
    def check(self, solution) -> bool:
        """
        Returns True if the solution satisfies the rule, False otherwise.
        `solution` must be of type Puzzle.
        """
        raise NotImplementedError("Subclasses of Rule must implement a `check` method!")

    def __str__(self):
        return self.description

class SuperRule(Rule):
    """
    A superrule is composed of multiple rules and
    requires all of them to be true.
    """
    description = "Unknown superrule."

    def __init__(self, subrules: list[Rule]) -> None:
        self.subrules = subrules
        Rule.__init__(self)

    def check(self, solution) -> bool:
        """
        Returns True if the solution satisfies the superrule, False otherwise.
        """
        valid = min(True, *(rule.check(solution) for rule in self.subrules))
        self.error_msg = "\n".join(list(subrule.error_msg for subrule in self.subrules))
        return valid
            

