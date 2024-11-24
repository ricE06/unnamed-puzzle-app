"""
This file implements helper functions to:
    create Puzzle and Solution instances from text files
    create Puzzle and Solution instances from JSON files
    get a Puzzle instance from the id in the database
    create Solution instances
"""

from typing import Any
from abc import ABC, abstractmethod
from puzzles.puzzle_core import Puzzle

TEXT_COMMENT_SYMBOL = '%'
WHITESPACE = ' \t'
BRACES = '()'
LEFT_BRACE = '(' #)
RIGHT_BRACE = ')' 


class PuzzleConstructor():
    """
    Contains helper functions to load puzzles.
    """
    
    @staticmethod
    def load_txt(data: str) -> Puzzle:
        """
        Loads a puzzle from a raw text file.
        """
        raise NotImplementedError

    @staticmethod
    def load_json(data: dict) -> Puzzle:
        """
        Loads a puzzle from a raw json file.
        """
        raise NotImplementedError

class TextParser():

    class TextParsingError(Exception):
        pass

    class Parser(ABC):

        def parse(self, tokens: str|list) -> Any:
            print(f'{tokens=} in `parse`')
            if isinstance(tokens, list):
                if len(tokens) == 0:
                    return []
                return list(map(self.parse_one, tokens))
            return self.parse_one(tokens)

        @abstractmethod
        def parse_one(self, token: str|list) -> Any:
            raise NotImplementedError('Subclasses of Parser must implement `parse_one`!')

    class SelfParser(Parser):

        def parse_one(self, token: str|list[str]) -> str|list[str]:
            return token

    class BaseParser(Parser):

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
        DELIMITER = '-'
        EMPTY_TOKEN = '_'

        def parse_one(self, token: str|list) -> Any:
            if isinstance(token, list):
                raise TextParser.TextParsingError('States cannot be nested!')
            return tuple(token for token in token.split(self.DELIMITER) 
                         if token != self.EMPTY_TOKEN)

    class ListParser(Parser):

        def __init__(self, sub_parser):
            self.sub_parser = sub_parser

        def _parse_depreciated(self, tokens: str|list) -> Any:
            """This function serves no purpose as of now."""
            print(f'{tokens=} in ListParser `parse`')
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
        IMPLICIT_KEYS = {'-': 'type'}

        def __init__(self, sub_parser=None, custom_parsers=None):
            self.sub_parser = TextParser.SelfParser() if sub_parser is None else sub_parser
            self.custom_parsers = {} if custom_parsers is None else custom_parsers
            self.out_dict = {}

        def parse(self, tokens: str|list) -> Any:
            print(f'{tokens=} in DictParser `parse`')
            super().parse(tokens)
            copy = self.out_dict # careful, not a shallow copy
            self.out_dict = {}
            return copy

        def parse_one(self, token: str|list) -> Any:
            print(f'{token=} in `parse_one`')
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
            ptr: the pointer the parsing ended at and for the next parser to continue with
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



            
