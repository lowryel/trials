from django.test import TestCase
from .views import index

# Create your tests here.
import pytest



class TestIndexTest:
    def index_test(self):

        assert index()

