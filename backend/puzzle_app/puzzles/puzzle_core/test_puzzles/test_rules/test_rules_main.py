"""
This module runs tests for each individual rule implemented.
There will be a lot of them.
"""
from typing import Callable
from puzzles.puzzle_core import Puzzle, PuzzleConstructor, Rule
from puzzles.puzzle_core.builtin_rules.nurikabe import NoTwoByTwoSquare

def gen_file_name(base_test_name: str) -> str:
    return f'puzzles/puzzle_core/test_puzzles/test_rules/test_rules_{base_test_name}.txt'

def load_puzzles_from_file(base_test_name: str) -> list[Puzzle]:
    file_name = gen_file_name(base_test_name)
    with open(file_name, 'r') as file:
        text = file.read()
        return PuzzleConstructor.load_txt_mult(text)

def load_expected_outputs(base_test_name: str) -> list[bool]:
    """
    Look for the pattern
    ```
    % !PPFFPPFP...
    ```
    and load a list of booleans, where each P is True (passing)
    and each F is False (failing).
    """
    file_name = gen_file_name(base_test_name)
    with open(file_name, 'r') as file:
        text = file.read()

    for line in text.splitlines():
        comment = False
        for idx, char in enumerate(line):
            if char == "%":
                comment = True
            elif char == "!" and comment:
                return [(char == 'p') for char in line[idx+1:].lower() if char in 'pf']
    return []

def _test_generator(base_test_name: str) -> Callable:
    """
    Returns a test function to test the puzzles in
        `base_test_name`.
    """
    def _testing_func(*args, **kwargs):
        puzzles  = load_puzzles_from_file(base_test_name)
        expected = load_expected_outputs(base_test_name)
        assert len(puzzles) == len(expected)
        for idx, (puz, exp) in enumerate(zip(puzzles, expected)):
            if not (checked := puz.check()):
                print(f"Puzzle #{idx}: {puz.error_msg = }")
            assert exp == checked, f"Test #{idx} checked incorrectly"

    return _testing_func
        

class Test_Nurikabe_Like():
    """
    Tests the Nurikabe superrule and its subrules.
    """

    test_no2x2 = _test_generator('notwobytwo')
    test_singleconnectedregion = _test_generator('singleconnectedregion')
    test_implicates = _test_generator('implicates')
    test_regsizeeqnum = _test_generator('regionsizesequalnumbers')
