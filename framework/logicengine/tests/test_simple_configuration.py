from decisionengine.framework.logicengine.LogicEngine import LogicEngine
import pytest

def test_simple_configuration():
    facts = { "f1" : "val > 10" }
    rules = { "r1": {"expression" :"f1", "actions": ["a1", "a2"]} }
    engine = LogicEngine({"facts": facts, "rules": rules})

    db =  {"val": 20} 
    ef = engine.evaluate_facts(db)
    print "Evaluted facts: ", ef
    assert ef["f1"] == True
    actions, newfacts = engine.evaluate(db)
    assert actions == { "r1" : ["a1", "a2"] }
    assert newfacts == { "r1": [] }

    actions, newfacts = engine.evaluate( {"val": 1} )
    assert actions == { "r1" : [] }
    assert newfacts == { "r1" : [] }

