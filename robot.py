class Variable:
    def __init__(self, name, addr, scope):
        self.name = name
        self.address = addr
        self.scope = scope
    
    def __repr__(self):
        return "<" + self.name + "|" + self.scope + " at " + str(self.address) + ">"

class Robot:
    def __init__(self):
        self.bytecode = []
        self.memcode = []
        self.vartable = {}

    def vardec(self, stack, scope):
        name = stack[0]
        val = stack[2]
        
        self.vartable[name.value] = Variable(name.value, len(self.vartable), scope)
        
        self.memcode.append(val)
    
    def output(self):
        return self.bytecode + [0xF000_0000, 0xFF000000] + self.memcode