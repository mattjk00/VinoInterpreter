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

        self.operands = ['+', '-', '*', '/', '^']

    def vardec(self, stack, scope):
        name = stack[0]
        val = stack[2]
        
        self.vartable[name.value] = Variable(name.value, len(self.vartable), scope)
        
        self.memcode.append(val)

    def varassign(self, stack):
        name = stack[0]
        print(stack)        

    def order_expression(self, ex):
        """
        Converts an expression sequence into Reverse Polish Notation for easier conversion to bytecode.
        Using the Shunting-yard algorithm
        """
        stack = []
        output = []
        i = 0
        while i < len(ex):
            token = ex[i]
            if not token in self.operands and token != '(' and token != ')':
                output.append(token)
            elif token in self.operands :
                if len(stack) > 0:
                    o2 = stack[-1]
                    while o2 != '(' and (prec(token) <= prec(o2) and token != '^'):
                        if len(stack) > 0:
                            op = stack.pop()
                            output.append(op)
                            o2 = -1 if len(stack) == 0 else stack[-1]
                        else:
                            break

                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                o2 = stack[-1]
                while o2 != '(':
                    op = stack.pop()
                    output.append(op)
                    o2 = stack[-1]
                stack.pop()
            i += 1 
        while len(stack) > 0:
            op = stack.pop()
            output.append(op)
        return output


    def output(self):
        return self.bytecode + [0xF000_0000, 0xFF000000] + self.memcode

def prec(token):
        if token == '^':
            return 4
        elif token == '*' or token == '/':
            return 3
        elif token == '+' or token == '-':
            return 2
        else:
            return -1