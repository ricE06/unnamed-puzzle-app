# Serialize for the django REST framework.

from rest_framework import serializers
from puzzles.models import BuiltinPuzzle

class PuzzleSerializer(serializers.ModelSerializer):
    # see the BuiltinPuzzle model in models.py for information about these
    class Meta:
        model = BuiltinPuzzle
        fields = ['name', 'display_name', 'active']
        read_only_fields = ['puzzle_json']

    # equivalent to the below
    """
    name = serializers.CharField()
    display_name = serializers.CharField()
    puzzle_json = serializers.JSONField(read_only=True)
    """
