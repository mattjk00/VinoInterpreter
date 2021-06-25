from re import split
from symbol import sym_to_str, Symbol

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

        self.operators = ['+', '-', '*', '/', '^', '<', '>', '==']
        self.jump_flags = []

    def vardec(self, stack, scope):
        name = stack[0]
        val = stack[2]
        
        addr = len(self.vartable)
        self.vartable[name.value] = Variable(name.value, addr, scope)
        
        self.bytecode.append(0x1000_0000 + int(val.value))
        self.bytecode.append(0x2200_0000 + addr)
        

    def varassign(self, stack):
        
        varsym = stack[0]

        var = self.find_variable(varsym.value)
        symexpression = stack[2:]
        if symexpression[-1] == ';':
            symexpression.pop()
        expression = list(map(lambda x: sym_to_str(x), symexpression))
        ordered_exp = self.order_expression(expression)
        print(ordered_exp) 

        self.evaluate_expression(ordered_exp)
        self.bytecode.append(0x2400_0000 + var.address)

    def jump_here(self):
        '''
        Used to keep track of where the program should jump to in case of if statements
        '''
        jump_to_loc = len(self.bytecode)-1
        jump_word_loc = self.jump_flags.pop()
        self.bytecode[jump_word_loc] = self.bytecode[jump_word_loc] + jump_to_loc
    
    def ifstatement(self, stack):
        print("IF: ", stack)
        exp = stack[1:-1]
        print(exp)
        orderedexp = self.order_expression(exp)
        self.evaluate_expression(orderedexp)

        self.bytecode.append(0x3100_0000) # jump zero
        self.jump_flags.append(len(self.bytecode)-1) # keeping track of where to jump to later

        '''split_index = -1
        compare = ''
        for i in range(len(stack)):
            
            if isinstance(stack[i], str) and (stack[i] == '>' or stack[i] == '<' or stack[i] == '=='):
                split_index = i
                compare = stack[i]
                break
        first_exp = stack[1:split_index]
        second_exp = stack[split_index+1:-2]
        
        ofirst = self.order_expression(first_exp)
        self.evaluate_expression(ofirst)
        self.bytecode.append(0x2000_0000) # push first expression
        osecond = self.order_expression(second_exp)
        self.evaluate_expression(osecond)
        
        self.bytecode.append(0x5100_0000) # sub expressions
        
        if compare == '>':
            self.bytecode.append(0x3300_0000)
        elif compare == '<':
            self.bytecode.append(0x3200_0000)
        else:
            self.bytecode.append(0x3100_0000)'''

    def evaluate_expression(self, ex):
        if len(ex) == 0:
            return

        stack = []

        for token in ex:
            if token in self.operators:
                op2 = stack.pop()
                op1 = stack.pop()
                res = self.evaluate_subexp(token, op1, op2)
                stack.append(res)
            else:
                stack.append(token)
        
        self.bytecode.pop()
        return stack.pop()
    
    def evaluate_subexp(self, operator, op1, op2):
        print(op1, operator, op2)
        op2var = self.find_variable(op2)
        if op2var != None:
            self.bytecode.append(0x2300_0000 + op2var.address)
            self.bytecode.append(0x2000_0000)
        elif op2 != 'stack':
            self.bytecode.append(0x1000_0000 + self.to_int(op2))
            self.bytecode.append(0x2000_0000)

        op1var = self.find_variable(op1)
        if op1var != None:
            self.bytecode.append(0x2300_0000 + op1var.address)
        elif op1 != 'stack':
            self.bytecode.append(0x1000_0000 + self.to_int(op1))
        elif op1 == 'stack':
            self.bytecode.append(0x2100_0000)
        
        if operator == '+':
            self.bytecode.append(0x5000_0000)
        elif operator == '*':
            self.bytecode.append(0x5100_0000)
        elif operator == '-':
            self.bytecode.append(0x5200_0000)
        elif operator == '/':
            self.bytecode.append(0x5300_0000)
        elif operator == '==':
            self.bytecode.append(0x5400_0000)
        self.bytecode.append(0x2000_0000)

        return 'stack'
    
    def find_variable(self, name):
        if isinstance(name, Symbol):
            name = name.value
        try:
            var = self.vartable[name]
            return var
        except:
            return None

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
            if not token in self.operators and token != '(' and token != ')':
                output.append(token)
            elif token in self.operators :
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

    def to_int(self, sym):
        if isinstance(sym, Symbol):
            return int(sym.value)
        else:
            return int(sym)

    def output(self):
        return self.bytecode + [0xF000_0000, 0xFF000000] + self.memcode
    
    def output_as_bytes(self):
        o = self.output()
        byteout = []
        for word in o:
            byteout.append( (word>>24) & 0xFF )
            byteout.append( (word>>16) & 0xFF )
            byteout.append( (word>>8) & 0xFF )
            byteout.append( word & 0xFF )
        return byteout
    
    def write_to_file(self, name, bytes):
        f = open(name, 'wb')
        f.write(bytearray(bytes))
        f.close()

def prec(token):
        if token == '^':
            return 4
        elif token == '*' or token == '/':
            return 3
        elif token == '+' or token == '-':
            return 2
        else:
            return -1