from django.db import models

# Create your models here.

class BuiltinPuzzle(models.Model):
    """
    Represents a puzzle that can be sent to the player
    for them to solve. All puzzles are created and stored in the backend,
    there should be no put or post endpoint for this.
    """
    name = models.CharField(max_length=255) # descriptive of the puzzle (e.g. `nurikabe_4x4_1`)
    display_name = models.CharField(max_length=255) # shown to the user, something cute or funny (e.g. `Double Cross`)
    puzzle_json = models.JSONField() # the actual puzzle representation
    active = models.BooleanField() # puzzles can only be retreived if this field is TRue

    def __repr__(self):
        return f'BuiltinPuzzle with {self.name=}, {self.display_name=}, {self.puzzle_json=}, {self.active=}'

    def __str__(self):
        return self.__repr__()
