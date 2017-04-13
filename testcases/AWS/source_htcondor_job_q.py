class HTCondorJobQ(Source):
    PRODUCES = []

    def __init__ (self, *args, **kwargs):
        self.DataBlock = kwargs["DataBlock"]
        self.desired_attrs = kwargs["desired_attrs"]
        self.constraint = kwargs["constraint"]
        self.schedd_name = kwargs["schedd_name"]

    def produces(self): return PRODUCES

    def acquire(self):
        self.DataBlock.put("stuff")
