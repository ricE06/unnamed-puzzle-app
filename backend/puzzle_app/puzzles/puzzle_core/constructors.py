"""
This file implements helper functions to:
    create Puzzle and Solution instances from text files
    create Puzzle and Solution instances from JSON files
    get a Puzzle instance from the id in the database
    create Solution instances
"""

from typing import Any
from abc import ABC, abstractmethod
from puzzles.puzzle_core import Puzzle, Grid, BuiltinSymbols
from puzzles.puzzle_core.grids import GridLookup
from puzzles.puzzle_core.builtin_rules.LOOKUP_TABLE import RuleLookup

TEXT_COMMENT_SYMBOL = '%'
WHITESPACE = ' \t'
BRACES = '()'
LEFT_BRACE = '(' #)
RIGHT_BRACE = ')' 


class ConstructorError(Exception):
    pass

class PuzzleConstructor():
    """
    Contains helper functions to load puzzles.
    """
  
    @staticmethod
    def _all_except_type(inp_data: dict[str, Any], to_remove: str = 'type') -> dict[str, Any]:
        """Returns a new dictionary but with the `type` entry removed."""
        return {k: v for k, v in inp_data.items() if k != to_remove}

    @staticmethod
    def construct_from_dict(data: dict[str, Any]) -> Puzzle:
        """
        Constructs a Puzzle object from the dictionary given from
        a text parser. This dictionary may have the following keys:
            'grid', 'vertices', 'rules', 'editlayers', 'symbols'
        """
        # create Grid object
        if 'grid' not in data:
            raise ConstructorError('Input data needs a `grid` key!')
        grid_data = data['grid']
        grid_cls = GridLookup.get_cls(grid_data['type'])
        # put all other arguments except for type in the initiator as kwargs
        grid: Grid = grid_cls(**PuzzleConstructor._all_except_type(grid_data))

        # instantiate all the vertices on the grid, we don't create
        # the vertices in this function
        grid.init_vertices(vertex_data=data.get('vertices', {}))

        # create Rule objects
        rules = []
        for rule_entry in data.get('rules', []):
            rule_cls = RuleLookup.get_cls(rule_entry['type'])
            rule = rule_cls(**PuzzleConstructor._all_except_type(rule_entry))
            rules.append(rule)

        # create Symbol objects
        symbols = []
        for symbol_name in data.get('symbols', []):
            # no initiation needed, SymbolLookup returns the symbol instance
            symbol = BuiltinSymbols.get_symbol(symbol_name)
            symbols.append(symbol)
          
        editlayers = data.get('editlayers', [])
        # create Symbol objects within the editlayers
        for layer in editlayers:
            if 'symbols' not in layer:
                raise ConstructorError('An editlayer requires the `symbols` key!')
            if not layer['symbols']:
                raise ConstructorError('At least one symbol required in `symbols` key of an editlayer!')
            layer['symbols'] = list(map(BuiltinSymbols.get_symbol, layer['symbols']))

        # No support for default states right now, but it will automatically be
        # the first state in Symbols
        # default_symbol = symbols[0] if symbols else BuiltinSymbols.empty
        # create Puzzle object
        main_puzzle = Puzzle(grid=grid, rules=rules, symbols=symbols, 
                             editlayers=editlayers)
        return main_puzzle

    @staticmethod
    def load_txt_mult(data: str) -> list[Puzzle]:
        """
        Loads puzzles from a raw text file.
        See the .txt files in the /test_puzzles/ directory
        to reference how to format the files. Perhaps one day I'll add that
        to the documentation here...
        """
        parsed = TextParser.parse_txt(data)
        # construct each and return as new list
        return list(map(PuzzleConstructor.construct_from_dict, parsed))

    @staticmethod
    def load_json(data: dict) -> Puzzle:
        """
        Loads a single puzzle from a raw json file.
        """
        raise NotImplementedError

class TextParser():

    class TextParsingError(Exception):
        pass

    class Parser(ABC):
        """
        Abstract class for parsing text. The `parse` method
        is called on a nested token list, and uses a custom-defined
        `parse_one` method for each subclass. `parse_one` deals
        with a single token, at a time. If the token given is a list
        of tokens, `parse` will call `parse_one` on each of them.
        """

        def parse(self, tokens: str|list) -> Any:
            if isinstance(tokens, list):
                if len(tokens) == 0:
                    return []
                return list(map(self.parse_one, tokens))
            return self.parse_one(tokens)

        @abstractmethod
        def parse_one(self, token: str|list) -> Any:
            raise NotImplementedError('Subclasses of Parser must implement `parse_one`!')

    class SelfParser(Parser):
        """
        Simplest possible parser - just returns the token raw.
        """

        def parse_one(self, token: str|list[str]) -> str|list[str]:
            return token

    class BaseParser(Parser):
        """
        Similar to the self-parser, but will cast integers or floats
        if possible.
        """

        def number_or_other(self, token: str|list[str]) -> Any:
            if isinstance(token, list): return token
            try: return int(token)
            except ValueError: pass
            try: return float(token)
            except ValueError: pass
            return token

        def parse_one(self, token: str|list[str]) -> Any:
            return self.number_or_other(token)

    class StateParser(Parser):
        """
        Special parser to parse symbols.

        These will be passed as ONE continuous token, with the
        `short_name` of each token separated by a delimiter
        (see the DELIMITER constant, which should be `-`).
        """
        DELIMITER = '-'
        EMPTY_TOKEN = '_'

        def parse_one(self, token: str|list) -> Any:
            if isinstance(token, list):
                raise TextParser.TextParsingError('States cannot be nested!')
            return tuple(token for token in token.split(self.DELIMITER) 
                         if token != self.EMPTY_TOKEN)

    class ListParser(Parser):
        """
        Special parser to parse lists.
        To be clear, this is something that should OUTPUT a python list,
        and I am not referring to the fact that tokens are stored in lists.

        If `sub_parser` is given, each element will be processed by the sub_parser.
        This allows us to create lists of lists or lists of dictionaries.

        Could this technically be achieved with a self parser? Maybe. I don't
        have the guts to refactor the code and try, though.
        """

        def __init__(self, sub_parser):
            self.sub_parser = sub_parser

        def _parse_depreciated(self, tokens: str|list) -> Any:
            """This function serves no purpose as of now."""
            if isinstance(tokens, list) and len(tokens) == 0:
                return []
            if (isinstance(tokens, str) 
                or max(isinstance(token, str) for token in tokens)):
                # at least one token is a pure string
                # so we implicitly re-wrap
                tokens = [tokens]
            return super().parse(tokens)

        def parse_one(self, token: str|list) -> Any:
            return self.sub_parser.parse(token)

    class DictParser(SelfParser):
        """
        Special parser to parse tokens and return a python dictionary.

        The input format should be a series of 2-element tokens, where the
        first subtoken will be the key and the second subtoken will be value.
        The exception is if the token is an atomic token (i.e. just a string),
        the parser will look for an *implicit key*. The prefix will be automatically
        mapped to a built-in key, while the remainder of the string will be the value.
        For instance, `-class_name` yields {'type': 'class_name'}.
        See the IMPLICIT_KEYS class attribute below.

        If `sub_parser` is given, the value will be processed by the sub_parser.
        This allows us to create dictionaries of lists or dictionaries of other dictionaries.
        """
        IMPLICIT_KEYS = {'-': 'type'}

        def __init__(self, sub_parser=None, custom_parsers=None):
            self.sub_parser = TextParser.SelfParser() if sub_parser is None else sub_parser
            self.custom_parsers = {} if custom_parsers is None else custom_parsers
            self.out_dict = {}

        def parse(self, tokens: str|list) -> Any:
            super().parse(tokens)
            copy = self.out_dict # careful, not a shallow copy
            self.out_dict = {}
            return copy

        def parse_one(self, token: str|list) -> Any:
            if isinstance(token, str):
                if token[0] not in self.IMPLICIT_KEYS:
                    raise TextParser.TextParsingError(f'No implicit key found for {token}!')
                key = self.IMPLICIT_KEYS[token[0]]
                val = token[1:]
            else:
                if len(token) < 2:
                    raise TextParser.TextParsingError(
                            f'Assignment in DictParser requires a key and value!')
                key, *val = token
                if len(val) == 1: val = val[0]
                parser = self.custom_parsers.get(key, self.sub_parser)
                val = parser.parse(val)
            self.out_dict[key] = val
        

    @staticmethod
    def raw_tokens_txt(inp_txt: str) -> list[str]:
        """
        Tokens a text file, stripping whitespace and ignoring the
        comment delimiter.
        """
        def tokenize_line(line: str, out: list[str]) -> None:
            """Helper to tokenize a single line."""
            token = ""

            def end_token(token: str) -> str:
                if token:
                    out.append(token)
                    token = ""
                return token

            for char in line:
                if char in WHITESPACE:
                    # stop current token or ignore if no token exists
                    token = end_token(token)
                elif char in BRACES:
                    token = end_token(token)
                    out.append(char) # individual brace is a token, spaces or not
                elif char in TEXT_COMMENT_SYMBOL:
                    token = end_token(token)
                    break # ignore rest of the line
                else:
                    token += char

            end_token(token)
            return None # we mutate out in-place

        out = []
        for line in inp_txt.splitlines():
            tokenize_line(line, out)

        return out

    @classmethod
    def nested_tokens_txt(cls, inp_txt: str) -> list[list|str]:
        """
        Takes the tokens from `raw_token_txt` and nests them, such that
        any tokens that are surrounded by matching braces 
        are in a nested list.
        """
        tokens = cls.raw_tokens_txt(inp_txt)
        out = []
        left_idxs = []
        for idx, token in enumerate(tokens):
            if token == LEFT_BRACE:
                left_idxs.append(len(out)) # keep track of when nest starts
            elif token == RIGHT_BRACE:
                # put everything between left and right braces 
                # into its own list entry
                if not left_idxs:
                    raise TextParser.TextParsingError(f'Unmatched close brace at token #{idx}!')
                # append, not extend, as this is one entry
                last_idx = left_idxs.pop()
                new_token = out[last_idx:]
                out = out[:last_idx]
                out.append(new_token)
            else:
                out.append(token)
        return out

    @classmethod
    def parse_txt(cls, inp_txt: str) -> list[dict[str, Any]]:
        """
        Parses a text file. Returns a list of puzzle dictionaries.
        """
        tokens = cls.nested_tokens_txt(inp_txt)
        return [cls._parse_puzzle(puzz) for puzz in tokens]

    SUBPUZZLE_FLAG_PREFIX = '--'
    SUBPUZZLE_FLAGS = {'--rules': {'parser': ListParser(DictParser(BaseParser())), 
                                   'name': 'rules',
                                   'smart_wrap': False},
                       '--grid': {'parser': DictParser(BaseParser()), 'name': 'grid'},
                       '--vertices': {'parser': DictParser(BaseParser(), 
                                                           custom_parsers={'data': StateParser()}), 
                                      'name': 'vertices'},
                       '--symbols': {'parser': ListParser(SelfParser()),
                                     'name': 'symbols',
                                     'smart_wrap': False},
                       '--editlayers': {'parser': ListParser(DictParser(BaseParser())),
                                        'name': 'editlayers',
                                        'smart_wrap': False}}

    @classmethod
    def _parse_puzzle(cls, tokens: list[list|str]) -> dict[str, Any]:
        """
        Parses part of the tokens list that describes a puzzle dictionary.
        Returns:
            out: a dictionary describing the Puzzle object (but not a Puzzle object), this
                should be passed into the PuzzleConstructor
        """
        out = {}
        def add_attr_smart_wrapping(flag: str, expr: list|str) -> None:
            """Adds expr to out. Wraps it in a list if needed."""
            # if the wrapper is explicitly given, no need to re-wrap in a new list
            if (len(expr) == 1 
                and isinstance(expr[0], list)
                and cls.SUBPUZZLE_FLAGS[flag].get('smart_wrap', True)):
                expr = expr[0]
            puzzle_attr = cls.SUBPUZZLE_FLAGS[flag]['parser'].parse(expr)
            out[cls.SUBPUZZLE_FLAGS[flag]['name']] = puzzle_attr
            return None

        start_ptr = 0
        last_flag = None
        for ptr, flag in enumerate(tokens):
            if not (isinstance(flag, str) 
                    and flag.startswith(cls.SUBPUZZLE_FLAG_PREFIX)): # wait until next flag
                continue
            if (flag := flag.lower()) not in cls.SUBPUZZLE_FLAGS:
                raise cls.TextParsingError(f"Subpuzzle flag {flag} not recognized!")

            # implicit wrapping of all the tokens in between into a list
            expr = tokens[start_ptr+1:ptr]
            start_ptr = ptr
            # parse and add to dict
            if last_flag is not None: 
                add_attr_smart_wrapping(last_flag, expr)
            last_flag = flag

        # add the last flag to dict
        if last_flag is None: 
            raise cls.TextParsingError("No flags found in puzzle!")
        expr = tokens[start_ptr+1:]
        add_attr_smart_wrapping(last_flag, expr)
            
        return out



            
