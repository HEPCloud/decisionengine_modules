from random import randint

class LocalCapacity(Source):
    PRODUCES = ["local_capacity_slots"]

    def __init__ (self, params_dict): pass

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        capacity_time_series = [1000, 10000, 200, 5000, 3250, 2345, 4567, 1, 6972, 45]

        DataBlock["local_capacity_slots"] = capacity_time_series[randint(0,9)]
