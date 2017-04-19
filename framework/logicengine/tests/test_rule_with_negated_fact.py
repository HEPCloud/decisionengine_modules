from decisionengine.framework.logicengine.LogicEngine import LogicEngine
import pytest

@pytest.fixture
def myengine():
    facts = { "f1" : "val > 10" }
    rules = {}
    rules["r1"] = {"expression" :"!f1", "actions": ["a1"]} 
    rules["r2"] = {"expression" :"!(f1)", "actions": ["a2"]}
    return LogicEngine({"facts": facts, "rules": rules})


def test_rule_that_fires():
    db =  {"val": 5} 
    ef = myengine().evaluate_facts(db)
    assert ef["f1"] == False
    result = myengine().evaluate(db)
    assert type(result) == type({})
    assert len(result) == 2
    actions = result["actions"]
    newfacts = result["newfacts"]
    assert type(actions) == type({})
    assert type(newfacts) == type({})
    assert actions["r1"] ==  ["a1"]
    assert actions["r2"] ==  ["a2"]
    assert len(actions) == 2
    assert newfacts["r1"] == {}
    assert newfacts["r2"] == {}
    assert len(newfacts) == 2


def test_rule_that_does_not_fire():
    """Rules that do not fire do not create entries in the returned
    actions and newfacts.
    """
    db =  {"val": 20}
    ef = myengine().evaluate_facts(db)
    assert ef["f1"] == True
    result = myengine().evaluate(db)
    assert type(result) == type({})
    assert len(result) == 2
    actions = result["actions"]
    newfacts = result["newfacts"]
    assert type(actions) == type({})
    assert type(newfacts) == type({})
    assert len(actions) == 0
    assert newfacts["r1"] == {}
    assert newfacts["r2"] == {}
    assert len(newfacts) == 2

