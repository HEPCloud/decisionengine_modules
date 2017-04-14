import json
import RE

class LogicEngine:
    def __init__(self, facts, rules):
        self.facts = facts
        # Only the names of facts are really needed. We pass in the
        # JSON form of the whole facts dictionary until the C++ is
        # updated to take a list of strings.
        self.re = RE.RuleEngine(json.dumps(facts), json.dumps(rules))

    def evaluate(self, db):
        """evaluate our facts and rules, in the context of the given data.

        db can be any mappable, in particular a DataBlock or dictionary."""
        # Evaluate facts
        evaluated_facts = { name : eval(expr, {}, db) for name, expr in facts.iteritems()}
        # Process rules
        actions, newfacts = self.re.execute(evaluated_facts)
        db["actions"] = actions
        db["newfacts"] = newfacts

if __name__ == "__main__":
    import copy
    facts = { "a": "True", "b": "z>10" }
    rules = { "r1": { "expression": "a & b", "actions": ["launch_missile", "cook dinner"]} }
    l1 = LogicEngine(facts, rules)

    db = {"z" : 100 }
    old = copy.copy(db)
    l1.evaluate(db)
    new_keys = set(db.keys()) - set(old.keys())
    if (len(new_keys) != 2):
        print "Wrong number of keys added"
    print "New facts: ", db["newfacts"]
    print "Actions: ", db["actions"]
    
              
