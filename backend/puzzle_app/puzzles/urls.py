"""
Contains URL endpoints for accessing and checking puzzles.
"""

from rest_framework import routers
from puzzles.views import PuzzleRetrieve
from django.urls import path

# puzzle_router = routers.SimpleRouter()
# puzzle_router.register('puzzles', PuzzleRetrieve, basename="puzzles")

urlpatterns = [
        path('puzzles', PuzzleRetrieve.as_view(), name='get-puzzles')
]

