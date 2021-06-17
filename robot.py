class Variable:
    def __init__(self, name, addr, scope):
        self.name = name
        self.address = addr
        self.scope = scope

class Robot:
    def __init__(self):
        self.bytecode = []
        self.memcode = []
        self.vartable = {}

    def vardec(self, stack):
        name = stack[0]
        val = stack[2]
        
        self.vartable[name.value] = Variable(name.value, 0, 0)
        
        self.memcode.append(val)
    
    def output(self):
        return self.bytecode + [0xFF000000] + self.memcode