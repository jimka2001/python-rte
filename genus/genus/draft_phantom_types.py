class foo(object):
    def __init__(self):
        super(foo, self).__init__()
    @staticmethod
    def printkk():
        print("kk")
    def printok():
        print("ok")
    a = 5

class subfoo(foo):
    def __init__(self):
        super(subfoo, self).__init__()

out = foo()
subout = subfoo()
del foo

class foo(object):
    def __init__(self):
        super(foo, self).__init__()
    @staticmethod
    def printkk():
        print("kk")
    def printok():
        print("ok")
    a = 5

print("bs", isinstance(subout, foo))
class haxxfoo(type(out)):
    """def __init__(self):
       pass"""
       #super(haxxfoo, self).__init__()
    def hi():
        print("hi")

"""lolz = haxxfoo() #this causes an error"""

print("subtest", isinstance(subout, type(out)))
print(type(out))
print("test", isinstance(type(out), object))
out.printkk()
#out.printok()
print(out.a)
print(isinstance(out, type(out)))
"""bar = foo() # this causes an error"""
print("type of out:", str(type(out)))
typeout = type(out)
print("tp", typeout)
#jesus = type(out).__init__() (this causes an error)
#bar = foo()
class foo(object):
    def __init__(self):
        super(foo, self).__init__()
    """def printfoo():
        print("hello bug")"""

bar = foo()
print(type(bar) == type(out))
print("same_str?", str(type(bar)) == str(type(out)))
print(isinstance(bar, type(out)))

save_type = type(out)
del out
print(isinstance(subout, save_type))
