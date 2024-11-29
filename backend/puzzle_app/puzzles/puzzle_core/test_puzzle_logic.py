"""
This file contains tests for the internal logic behind puzzles.
Tests that should go here include:
    proper storage of puzzles
    proper loading of a puzzles from text files
    proper loading of puzzles from json files
    correctly checking solution correctness for every single rule
    string representation of puzzles
    superrule behavior
"""
import pytest
import pprint
import json
from typing import cast
from puzzles.puzzle_core import Puzzle, RectGrid, BuiltinSymbols, TextParser, PuzzleConstructor
from puzzles.puzzle_core.builtin_rules import Nurikabe

# we run `pytest` from the django base directory (the one with `manage.py` in it)
# this allows us to call `django.ini` and actually import everything correctly
PATH_TO_TEST_PUZZLES = 'puzzles/puzzle_core/test_puzzles/'

def load_from_file(base_file_name):
    file_name = PATH_TO_TEST_PUZZLES + base_file_name
    with open(file_name, 'r') as file:
        return file.read()


class Test_Puzzles_Debug():
    """
    Tests the testing tools. So meta!
    """

    @pytest.fixture
    def example_tiny(self):
        grid = RectGrid(3, 2)
        white = BuiltinSymbols.white
        self.tiny = Puzzle(grid=grid, symbols=[white], rules=[], editlayers=[{'symbols': ['WH']}])

    def test_print_puzzle(self, example_tiny):
        exp = "\nWH WH \nWH WH \nWH WH \n"
        assert str(self.tiny) == exp

    def test_multiple_symbols_1(self, example_tiny):
        grid: RectGrid = cast(RectGrid, self.tiny.grid)
        grid.add_symbol(2, 0, BuiltinSymbols.black)
        exp = "\nWH    WH    \nWH    WH    \nWH-BK WH    \n"
        assert str(self.tiny) == exp

    def test_multiple_symbols_2(self, example_tiny):
        grid: RectGrid = cast(RectGrid, self.tiny.grid)
        grid.add_symbol(2, 0, BuiltinSymbols.black)
        grid.add_symbol(1, 1, BuiltinSymbols.empty) # this one is shorter
        grid.add_symbol(2, 1, BuiltinSymbols.black) 
        grid.add_symbol(2, 1, BuiltinSymbols.black) 
        exp = "\nWH       WH       \nWH       WH-_     \nWH-BK    WH-BK-BK \n"
        assert str(self.tiny) == exp

    def test_replace_symbol(self, example_tiny):
        grid: RectGrid = cast(RectGrid, self.tiny.grid)
        grid.replace_symbols(2, 0, [BuiltinSymbols.black])
        exp = "\nWH WH \nWH WH \nBK WH \n"
        assert str(self.tiny) == exp

    def test_numeric_symbols(self):
        grid = RectGrid(3, 2)
        all_nums = BuiltinSymbols.all_numerals()
        puz = Puzzle(grid, all_nums, [], editlayers=[{'symbols': ['0']}])
        exp = "\n0 0 \n0 0 \n0 0 \n"
        assert str(puz) == exp
        grid.replace_symbols(0, 1, [BuiltinSymbols.numeral(4)])
        exp = "\n0 4 \n0 0 \n0 0 \n"
        assert str(puz) == exp
        grid.replace_symbols(1, 0, [BuiltinSymbols.numeral(14)])
        exp = "\n0  4  \n14 0  \n0  0  \n"
        assert str(puz) == exp

class Test_Text_Tokenizer():
    """
    Tests the tokenizer to parse an input text file correctly,
    all the way to returning the correct dictionary 
    (the equivalent of doing an easy JSON load).
    """

    def test_raw_tokens(self):
        simple = "(3) \n(t urt\t (le))"
        exp = ['(', '3', ')', '(', 't', 'urt', '(', 'le', ')', ')', ]
        output = TextParser.raw_tokens_txt(simple)
        assert exp == output

    def test_raw_tokens_2(self):
        simple = "(1 2 3\n 4 5 6\n 7 8 9)"
        exp = ['(', '1', '2', '3', '4', '5', '6', '7', '8', '9', ')']
        output = TextParser.raw_tokens_txt(simple)
        assert exp == output

    def test_raw_tokens_comments(self):
        simple = "(3) \t(t% urt\n (le))"
        exp = ['(', '3', ')', '(', 't', '(', 'le', ')', ')', ]
        output = TextParser.raw_tokens_txt(simple)
        assert exp == output

    def test_empty_tokens(self):
        empty = "%%%%%%%%%"
        exp = []
        output = TextParser.raw_tokens_txt(empty)
        assert exp == output

    def test_nested_tokens(self):
        simple = "(3) \n(t urt\t (le))"
        exp = [['3'], ['t', 'urt', ['le'], ], ]
        output = TextParser.nested_tokens_txt(simple)
        assert exp == output

    @pytest.fixture
    def self_parser(self):
        self.parser = TextParser.SelfParser()

    def test_self_parser_1(self, self_parser):
        token = ['3']
        exp = ['3']
        out = self.parser.parse(token)
        assert exp == out

    def test_self_parser_2(self, self_parser):
        token = ['3', '4']
        exp = ['3', '4']
        out = self.parser.parse(token)
        assert exp == out

    def test_self_parser_3(self, self_parser):
        token = [['3', '4']]
        exp = [['3', '4']]
        out = self.parser.parse(token)
        assert exp == out

    @pytest.fixture
    def state_parser(self):
        self.parser = TextParser.StateParser()

    def test_state_parser_1(self, state_parser):
        token = 'WH-BK-4'
        exp = ('WH', 'BK', '4')
        out = self.parser.parse(token)
        assert exp == out
    
    def test_state_parser_2(self, state_parser):
        token = '_'
        exp = tuple()
        out = self.parser.parse(token)
        assert exp == out
    
    def test_state_parser_3(self, state_parser):
        token = ['WH-BK-4', '_', '1']
        exp = [('WH', 'BK', '4'), tuple(), ('1',)]
        out = self.parser.parse(token)
        assert exp == out

    @pytest.fixture
    def list_parser(self):
        sub_parser = TextParser.StateParser()
        self.parser = TextParser.ListParser(sub_parser)

    def test_list_parser_1(self, list_parser):
        token = []
        exp = []
        out = self.parser.parse(token)
        assert exp == out
    
    def test_list_parser_2(self, list_parser):
        token = ['WH-BK-4', '_', '1']
        exp = [('WH', 'BK', '4'), tuple(), ('1',)]
        out = self.parser.parse(token)
        assert exp == out

    def test_list_parser_3(self, list_parser):
        token = ['WH-BK-4']
        exp = [('WH', 'BK', '4')]
        out = self.parser.parse(token)
        assert exp == out

    def test_list_parser_double_nested(self, list_parser):
        new_parser = TextParser.ListParser(self.parser)
        token = [['WH-BK-4', '_'], ['1', '4-5'], []]
        exp = [[('WH', 'BK', '4'), tuple()], [('1',), ('4', '5')], []]
        out = new_parser.parse(token)
        assert exp == out

    @pytest.fixture
    def dict_parser(self):
        sub_parser = TextParser.BaseParser()
        self.parser = TextParser.DictParser(sub_parser)

    def test_dict_parser_1(self, dict_parser):
        tokens = []
        exp = {}
        out = self.parser.parse(tokens)
        assert exp == out
    
    def test_dict_parser_2(self, dict_parser):
        tokens = [['five', '5'], ['six', '6'], ['8', 'ate']]
        exp = {'five': 5, 'six': 6, '8': 'ate'}
        out = self.parser.parse(tokens)
        assert exp == out
    
    def test_dict_parser_3(self, dict_parser):
        tokens = ['-nums', ['six', '6'], ['8', 'ate']]
        exp = {'type': 'nums', 'six': 6, '8': 'ate'}
        out = self.parser.parse(tokens)
        assert exp == out
    
    def test_dict_parser_4(self, dict_parser):
        tokens = ['-nums', ['six', '2', '4'], ['8', 'ate']]
        exp = {'type': 'nums', 'six': [2, 4], '8': 'ate'}
        out = self.parser.parse(tokens)
        assert exp == out

    def test_dict_parser_resets(self, dict_parser):
        tokens = ['-nums', ['six', '6'], ['8', 'ate']]
        exp = {'type': 'nums', 'six': 6, '8': 'ate'}
        out = self.parser.parse(tokens)
        assert exp == out
        tokens_2 = ['-game', ['1', '4'], ['3', '4']]
        exp_2 = {'type': 'game', '1': 4, '3': 4}
        out_2 = self.parser.parse(tokens_2)
        assert exp_2 == out_2
    
    def test_text_to_dict_1(self):
        text = load_from_file('test_parsing.txt')
        output = TextParser.parse_txt(text)
        assert isinstance(output, list) # should be list of two puzzles
        assert len(output) == 2
        exp_1 = {'rules': [], 
                 'grid': {'type': 'RectGrid',
                          'height': 3, 'width': 3},
                 'vertices': {'data': [tuple(), tuple(), ('3',),
                              tuple(), tuple(), tuple(),
                              ('1', ), tuple(), ('WH',)],
                              'type': 'RectVertex',
                              'encoding': 'full'}}
        assert output[0] == exp_1

    def test_text_to_dict_2(self):
        text = load_from_file('test_parsing.txt')
        output = TextParser.parse_txt(text)
        exp_2 = {'rules': [{'type': 'Nurikabe'},
                           {'type': 'Sudoku', 'reg_height': 3, 'reg_width': 2}], 
                 'grid': {'type': 'RectGrid',
                          'height': 3, 'width': 4},
                 'vertices': {'data': [tuple(), ('WH', 'BK'), tuple(), tuple(),
                              tuple(), ('3', '1', '0'), ('1', '5'), ('1',),
                              ('BK',), tuple(), ('BK',), ('BK',)],
                              'type': 'RectVertex',
                              'encoding': 'full'}}
        assert output[1] == exp_2

    def test_text_to_dict_implicit_wrapping(self):
        text = load_from_file('test_implicit_wrapping.txt')
        output = TextParser.parse_txt(text)
        exp = {'rules': [{'type': 'Nurikabe', 'symbol': 'BK'},],
                 'grid': {'type': 'RectGrid',
                          'height': 2, 'width': 2},
                 'vertices': {'data': [tuple(), tuple(), tuple(), ('1',)],
                              'type': 'RectVertex',}}
        assert output[0] == exp

    def test_text_to_dict_more_supertags(self):
        text = load_from_file('test_implicit_wrapping.txt')
        output = TextParser.parse_txt(text)
        exp = {'rules': [{'type': 'Nurikabe', 'symbol': 'BK'},],
                 'grid': {'type': 'RectGrid',
                          'height': 2, 'width': 2},
                 'vertices': {'data': [tuple(), tuple(), tuple(), ('1',)],
                              'type': 'RectVertex',},
               'symbols': ['WH', 'BK', '1'],
               'editlayers': [{'type': 'toggle', 'symbols': ['WH', 'BK']}]}
        assert output[1] == exp

      
class Test_Puzzle_Construct():
    """
    Tests the constructor for both text and json formats.
    """

    @pytest.fixture
    def well_formed(self):
        self.txt = load_from_file('test_constructor.txt')

    @pytest.fixture
    def puzzle_a(self):
        txt = load_from_file('test_constructor.txt')
        self.puzzle = PuzzleConstructor.load_txt_mult(txt)[0]

    def test_text_construction_simple(self, well_formed):
        puzzles = PuzzleConstructor.load_txt_mult(self.txt)
        assert isinstance(puzzles, list)
        assert len(puzzles) == 1

    def test_symbol_construction(self, puzzle_a):
        symbols = self.puzzle.symbols
        assert symbols == [BuiltinSymbols.white, BuiltinSymbols.black, BuiltinSymbols.numeral(1)]
    
    def test_rule_construction(self, puzzle_a):
        rules = self.puzzle.rules
        assert isinstance(rules, list)
        assert len(rules) == 1
        rule = rules[0]
        assert isinstance(rule, Nurikabe)
        assert rule.symbol == BuiltinSymbols.black
       
    def test_grid_construction(self, puzzle_a):
        exp = "WH   WH   \nBK   WH-1 \n"
        assert str(self.puzzle.grid) == exp

    def test_editlayer_construction(self, puzzle_a):
        exp = [{'mode': 'toggle',
               'symbols': [BuiltinSymbols.white, BuiltinSymbols.black]}]
        assert self.puzzle.editlayers == exp

    def test_raw_grid_construction(self, puzzle_a):
        raw_grid = self.puzzle.raw_grid
        exp = "_  _  \nBK 1  \n"
        assert str(raw_grid) == exp
    
    def test_json_dump_print_only(self, puzzle_a):
        pprint.pp(self.puzzle.dump())
        assert True

    def test_json_load_print_only(self, puzzle_a, well_formed):
        dumped = self.puzzle.dump()
        pprint.pp(json.loads(dumped))
        pprint.pp(TextParser.parse_txt(self.txt))
        assert True

    def test_json_symbol_construction(self, puzzle_a):
        dumped = self.puzzle.dump()
        reloaded = PuzzleConstructor.load_json(dumped)
        assert self.puzzle.symbols == reloaded.symbols

    def test_json_rule_construction(self, puzzle_a):
        dumped = self.puzzle.dump()
        reloaded = PuzzleConstructor.load_json(dumped)
        rules = reloaded.rules
        assert isinstance(rules, list)
        assert len(rules) == len(self.puzzle.rules)
        rule = rules[0]
        assert rule.type == self.puzzle.rules[0].type == 'Nurikabe'
        assert rule.symbol == self.puzzle.rules[0].symbol

    def test_json_grid_construction(self, puzzle_a):
        dumped = self.puzzle.dump()
        reloaded = PuzzleConstructor.load_json(dumped)
        assert str(self.puzzle.grid) == str(reloaded.grid)

    def test_json_raw_grid_construction(self, puzzle_a):
        dumped = self.puzzle.dump()
        reloaded = PuzzleConstructor.load_json(dumped)
        assert str(self.puzzle.raw_grid) == str(reloaded.raw_grid)

    def test_json_editlayer_construction(self, puzzle_a):
        dumped = self.puzzle.dump()
        reloaded = PuzzleConstructor.load_json(dumped)
        assert self.puzzle.editlayers == reloaded.editlayers

