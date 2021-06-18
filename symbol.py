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

class Symbol:
    def __init__(self, v, raw=False):
        self.value = v
        self.is_raw = raw
    
    def __str__(self):
        return sym_to_str(self.value)
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.value == other.value and self.is_raw == other.is_raw

def sym_to_str(num):
    if num in symdict:
        return symdict[num]
    else:
        return num