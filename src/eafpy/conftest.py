import pytest
import eafpy


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace["eaf"] = eafpy
