import pytest
from src.joborchrrestrator.handler.handlers import SomeHandler

def test_some_handler_method():
    handler = SomeHandler()
    result = handler.some_method()
    assert result == "expected_result"
