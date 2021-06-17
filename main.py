from enum import Enum
import re

class Symbol:
    def __init__(self, v, raw=False):
        self.value = v
        self.is_raw = raw
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.value == other.value and self.is_raw == other.is_raw

IDENT = 0
ENDL = 1
EQ = 2
LET = 3
ANY = 4
PROC = 5
COLON = 6
LCB = 7
RCB = 8
LP = 9
RP = 10
PLUS = 11
MINUS = 12
MULT = 13
DIV = 14
symdict = {LET:"let", IDENT:"?", ENDL:";", EQ:"=", ANY:"A", PROC:"fn", COLON:":", LCB:"{", RCB:"}", LP:"(", RP:")", PLUS:"+", MINUS:"-", MULT:"*", DIV:"/"}
inv_symdict = {v:k for k, v in symdict.items()}

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
        #print("\nBlock ", self.bc)
        
        if self.accept(LET):
            self.stack.clear()
            self.expect(ANY)
            if self.accept(EQ):
                self.expect(ANY)
                self.expect(ENDL)
                self.robot.vardec(self.stack)
                self.stack.clear()
            else:
                self.expect(ENDL)
            #self.block()
        while self.accept(PROC):
            print("[Start] Proccess")
            #if self.fn_flag == False:
                #self.fn_flag = True
            self.expect(ANY)
            self.expect(LP)
            self.expect(RP)
            self.expect(LCB)
            
            self.block()
            self.expect(RCB)
            print("[End] Proccess")
            #else:
                #self.error("Cannot declare function within function.")
        #if self.fn_flag:
            
            #self.expect(RCB)
            #self.fn_flag = False
        #else:
            #pass    
        self.statement()
            #else:
                #self.error("Cannot declare function within function.")
        
        
    
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
            self.error("Syntax Error -> " + str(self.sym()))
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
        self.block()

class Robot:
    def __init__(self):
        self.bytecode = []
        self.memcode = []
        self.vartable = {}

    def vardec(self, stack):
        name = stack[0]
        val = stack[2]
        
        self.vartable[name.value] = 0
        
        self.memcode.append(val)
    
    def output(self):
        return self.bytecode + [0xFF000000] + self.memcode


def main():
    p = Program()
    p.load_symbols("test.vn")
    p.parse()
    print(p.robot.output())


if __name__ == '__main__':
    main()