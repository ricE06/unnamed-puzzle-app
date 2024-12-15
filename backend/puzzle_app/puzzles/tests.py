from django.test import TestCase
from django.urls import reverse
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APIClient, RequestsClient
from puzzles.models import BuiltinPuzzle
from puzzles.views import PuzzleRetrieve
import pytest
import json


class TestPuzzleModel():
    """
    Contains a suite of tests for proper saving and
    loading of built-in puzzles.
    """
    factory = APIRequestFactory()
    client = APIClient()

    @property
    def view(self):
        return PuzzleRetrieve.as_view()

    @pytest.fixture
    def init_basic_puzzles(self):
        puz = BuiltinPuzzle(name='empty_puzzle', display_name='Test Puzzle!', puzzle_json='{}', active=True)
        puz.save()
        puz_2 = BuiltinPuzzle(name='empty_puzzle_2', display_name='Test Puzzle 2!', puzzle_json='{"a": "b"}', active=True)
        puz_2.save()
        self.get_url = reverse('get-puzzles')

    @pytest.mark.django_db
    def test_puzzle_create(self):
        prev_count = BuiltinPuzzle.objects.count()
        puz = BuiltinPuzzle(name='new_puzzle', display_name='Test Puzzle!', puzzle_json='{}', active=True)
        puz.save()
        assert BuiltinPuzzle.objects.count() == prev_count + 1

    @pytest.mark.django_db
    def test_puzzle_get(self, init_basic_puzzles):
        data = {'name': 'empty_puzzle'}
        request = self.factory.get(self.get_url, data)
        response = self.view(request)
        content = response.content
        decoded = content.decode('utf-8')
        # content = json.load(response.content)
        assert decoded == '{"name": "empty_puzzle", "display_name": "Test Puzzle!", "active": true}'





