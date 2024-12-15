from django.shortcuts import render
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from puzzles.serializers import PuzzleSerializer
from puzzles.models import BuiltinPuzzle

class PuzzleRetrieve(APIView):
    """
    Gets a specific puzzle from the database by name.
    """
    # queryset = BuiltinPuzzle.objects.all()

    @property
    def serializer_class(self):
        return PuzzleSerializer

    def _get_object(self, name: str) -> BuiltinPuzzle:
        try: 
            return BuiltinPuzzle.objects.get(name=name)
        except BuiltinPuzzle.DoesNotExist:
            raise Http404

    def get(self, request):
        name = request.query_params.get("name")
        puzzle = self._get_object(name=name)
        serializer = self.serializer_class(puzzle)
        assert isinstance(serializer.data, dict)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


# Create your views here.
