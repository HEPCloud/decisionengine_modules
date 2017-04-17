
class Module:

    def __init__(self,set_of_parameters, my_data_block):
        self.parameters = set_of_parameters
        self.data_block = my_data_block

    def get_paramaters(self):
        return self.parameters

    def get_data_bock(self):
        return self.data_block
        
