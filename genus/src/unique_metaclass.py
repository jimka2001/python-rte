from simple_type_d import SimpleTypeD 

#this should never reach master, but I like it in trial_and_error
class Unique(SimpleTypeD):

    def __call__(cls, *args, **kwargs):
        if cls._cache:
            self = cls.__new__(cls, *args, **kwargs)
            cls.__init__(self, *args, **kwargs)
            cls._cache[args[0]] = self
        return cls._cache[args[0]]

    def __init__(cls):
        super().__init__()
        cls._cache = {}

    def typep(self, any):
        raise NotImplementedError