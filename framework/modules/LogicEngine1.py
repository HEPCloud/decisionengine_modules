from modules import Module

class LogicEngine1(Module.Module):
    def __init__(self,set_of_parameters, my_data_block):
        Module.Module.__init__(self,set_of_parameters, my_data_block)

    def evaluate(self):
        print "Called LogicEngine1.evaluate"
        return True
