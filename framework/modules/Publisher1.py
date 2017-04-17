from modules import Module

class Publisher1(Module.Module):
    def __init__(self,set_of_parameters, my_data_block):
        Module.Module.__init__(self,set_of_parameters, my_data_block)

    def consumes(self, name_list): 
        print "Called Publisher1.consumes"

    def publish(self):
        print "Called Publisher1.publish"

