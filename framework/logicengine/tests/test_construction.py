from decisionengine.framework.logicengine import LogicEngine
import pytest

def test_default_construction():
    """LogicEngine is not default constructible."""
    with pytest.raises(TypeError):
        engine = LogicEngine()

def test_wrong_configuration():
    """LogicEngine construction requires rules and facts."""
    with pytest.raises(TypeError):
        engine = LogicEngine({})
