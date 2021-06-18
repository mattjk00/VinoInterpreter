from enum import Enum
import re
from robot import Robot
from symbol import *


def symbol_string():
    s = ""
    ss = list(symdict.values())
    for i in range(len(ss)):
        if ss[i] == "{" or ss[i] == "}" or ss[i] == "(" or ss[i] == ")":
            s += "\\"
        if i < len(ss) - 1:
            s += ss[i] + "|"
        else:
            s += ss[i]
    print(s)
    return s

class Program:
    def __init__(self):
        self.symbols = [PROC, "main", LP, RP, LCB, LET, "a", EQ, "0", ENDL, RCB]
        self.sindex = 0
        self.robot = Robot()
        self.stack = []
        self.done = False
        self.bc = 0
        self.fn_flag = False
        self.scope = ['module']
    
    def accept_ident(self): 
        t = self.sym().value in self.robot.vartable  
        if t:
            print(self.sym())
            self.nextsym()
        return t
    
    def accept_num(self):
        if self.sym().is_raw == False:
            return False
        t = self.sym().value
        try:
            num = int(t)
            print(num)
            self.nextsym()
            return True
        except ValueError:
            return False

    def load_symbols(self, filename):
        f = open(filename)
        s = f.read()
        s = " ".join(s.split())
        syms = re.split(r"(\blet\b|;|=|\)|\(|\{|fn|\+|-|/|\*)", s)
        syms = list(filter(lambda x:x != "" and x != " ", syms))
        syms = list(map(lambda x: "".join(x.split()), syms))
        syms = list(map(lambda x: Symbol(inv_symdict[x]) if x in inv_symdict else Symbol(x, raw=True), syms))
        print(syms)
        self.symbols = syms

    def sym(self):
        return self.symbols[self.sindex]

    def nextsym(self):
        
        self.sindex += 1
        if self.sindex >= len(self.symbols):
            self.done = True
            self.sindex = len(self.symbols) - 1
            print("Done")
    
    def error(self, msg):
        if not self.done:
            print("Error:\n\t", msg)

    def accept(self, s):

        if self.done:
            return False

        if self.sym().value == s or s == ANY:
            print(self.sym() if s == ANY else symdict[s])
            self.stack.append(self.sym() if s == ANY else symdict[s])
            self.nextsym()
            return True
        return False
    
    def expect(self, s):
        if self.accept(s):
            return True
        self.error("Unexpected Symbol: " + symdict[s]),
        return False

    def block(self):
        self.bc += 1
        print("\nBlock ", self.bc, "- Scope:", self.scope[-1])

        
        self.proc_block()
        if not self.let_block():
            self.statement()

    def let_block(self):    
        if self.accept(LET):
            self.stack.clear()
            self.expect(ANY)
            if self.accept(EQ):
                self.expect(ANY)
                self.expect(ENDL)
                self.robot.vardec(self.stack, self.scope[-1])
                self.stack.clear()
                return True
            else:
                self.expect(ENDL)
                return True
            #self.block()
        return False
    
    def proc_block(self):
        while self.accept(PROC):
            fn_name = self.sym().value
            self.expect(ANY)
            self.expect(LP)
            self.expect(RP)
            self.expect(LCB)

            self.scope.append(fn_name)
            
            while not self.sym().value == RCB:
                self.block()
            
            self.scope.pop()
    
    def statement(self):
        
        if self.accept_ident():
            
            self.expect(EQ)
            self.expression()
            self.expect(ENDL)

            #self.robot.vardec(self.stack)
            #self.stack.clear()
        elif self.accept(ENDL) or self.accept(RCB):
            pass
        else:
            self.error("Statement Syntax Error -> " + str(self.sym()))
            self.nextsym()
    
    def expression(self):
        
        if self.sym().value == PLUS or self.sym().value == MINUS: 
            self.nextsym()
            
        self.term()

        while self.sym().value == PLUS or self.sym().value == MINUS:
            self.nextsym()
            self.term()
    
    def term(self):
        self.factor()
        
        while self.sym().value == MULT or self.sym().value == DIV:
            self.nextsym()
            self.factor()
    
    def factor(self):
        
        if self.accept_ident():
            pass
        elif self.accept_num():
            pass
        elif self.accept(LP):
            
            self.expression()
            self.expect(RP)
        else:
            self.error("Expression Error: " + str(self.sym()))
            self.nextsym()
    
    def parse(self):
        while not self.done:
            self.block()
        print(list(self.robot.vartable.values()))
        




def main():
    p = Program()
    p.load_symbols("test.vn")
    p.parse()
    print(p.robot.output())


if __name__ == '__main__':
    main()