from decisionengine.framework.logicengine.LogicEngine import LogicEngine
import pytest

def test_default_construction():
    """LogicEngine is not default constructible."""
    with pytest.raises(TypeError):
        engine = LogicEngine()

def test_wrong_configuration():
    """LogicEngine construction requires rules and facts;
    if we don't supply them it is an error."""
    with pytest.raises(KeyError):
        engine = LogicEngine({})

def test_simple_configuration():
    """Logic engine constructed with trivial rules and facts."""
    cfg = { "rules": {}, "facts": {} }
    le = LogicEngine(cfg)
    assert le.produces() == ["actions", "newfacts"]
