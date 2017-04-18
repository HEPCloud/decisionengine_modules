from decisionengine.framework.logicengine.NamedFact import NamedFact
import pytest

def test_simple_fact():
    fact = NamedFact("f1", "z < 100")
    assert fact.evaluate({ "z" : 50 })  == True
    assert fact.evaluate({ "z" : 100 }) == False
    assert fact.evaluate({ "z" : 200 }) == False


def test_compound_fact():
    fact = NamedFact("f2", "z < 100 and a == 4")
    assert fact.evaluate({ "z" : 50, "a" : 4  })  == True
    assert fact.evaluate({ "z" : 100, "a" : 4  }) == False
    assert fact.evaluate({ "z" : 200, "a" : 4 })  == False
    assert fact.evaluate({ "z" : 200, "a" : 5 })  == False
    assert fact.evaluate({ "z" : 100, "a" : 5 })  == False
    assert fact.evaluate({ "z" : 50, "a" : 5 })   == False

# We need to use this helper function to make sure the name np is not
# seen in the context of the use of the facts.
def make_db(maximum):
    import numpy as np
    return  {"vals" : np.arange(maximum) }

def test_fact_using_numpy_array():
    fact = NamedFact("f3", "vals.sum() > 40")
    #fact = NamedFact("f3", "np.sum(vals) > 40")
    assert fact.evaluate(make_db(3)) == False
    assert fact.evaluate(make_db(10)) == True


def test_fact_using_numpy_function():
    NamedFact("f3", "sum(vals) > 40")
    with pytest.raises(NameError):
        fact.evaluate(make_db(3))

def test_no_numpy_found():
    with pytest.raises(NameError):
        dummy = np.arange(10)


