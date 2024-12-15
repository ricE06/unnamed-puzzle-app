"""
Routes URLs for accessing puzzles and checking puzzles.
"""
from puzzles.serializers import PuzzleSerializer
from rest_framework import viewsets

class PuzzleViewSet(viewsets.ViewSet):
    """
    A Viewset for getting built-in puzzles.
    """
