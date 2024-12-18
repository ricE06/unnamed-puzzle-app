"""
This file implements classes for puzzle grids.
"""
from abc import ABC, abstractmethod
from typing import Optional
from puzzles.puzzle_core.builtin_rules.lookup import Lookup
from puzzles.puzzle_core.symbols import Symbol, BuiltinSymbols

class GridConstructorError(Exception):
    pass

class Vertex(): 
    """
    Represents a vertex in a grid.
    Maintains a reference to the symbol(s) that are placed onto it,
    as well as to the grid containing it.

    Attributes:
        symbols: a list of Symbol objects that are on this vertex
            in the puzzle.
            In the case of a Puzzle object, these are GIVENS;
            for a Solution object, they are either givens or 
            part of the solution.
    """
    EMPTY_VERTEX_REPR = '_'

    def __init__(self, symbols: Optional[list[Symbol]] = None) -> None:
        self.symbols = [] if symbols is None else symbols # list of Symbol objects
        self.type = self.__class__.__name__

    def symbols_str(self) -> str:
        """
        Returns the short names of all of the symbols on the vertex,
        joined by the `-` character.
        """
        if not self.symbols: return self.EMPTY_VERTEX_REPR
        return '-'.join(map(str, self.symbols))

    
class RectVertex(Vertex):
    """
    Represents a vertex in a rectangular grid.

    Attributes:
        symbols: a list of Symbol objects placed on this vertex.
        row_idx: the row coordinate (0 is top)
        col_idx: the column coordinate (0 is left)
    """

    def __init__(self, row_idx: int, col_idx: int, symbols: Optional[list[Symbol]] = None) -> None:
        self.row_idx = row_idx
        self.col_idx = col_idx
        Vertex.__init__(self, symbols)

    @property
    def coords(self) -> tuple[int, int]:
        """
        Returns the row and col indices as a tuple.
        """
        return (self.row_idx, self.col_idx)

    def __hash__(self):
        return hash(self.coords)

class Grid(ABC): # abstract class
    """
    This is an abstract class for a puzzle grid. All grids are
    treated as graphs internally, although certain shapes will allow for
    coordinate systems to make life easier.
    
    Attributes:
        vertices: (list[Vertex]) list of each vertex in the grid

    Methods:
        adjacent(self, vertex_1, vertex_2): checks if the two
            Vertex objects are adjacent.
    """
    vertices = []
    display_sep = ' '

    def __init__(self):
        self.type = self.__class__.__name__

    @abstractmethod
    def adjacent(self, vertex_1, vertex_2) -> bool:
        """
        Returns True if two vertex objects are adjacent to each other.
        """
        raise NotImplementedError

    @abstractmethod
    def init_vertices(self, vertex_data: dict) -> None:
        """
        Adds all the states to the vertices in `self.vertices`.
        Depending on the grid type, it may add the vertices themselves too.
        """
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a human readable version of the board for debugging.
        """
        raise NotImplementedError

    def __iter__(self):
        """
        Iterates over each vertex in the Grid, in no particular order.
        """
        yield from self.vertices

    @property
    def all_symbols(self) -> list[Symbol]:
        """
        Returns a list of all distinct states that show up in the vertices
        of the Grid instance.
        """
        out = []
        for vertex in self.vertices:
            for symbol in vertex.symbols:
                if symbol not in out:
                    out.append(symbol)
        return out

    @property
    def longest_symbol_len(self) -> int:
        """
        Returns the length of the longest symbol `short_name`
        attribute for printing to the terminal and saving a puzzle as text.
        """
        def len_of_all_symbols(vertex: Vertex) -> int:
            return len(vertex.symbols_str())

        max_len = 0
        for vertex in self.vertices:
            if (new_len := len_of_all_symbols(vertex)) > max_len:
                max_len = new_len
        return max_len

class RectGrid(Grid):
    """
    Implements a simple rectangular grid.
    
    Attributes:
        height: int, number of rows
        width: int, number of columns
        vertices: list of RectVertex objects
    """
    adj_differences = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    DEFAULT_SYMBOL = '_'

    def __init__(self, height: int, width: int, vertices: Optional[list[Vertex]] = None) -> None:
        self.height = height
        self.width = width
        self.vertices = self._gen_vertices() if vertices is None else vertices
        Grid.__init__(self)

    def _gen_vertices(self):
        """
        Returns a list of initial vertices.
        """
        out = []
        for row_idx in range(self.height):
            for col_idx in range(self.width):
                out.append(RectVertex(row_idx, col_idx))
        return out

    def adjacent(self, vertex_1: RectVertex, vertex_2: RectVertex) -> bool:
        diff_row = vertex_1.row_idx - vertex_2.row_idx
        diff_col = vertex_1.col_idx - vertex_2.col_idx
        return (diff_row, diff_col) in self.adj_differences

    def __str__(self) -> str:
        """
        Returns a string represenation of the grid. Spaces the vertices
        evenly, with at least one space between vertices.
        """
        sep_len = self.longest_symbol_len + 1

        out: str = ""
        count_per_line = 0
        for vertex in self:
            # we know these are ordered
            count_per_line += 1
            sym = vertex.symbols_str()
            out += sym
            out += self.display_sep * (sep_len - len(sym))
            if count_per_line >= self.width:
                out += "\n" # make a new line, reset count
                count_per_line = 0
        return out

    def get_vertex(self, row_idx: int, col_idx: int) -> RectVertex:
        """
        Returns the RectVertex at a certain row index and column index.
        """
        return self.vertices[row_idx*self.width + col_idx]

    def add_symbol(self, row_idx: int, col_idx: int, new_symbol: Symbol) -> None:
        """
        Appends `new_symbol` onto the vertex described by row_idx and col_idx.
        """
        vertex = self.get_vertex(row_idx, col_idx)
        vertex.symbols.append(new_symbol)

    def replace_symbols(self, row_idx: int, col_idx: int, new_symbols: list[Symbol]) -> None:
        """
        Replaces all the symbols at an vertex to the new symbols list.
        """
        vertex = self.get_vertex(row_idx, col_idx)
        vertex.symbols = new_symbols.copy() # shallow copy is okay, we aren't changing Symbols

    def init_vertices(self, vertex_data: dict) -> None:
        """
        Adds symbols to each vertex in `self.vertices`.
        `vertex_data` is the value of the `vertices` attribute
        in the full dictionary.
        """
        if 'data' not in vertex_data:
            raise GridConstructorError('Vertices require a `data` attribute!')

        encoding = vertex_data.get('encoding', 'full')
        data = vertex_data['data']
        default_symbol = vertex_data.get('default', self.DEFAULT_SYMBOL)
        default_symbol = BuiltinSymbols.get_symbol(default_symbol)
        if encoding == 'full':
            # set every vertex to have the symbols
            for vertex, state_tup in zip(self, data):
                if not state_tup:
                    vertex.symbols = [default_symbol]
                vertex.symbols = [BuiltinSymbols.get_symbol(name) for name in state_tup]
        else:
            raise GridConstructorError(f'Invalid encoding scheme {encoding}')

    def populate_by_coords(self, data: list[tuple[int, int, Symbol]]) -> None:
        """
        Adds symbols to the grid. Will override any existing symbols if needed,
        everything else is left alone.

        Args:
            data: list of tuples with three entries each:
                row (int)
                col (int)
                symbol (Symbol object)

        Returns: none
        """
        raise NotImplementedError
    
    def get_adjacencies(self, vertex: RectVertex) -> list[RectVertex]:
        """
        Given a RectVertex, return all of the RectVertex objects that are
        adjacent to it (diagonals NOT included).
        """
        out = []
        for dir in self.adj_differences:
            new_x = vertex.coords[0] + dir[0]
            new_y = vertex.coords[1] + dir[1]
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                out.append(self.get_vertex(new_y, new_x)) # new_y is row, new_x is col
        return out

    def region(self, seed: RectVertex, symbol: Symbol) -> list[RectVertex]:
        """
        Given a starting `seed` RectVertex, returns the connected region of vertices all
        containing `symbol` containing `seed`.
        """
        if symbol not in seed.symbols:
            return []
        # begin bfs
        visited = {seed}
        queue = [seed]
        qidx = 0 # we don't remove from the start, but keep track of where we are

        while qidx < len(queue):
            cur_vertex = queue[qidx]
            for new_vertex in self.get_adjacencies(cur_vertex):
                if new_vertex in visited:
                    continue
                visited.add(new_vertex)
                if symbol not in new_vertex.symbols:
                    continue
                queue.append(new_vertex)
            qidx += 1

        return queue


class VertexLookup(Lookup):
    TABLE = {'rectvertex': RectVertex}

class GridLookup(Lookup):
    TABLE = {'rectgrid': RectGrid}


