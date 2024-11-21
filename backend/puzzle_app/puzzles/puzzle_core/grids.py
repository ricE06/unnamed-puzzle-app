"""
This file implements classes for puzzle grids.
"""
from abc import ABC, abstractmethod
from puzzles.puzzle_core.symbols import Symbol


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

    def __init__(self) -> None:
        self.symbols = [] # list of Symbol objects
    
class RectVertex(Vertex):
    """
    Represents a vertex in a rectangular grid.

    Attributes:
        symbols: a list of Symbol objects placed on this vertex.
        row_idx: the row coordinate (0 is top)
        col_idx: the column coordinate (0 is left)
    """

    def __init__(self, row_idx: int, col_idx: int) -> None:
        self.row_idx = row_idx
        self.col_idx = col_idx
        Vertex.__init__(self)

    @property
    def coords(self) -> tuple[int, int]:
        """
        Returns the row and col indices as a tuple.
        """
        return (self.row_idx, self.col_idx)


class Grid(ABC): # abstract class
    """
    This is an abstract class for a puzzle grid. All grids are
    treated as graphs internally, although certain shapes will allow for
    coordinate systems to make life easier.

    Methods:
        adjacent(self, vertex_1, vertex_2): checks if the two
            Vertex objects are adjacent.
    """
    vertices = []
    display_sep = ' '

    @abstractmethod
    def adjacent(self, vertex_1, vertex_2) -> bool:
        """
        Returns True if two vertex objects are adjacent to each other.
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
        max_len = 0
        for symbol in self.all_symbols:
            if new_len := len(symbol.short_name) > max_len:
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

    def __init__(self, height: int, width: int) -> None:
        self.height = height
        self.width = width
        self.vertices = self._gen_vertices()

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
        sep_len = self.longest_symbol_len + 1

        out = ""
        count_per_line = 0
        for vertex in self:
            # we know these are ordered
            count_per_line += 1
            sym = vertex.symbols[-1]
            out += sym
            out += self.display_sep * (sep_len - len(sym))
            if count_per_line >= self.width:
                out += "\n" # make a new line, reset count
                count_per_line = 0
        return out

