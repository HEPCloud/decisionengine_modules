from LogicEngine import LogicEngine
import pytest

def test_default_construction():
    with pytest.raises(TypeError):
        engine = LogicEngine()
