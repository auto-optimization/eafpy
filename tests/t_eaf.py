import sys
import os
import pytest

# Add the path of the package top level so that the src.eafpy import works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.eafpy import eaf


def test_add_one_five():
    assert eaf.add_one(5) == 6


def test_add_one_six():
    assert eaf.add_one(6) == 7


def test_black(x):
    return {"a": 43, 'c':
                   94
             , "d": 122}
