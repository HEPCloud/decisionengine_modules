from decisionengine.framework.modules import Module

class LogicEngine1(Module.Module):
    def __init__(self,set_of_parameters):
        Module.Module.__init__(self,set_of_parameters)

    def evaluate(self):
        print "Called LogicEngine1.evaluate"
        return True
