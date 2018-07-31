
# coding: utf-8

# # π$^2$: π Framework in Python
# 
# The π Framework is a simple framework for compiler construction. It defines a set of common programming languages primitives (π Lib) and their formal semantics (π Automata). In this notebook π is formally described. The syntax of π Lib is given as a BNF description. The π Automata for the dynamic semantics of π Lib is described in Maude syntax. We implement the π Framework in Python to start exploring notebook features together with different libraries available for the Python language such as ``llvm`` and ``SMV`` bindings.
# 
# ## π Lib Expressions

# ### Grammar for π Lib Expressions
# $\begin{array}{rcl}
# Statement & ::= & Exp \\
# Exp       & ::= & ArithExp \mid BoolExp \\
# ArithExp  & ::= & Sum(Exp, Exp) \mid Sub(Exp, Exp) \mid Mul(Exp, Exp) \\
# BoolExp.  & ::= & Eq(Exp, Exp) \mid Not(Exp)
# \end{array}$

# ### π Lib Expressions in Python
# 
# We encode BNF rules as classes in Python. Every non-terminal gives rise to a class. The reduction relation $::=$ is encoded as inheritance. Operands are encoded as cells in a list object attribute, whose types are enforced by `assert` predicates on `isinstace` calls. The operand list `opr` is declared in the `Statement` class, whose constructor initializes the `opr` attribute with as many parameters as the subclass constructor might have.

# In[2]:


# π Lib
## Statement
class Statement: 
    def __init__(self, *args):
        self.opr = args
    def __str__(self):
        ret = str(self.__class__.__name__)+"("
        for o in self.opr:
            ret += str(o)
        ret += ")"
        return ret

## Expressions
class Exp(Statement): pass
class ArithExp(Exp): pass
class Num(ArithExp): 
    def __init__(self, f): 
        assert(isinstance(f, float))
        super().__init__(f)
class Sum(ArithExp): 
    def __init__(self, e1, e2): 
        assert(isinstance(e1, Exp) and isinstance(e2, Exp))
        super().__init__(e1, e2)
class Sub(ArithExp): 
    def __init__(self, e1, e2): 
        assert(isinstance(e1, Exp) and isinstance(e2, Exp))
        super().__init__(e1, e2)
class Mul(ArithExp): 
    def __init__(self, e1, e2): 
        assert(isinstance(e1, Exp) and isinstance(e2, Exp))
        super().__init__(e1, e2)
class BoolExp(Exp): pass
class Eq(BoolExp):
    def __init__(self, e1, e2):
        assert(isinstance(e1, Exp) and isinstance(e2, Exp))
        super().__init__(e1, e2)
class Not(BoolExp):
    def __init__(self, e):
        assert(isinstance(e, Exp))
        super().__init__(e)


# In[3]:


exp = Sum(Num(1.0), Mul(Num(2.0), Num(4.0)))
type(exp)
print(exp)


# However, if we create an ill-formed tree, an exception is raised.
# 
# ```python
# exp2 = Mul(2.0, 1.0)
# 
# ---------------------------------------------------------------------------
# AssertionError                            Traceback (most recent call last)
# <ipython-input-3-de6e358a117c> in <module>()
# ----> 1 exp2 = Mul(2.0, 1.0)
# 
# <ipython-input-1-09d2d91ef407> in __init__(self, e1, e2)
#      28 class Mul(ArithExp):
#      29     def __init__(self, e1, e2):
# ---> 30         assert(isinstance(e1, Exp) and isinstance(e2, Exp))
#      31         super().__init__(e1, e2)
#      32 class BoolExp(Exp): pass
# 
# AssertionError: 
# ```

# ### π Automaton for π Lib Expressions

# The π automaton for π Lib Expressions is implemented in the `ExpπAut` class. Instances of `ExpπAut` are dictionaries, that come initialized with two entries: one for the value stack, at index `val`, and antother for the control stack, indexed `cnt`.
# ```python
# class ExpπAut(dict):
#     def __init__(self):    
#         self["val"] = ValueStack()
#         self["cnt"] = ControlStack()
# # ...
# ```

# Class `ExpπAut` encapsulates the encoding for π Lib Expression rules as private methods that are called by the public (polimorphic) `eval` method. In the following code snippet it calls the function that evaluates a `Sum` expression.
# ```python
# def eval(self):
#     e = self.popCnt()
#     if isinstance(e, Sum):
#         self.__evalSum(e)  
# # ...
# ```

# We use Maude syntax to specify π Automaton rules. This is the π rule for the evaluation of (floating point) numbers, described as an equation in Maude. It specifies that whenever a number is in the top of the control stack `C` is should be popped from `C` and pushed into the value stack `SK`.

# ```maude
# eq [num-exp] : 
#    < cnt : (num(f:Float) C:ControlStack), val : SK:ValueStack, ... > 
#  = 
#    < cnt : C:ControlStack, 
#      val : (val(f:Float) SK:ValueStack), ... > .```

# π rule `num-exp` is encoded in function `__evalNum(self, n)`. It receives a `Num` object in `n` whose sole attribute has the floating point number that `n` denotes. Method `pushVal(.)` pushes the given argument into the value stack.  
# ```python
# def __evalNum(self, n):
#     f = n.opr[0]
#     self.pushVal(f)
# ```

# ### The complete π Automaton for π Lib Expressions in Python

# In[4]:


## Expressions
class ValueStack(list): pass
class ControlStack(list): pass
class ExpKW:
    SUM = "#SUM"
    SUB = "#SUB"
    MUL = "#MUL"
    EQ = "#EQ"
    NOT = "#NOT"
class ExpπAut(dict):
    def __init__(self):    
        self["val"] = ValueStack()
        self["cnt"] = ControlStack()
    def val(self):
        return self["val"]
    def cnt(self):
        return self["cnt"]
    def pushVal(self, v):
        vs = self.val() 
        vs.append(v)
    def popVal(self):
        vs = self.val()
        v = vs[len(vs) - 1]
        vs.pop()
        return v
    def pushCnt(self, e):
        cnt = self.cnt()
        cnt.append(e)
    def popCnt(self):
        cs = self.cnt()
        c = cs[len(cs) - 1]
        cs.pop()
        return c
    def emptyCnt(self):
        return len(self.cnt()) == 0
    def __evalSum(self, e):
        e1 = e.opr[0]
        e2 = e.opr[1]
        self.pushCnt(ExpKW.SUM)
        self.pushCnt(e1)
        self.pushCnt(e2)
    def __evalSumKW(self, e):
        v1 = self.popVal()
        v2 = self.popVal()
        self.pushVal(v1+v2)
    def __evalMul(self, e):
        e1 = e.opr[0]
        e2 = e.opr[1]
        self.pushCnt(ExpKW.MUL)
        self.pushCnt(e1)
        self.pushCnt(e2)
    def __evalMulKW(self):
        v1 = self.popVal()
        v2 = self.popVal()
        self.pushVal(v1*v2)
    def __evalSub(self, e):
        e1 = e.opr[0]
        e2 = e.opr[1]
        self.pushCnt(ExpKW.SUB)
        self.pushCnt(e1)
        self.pushCnt(e2)
    def __evalSubKW(self):
        v1 = self.popVal()
        v2 = self.popVal()
        self.pushVal(v1-v2)
    def __evalNum(self, n):
        f = n.opr[0]
        self.pushVal(f)
    def __evalEq(self, e):
        e1 = e.opr[0]
        e2 = e.opr[1]
        self.pushCnt(ExpKW.EQ)
        self.pushCnt(e1)
        self.pushCnt(e2)
    def __evalEqKW(self):
        v1 = self.popVal()
        v2 = self.popVal()
        self.pushVal(v1 == v2) 
    def __evalNot(self, e):
        e = e.opr[0]
        self.pushCnt(ExpKW.NOT)
        self.pushCnt(e)
    def __evalNotKW(self):
        v = self.popVal()
        self.pushVal(not v) 
    def eval(self):
        e = self.popCnt()
        if isinstance(e, Sum):
            self.__evalSum(e)  
        elif e == ExpKW.SUM:
            self.__evalSumKW(e)  
        elif isinstance(e, Sub):
            self.__evalSub(e)
        elif e == ExpKW.SUB:
            self.__evalSubKW()
        elif isinstance(e, Mul):
            self.__evalMul(e)
        elif e == ExpKW.MUL:
            self.__evalMulKW()
        elif isinstance(e, Num):
            self.__evalNum(e)
        elif isinstance(e, Eq):
            self.__evalEq(e)
        elif e == ExpKW.EQ:
            self.__evalEqKW()
        elif isinstance(e, Not):
            self.__evalNot(e)
        elif e == ExpKW.NOT:
            self.__evalNotKW()
        else:
            raise Exception("Ill formed:", e)


# In[5]:


ea = ExpπAut()
print(exp)
ea.pushCnt(exp)
while not ea.emptyCnt():
    ea.eval()
    print(ea)


# ## π Lib Commands
# 
# ### Grammar for π Lib Commands
# 
# $\begin{array}{rcl}
# Statement & ::= & Cmd \\
# Exp       & ::= & Id(String) \\
# Cmd       & ::= & Assign(Id, Exp) \mid Loop(BoolExp, Cmd) \mid CSeq(Cmd, Cmd)
# \end{array}$
# 
# Commands are language constructions that require both an environement and a memory store to be evaluated. 
# From a syntactic standpoint, they extend statements and expressions, as an identifier is an expression.

# ### Grammar for π Lib Commands in Python
# 
# The enconding of the grammar for commands follows the same mapping of BNF rules as classes we used for expressions.

# In[6]:


## Commands
class Cmd(Statement): pass
class Id(Exp):
    def __init__(self, s):
        assert(isinstance(s, str))
        super().__init__(s)
class Assign(Cmd):
    def __init__(self, i, e): 
        assert(isinstance(i, Id) and isinstance(e, Exp))
        super().__init__(i, e)
class Loop(Cmd):
    def __init__(self, be, c):
        assert(isinstance(be, BoolExp) and isinstance(c, Cmd))
        super().__init__(be, c)
class CSeq(Cmd):
    def __init__(self, c1, c2):
        assert(isinstance(c1, Cmd) and isinstance(c2, Cmd))
        super().__init__(c1, c2)


# In[7]:


cmd = Assign(Id("x"), Num(1.0))
print(type(cmd))
print(cmd)


# ### Complete π Automaton for Commands in Python

# In[8]:


## Commands
class Env(dict): pass
class Loc(float): pass
class Sto(dict): pass
class CmdKW:
    ASSIGN = "#ASSIGN"
    LOOP = "#LOOP"
class CmdπAut(ExpπAut): 
    def __init__(self):    
        self["env"] = Env()
        self["sto"] = Sto()
        super().__init__()
    def env(self):
        return self["env"]
    def getLoc(self, i):
        en = self.env()
        return en[i]
    def sto(self):
        return self["sto"]
    def updateStore(self, l, v):
        st = self.sto()
        st[l] = v
    def __evalAssign(self, c): 
        i = c.opr[0]
        e = c.opr[1]
        self.pushVal(i.opr[0])
        self.pushCnt(CmdKW.ASSIGN)
        self.pushCnt(e)
    def __evalAssignKW(self):
        v = self.popVal()
        i = self.popVal()
        l = self.getLoc(i)
        self.updateStore(l, v) 
    def __evalId(self, i):
        s = self.sto()
        l = self.getLoc(i)
        self.pushVal(s[l])
    def __evalLoop(self, c):
        be = c.opr[0]
        bl = c.opr[1]
        self.pushVal(Loop(be, bl))
        self.pushVal(bl)
        self.pushCnt(CmdKW.LOOP)
        self.pushCnt(be)
    def __evalLoopKW(self):
        t = self.popVal()
        if t:
            c = self.popVal()
            lo = self.popVal()
            self.pushCnt(lo)
            self.pushCnt(c)
        else:
            self.popVal()
            self.popVal()
    def __evalCSeq(self, c):
        c1 = c.opr[0]
        c2 = c.opr[1]
        self.pushCnt(c2)
        self.pushCnt(c1)
    def eval(self): 
        c = self.popCnt()
        if isinstance(c, Assign):
            self.__evalAssign(c)
        elif c == CmdKW.ASSIGN:
            self.__evalAssignKW()
        elif isinstance(c, Id):
            self.__evalId(c.opr[0])
        elif isinstance(c, Loop):
            self.__evalLoop(c)
        elif c == CmdKW.LOOP:
            self.__evalLoopKW()
        elif isinstance(c, CSeq):
            self.__evalCSeq(c)
        else:
            self.pushCnt(c)
            super().eval()


# ## π Lib Declarations
# ### Grammar for π Lib Declarations
# 
# $
# \begin{array}{rcl}
# Statement & ::= & Dec \\
# Exp       & ::= & Ref(Exp) \mid Cns(Exp) \\
# Cmd       & ::= & Blk(Dec, Cmd) \\
# Dec       & ::= & Bind(Id, Exp) \mid DSeq(Dec, Dec) 
# \end{array}
# $

# ### Grammar for π Lib Declarations in Python

# In[9]:


## Declarations
class Dec(Statement): pass
class Bind(Dec):
    def __init__(self, i, e):
        assert(isinstance(i, Id) and isinstance(e, Exp))
        super().__init__(i, e)
class Ref(Exp):
    def __init__(self, e):
        assert(isinstance(e, Exp))
        super().__init__(e)
class Cns(Exp):
    def __init__(self, e):
        assert(isinstance(e, Exp))
        super().__init__(e)
class Blk(Cmd):
    def __init__(self, d, c):
        assert(isinstance(d, Dec) and isinstance(c, Cmd))
        super().__init__(d, c)
class DSeq(Dec):
    def __init__(self, d1, d2):
        assert(isinstance(d1, Dec) and isinstance(d2, Dec))
        super().__init__(d1, d2)


# ### Complete π Automaton for π Lib Declarations in Python

# In[10]:


## Declarations
class DecExpKW(ExpKW):
    REF = "#REF"
    CNS = "#CNS"
class DecCmdKW(CmdKW):
    BLKDEC = "#BLKDEC"
    BLKCMD = "#BLKCMD"
class DecKW:
    BIND = "#BIND"
    DSEQ = "#DSEQ"
class DecπAut(CmdπAut):
    def __init__(self):
        self["locs"] = []
        super().__init__()
    def locs(self):
        return self["locs"]
    def pushLoc(self, l):
        ls = self.locs()
        ls.append(l)
    def __evalRef(self, e):
        ex = e.opr[0]
        self.pushCnt(DecExpKW.REF)
        self.pushCnt(ex)
    def __newLoc(self):
        sto = self.sto()
        if sto:
            return max(list(sto.keys())) + 1
        else:
            return 0.0
    def __evalRefKW(self):
        v = self.popVal()
        l = self.__newLoc()
        self.updateStore(l, v)
        self.pushLoc(l)
        self.pushVal(l)
    def __evalBind(self, d): 
        i = d.opr[0]
        e = d.opr[1]
        self.pushVal(i)
        self.pushCnt(DecKW.BIND)
        self.pushCnt(e)
    def __evalBindKW(self):
        l = self.popVal()
        i = self.popVal()
        x = i.opr[0]
        self.pushVal({x:l})
    def __evalDSeq(self, ds):
        d1 = ds.opr[0]
        d2 = ds.opr[1]
        self.pushCnt(DecKW.DSEQ)
        self.pushCnt(d2)
        self.pushCnt(d1)
    def __evalDSeqKW(self):
        d2 = self.popVal()
        d1 = self.popVal()
        d1.update(d2)
        self.pushVal(d1)
    def __evalBlk(self, d):
        ld = d.opr[0]
        c = d.opr[1]
        l = self.locs()
        self.pushVal(l.copy())
        self.pushVal(c)
        self.pushCnt(DecCmdKW.BLKDEC)
        self.pushCnt(ld)
    def __evalBlkDecKW(self):
        d = self.popVal()
        c = self.popVal()
        l = self.locs()
        self.pushVal(l)
        en = self.env()
        ne = en.copy()
        ne.update(d)
        self.pushVal(en)
        self["env"] = ne
        self.pushCnt(DecCmdKW.BLKCMD)
        self.pushCnt(c)
    def __evalBlkCmdKW(self):
        en = self.popVal()
        ls = self.popVal()
        self["env"] = en
        s = self.sto()
        s = {k:v for k,v in s.items() if k not in ls}
        self["sto"] = s
        del ls
        ols = self.popVal()
        self["locs"] = ols
    def eval(self):
        d = self.popCnt()
        if isinstance(d, Bind):
            self.__evalBind(d)
        elif d == DecKW.BIND:
            self.__evalBindKW()
        elif isinstance(d, DSeq):
            self.__evalDSeq(d)
        elif d == DecKW.DSEQ:
            self.__evalDSeqKW()
        elif isinstance(d, Ref):
            self.__evalRef(d)
        elif d == DecExpKW.REF:
            self.__evalRefKW()
        elif isinstance(d, Blk):
            self.__evalBlk(d)
        elif d == DecCmdKW.BLKDEC:
            self.__evalBlkDecKW()
        elif d == DecCmdKW.BLKCMD:
            self.__evalBlkCmdKW()
        else:
            self.pushCnt(d)
            super().eval()


# ### Factorial example

# In[11]:


dc = DecπAut()
fac = Loop(Not(Eq(Id("y"), Num(0.0))), 
        CSeq(Assign(Id("x"), Mul(Id("x"), Id("y"))),
            Assign(Id("y"), Sub(Id("y"), Num(1.0)))))
dec = DSeq(Bind(Id("x"), Ref(Num(1.0))), 
           Bind(Id("y"), Ref(Num(2.0))))
fac_blk = Blk(dec, fac)
dc.pushCnt(fac_blk)
print(dc)
while not dc.emptyCnt():
    dc.eval()
    print(dc)
