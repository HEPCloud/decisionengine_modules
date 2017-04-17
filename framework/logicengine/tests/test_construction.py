from decisionengine.framework.logicengine import LogicEngine
import pytest

def test_default_construction():
    """LogicEngine is not default constructible."""
    with pytest.raises(TypeError):
        engine = LogicEngine.LogicEngine()

def test_wrong_configuration():
    """LogicEngine construction requires rules and facts;
    if we don't supply them it is an error."""
    with pytest.raises(TypeError):
        engine = LogicEngine.LogicEngine({})

def test_simple_configuration():
    """Logic engine constructed with trivial rules and facts."""
    rules = {}
    facts = {}
    le = LogicEngine.LogicEngine(facts, rules)
    assert le.produces() == ["actions", "newfacts"]
