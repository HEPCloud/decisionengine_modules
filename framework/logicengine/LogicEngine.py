from decisionengine.framework.logicengine.RE import RuleEngine
from decisionengine.framework.logicengine.NamedFact import NamedFact
from decisionengine.framework.modules.Module import Module
import json

class LogicEngine(Module, object):
    # Inheritance from object can be dropped if Module is modified to
    # inherit from object.
    def __init__(self, cfg):
        # TODO: remove the second argument to the Module c'tor when
        # the Module base class is updated.
        super(LogicEngine, self).__init__(cfg, None)
        self.facts = [ NamedFact(name, expr) for name, expr in cfg["facts"] ]
        # Only the names of facts are really needed. We pass in the
        # JSON form of the whole facts dictionary until the C++ is
        # updated to take a list of strings.
        self.re = RuleEngine(json.dumps(cfg["facts"]),
                             json.dumps(cfg["rules"]))

    def produces(self):
        return ["actions", "newfacts"]

    def evaluate(self, db):
        """evaluate our facts and rules, in the context of the given data.

        db can be any mappable, in particular a DataBlock or dictionary."""
        # Evaluate facts
        evaluated_facts = { fact.name : fact.evalute(db) for fact in facts }
        # Process rules
        actions, newfacts = self.re.execute(evaluated_facts)
        return {"actions": actions, "newfacts": newfacts}

if __name__ == "__main__":
    import copy
    facts = { "a": "True",
              "b": "z>10",
              "c": "match_table[still_good == True]).assign(req_cost=number_to_request * burn_rate)['req_cost'].sum() > 0"
            }
    rules = { "r1": { "expression": "a && b && c", "actions": ["launch_missile", "cook dinner"]} }
    l1 = LogicEngine(facts, rules)

    db = {"z" : 100 }
    old = copy.copy(db)
    l1.evaluate(db)
    new_keys = set(db.keys()) - set(old.keys())
    if (len(new_keys) != 2):
        print "Wrong number of keys added"
    print "New facts: ", db["newfacts"]
    print "Actions: ", db["actions"]
    
              
