import re
from robot import Robot
from symbol import * 

# Generates a Regex String for matching the language tokens
def symbol_string():
    """
    NOT IMPLEMENTED
    """
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
    """ 
    Parses a Vino Language file
    """
    def __init__(self):
        self.symbols = [PROC, "main", LP, RP, LCB, LET, "a", EQ, "0", ENDL, RCB]
        self.sindex = 0             # Symbol Index.
        self.robot = Robot()        # Robot is used for generating bytecode.
        self.stack = []             # Symbol stack. Passed to robot when needed.
        self.done = False           # Done flag is set to true when done parsing.
        self.bc = 0                 # Block Count.
        self.scope = ['module']     # Scope stack. Used to keep track of the scope of code.

    def accept_ident(self) -> bool: 
        """
        Returns true if the current symbol is a registered identifier.
        TODO: Check scope of the identifier
        """
        t = self.sym().value in self.robot.vartable # Check if the current symbol is in the program's variable table
        if t:
            print(self.sym())
            self.nextsym()
        return t
    
    def accept_num(self) -> bool:
        """
        Returns true if the current symbol is a valid number. is_raw flag on symbol must be true for this to return true
        """
        # Check is_raw flag first
        if self.sym().is_raw == False:
            return False
        t = self.sym().value
        # Try converting the symbol's value to a number
        try:
            num = int(t)
            print(num)
            self.nextsym()
            return True
        except ValueError:
            return False

    def load_symbols(self, filename):
        """
        Loads a vino source coude file and then parses out the symbols into a list.
        :param filename: Path of .vn file
        """
        f = open(filename)
        s = f.read()
        s = " ".join(s.split())
        print(s)
        syms = re.split(r"(\bwhile\b|\bif\b|\blet\b|;|\)|\(|\{|}|\bfn\b|\+|-|/|\*|>|<|(?<![!=])[!=]=(?!=)|=)", s)
        syms = list(filter(lambda x:x != "" and x != " ", syms))
        syms = list(map(lambda x: "".join(x.split()), syms))
        syms = list(map(lambda x: Symbol(inv_symdict[x]) if x in inv_symdict else Symbol(x, raw=True), syms))
        print(syms)
        self.symbols = syms

    def sym(self):
        """
        Get the current symbol.
        """
        return self.symbols[self.sindex]

    def nextsym(self, push=True):
        """
        Increments the symbol pointer and checks if the end of the symbol list is reached.
        Set param 'push' to false if the current symbol should not be pushed to the symbol stack.
        """
        if push:
            self.stack.append(self.sym() if self.sym().value == ANY or self.sym().is_raw else symdict[self.sym().value])
        self.sindex += 1
        if self.sindex >= len(self.symbols):
            self.done = True
            self.sindex = len(self.symbols) - 1
            print("Done")
    
    def error(self, msg):
        """
        Display an error message.
        """
        if not self.done:
            print("Error:\n\t", msg)

    def accept(self, s) -> bool:
        """
        Returns true if the current symbol is equivalent to the given symbol s.
        Next sym is called if accepted.
        :param s: The symbol to compare self.sym() to.
        """
        if self.done:
            return False

        if self.sym().value == s or s == ANY:
            print(self.sym() if s == ANY or self.sym().is_raw else symdict[s])
            
            self.nextsym()
            return True
        return False
    
    def expect(self, s):
        """
        Returns true if the current symbol is equivalent to the given symbol s. Error is thrown if there is an unexpected symbol.
        """
        if self.accept(s):
            return True
        self.error("Unexpected Symbol: " + symdict[s]),
        return False

    def block(self):
        """
        Begins parsing a block of code.
        """
        self.bc += 1
        print("\nBlock ", self.bc, "- Scope:", self.scope[-1])

        self.proc_block()
        if not self.let_block(): 
            self.statement()

    def let_block(self):
        """
        Tries parsing a 'let' block. Returns true if a valid let block is parsed.
        e.g. 'let a = 0;'
        """    
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
        """
        Tries to parse a process block. e.g. 'fn a() { return 0; }'
        Will continue to parse sub blocks until a right curly brace is found.
        Keeps track of scope.
        """
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
        """
        Tries to parse a code statement. This includes if statements, variable reassignments, loops, etc.
        """
        # Variable reassignment
        if self.accept_ident():
            
            self.expect(EQ)
            self.expression()
            self.expect(ENDL)

            self.robot.varassign(self.stack)
            self.stack.clear()
        # If statement
        elif self.accept(IF):
            self.condition()
            self.expect(LCB)

            self.robot.ifstatement(self.stack)
            self.stack.clear()

            self.block()
            
            self.expect(RCB)

            self.robot.jump_here()    
        elif self.accept(WHILE):
            self.condition()
            self.expect(LCB)

            self.robot.while_loop(self.stack)
            self.stack.clear()

            self.block()

            self.expect(RCB)    
            self.robot.end_while() 
            
        elif self.accept(ENDL) or self.accept(RCB):
            pass
        else:
            self.error("Statement Syntax Error -> " + str(self.sym()))
            self.nextsym(push=False)
    
    def condition(self, call_expression=True):
        """
        Tries to parse a conditional statement
        param: call_expression - Set to false if you do not want this condition call to also call expression before parsing.
        """
        if call_expression == True:
            self.expression()
        s = self.sym().value
        if s == EQUAL or s == GTHAN or s == LTHAN:
            self.nextsym(push=s)
            self.expression()
        else:
            if call_expression == False or s == LCB or s == ENDL:
                return
            self.error("Invalid Operator in Conditional Statement.")
            self.nextsym(push=False)
    
    def expression(self):
        """
        Tries to parse an expression. e.g. 5 + 2
        """
        if self.sym().value == PLUS or self.sym().value == MINUS: 
            self.nextsym()

        self.term()

        while self.sym().value == PLUS or self.sym().value == MINUS:
            self.nextsym()
            self.term()

        # Check to see if the expression is actually a conditional statement.
        self.condition(call_expression=False)
    
    def term(self):
        """
        Tries to parse a term for an expression.
        """
        self.factor()
        
        while self.sym().value == MULT or self.sym().value == DIV:
            self.nextsym()
            self.factor()
    
    def factor(self):
        
        """
        Tries to parse a factor for an expression.
        """
        if self.accept_ident():
            pass
        elif self.accept_num():
            pass
        elif self.accept(LP):
            
            self.expression()
            self.expect(RP)
        else:
            self.error("Expression Error: " + str(self.sym()))
            self.nextsym(push=False)
    
    def scope_block(self):
        """
        NOT IMPLEMENTED
        """
        if self.accept(RCB):
            self.scope.append("some")
            self.block()
            self.expect(LCB)
            return True
        return False
    
    def parse(self):
        """
        Begins the parsing process
        """
        while not self.done:
            self.block()
        print(list(self.robot.vartable.values()))
        
def main():
    import sys
    p = Program()

    n = len(sys.argv)
    out = "test.vino"
    if n > 1:
        p.load_symbols(sys.argv[1])
        out = sys.argv[1].split('.')[0] + ".vino"
    else:
        p.load_symbols("test.vn")
    
    
    p.parse()
    print(list(map(lambda x: hex(x), p.robot.output())))
    bytes = p.robot.output_as_bytes()
    print(list(map(lambda x: hex(x), bytes)))
    p.robot.write_to_file(out, bytes)

    #exp = ['3', '+', '4', '*', '2', '/', '(', '1', '-', '5', ')', '^', '2', '^', '3']
    #exp = ['5', '+', '2','*','(','3','-','4',')']
    #print(exp)
    #p.robot.order_expression(exp)


if __name__ == '__main__':
    main()