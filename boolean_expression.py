from quine_mccluskey import QuineMcCluskeyChart
from itertools import product
from collections import Counter
import re


class Boolean:
    def __init__(self, varSet, expr=None, minterm=None, dont_care=None):
        # Only want at most one of these defined
        if expr != None and minterm != None:
            raise ValueError("At most one of [expr, minterm] may be defined")

        
        self._minterm_exp = ''
        self._simple_exp = ''
        self._maxterm_exp = ''
        self._minterm = set()
        self._maxterm = set()
        self._varSet = set()

        if type(varSet) is not set:
            raise TypeError("Invalid argument type")

        if expr is not None:
            expr = expr.replace(' ', '')
            self._varSet = varSet
            self._parse_expr(expr)
            self._maxterm = Boolean._getMaxTerm(self._varSet, self._minterm)
        elif minterm is not None:
            self._minterm = minterm
            self._varSet = varSet
            self._maxterm = Boolean._getMaxTerm(self._varSet, self._minterm)

        if dont_care is not None:
            self._dont_care = dont_care
        else:
            self._dont_care = set()

        if len(self._dont_care & self._minterm) > 0:
            raise ValueError("dont_care and minterm sets must be disjoint")


    def getMinTerm(self):
        return self._minterm

    def getMaxTerm(self):
        return self._maxterm

    def getMinTerm_exp(self):
        if self._minterm_exp is '':
            self._minterm_exp = None

        return self._minterm_exp
    
    def getSimple_exp(self):
        if self._simple_exp is '':
           pass 

    def getVarSet(self):
        return self._varSet

    def _generate_expressions(self):
        varList = sorted(list(self._varSet))

        binMinTerm = Boolean._itob(self._minterm | self._dont_care, len(self._varSet))
        self._minterm_exp = ''
        for term in binMinTerm:
            for i in range(0, len(term)):
                self._minterm_exp += varList[i]
                if term[i] is '0':
                    self._minterm_exp += '\''

        simpTerm = QuineMcCluskeyChart(binMinTerm).getMinTerm()
        print(self._minterm)
        print(simpTerm)

    def _parse_expr(self, exp):
        postfix = self._buildPostfix(exp)[0]
        temp = Boolean._processPostfix(postfix)
        
        self._minterm = Boolean._maskTermToVarSet(temp._minterm, temp._varSet, self._varSet)

    @staticmethod
    def _processPostfix(postfix):
        del postfix[0]
        stack = []
        
        for val in postfix:
            if isinstance(val, list):
                stack.append(Boolean._processPostfix(val))
            elif val is '+':
                stack.append(stack.pop() + stack.pop())
            elif val is '*':
                stack.append(stack.pop() * stack.pop())
            elif val is '\'':
                stack.append(~stack.pop())
            else:
                stack.append(val)

        return stack.pop()

    def _buildPostfix(self, exp, i=0, varIdx=0):
        postfix = [None]
        b_exp = Boolean(set(), self._varSet)

        prevVal = None
        curListIdx = 1
        consecTerms = 0
        while i < len(exp):
            if exp[i] is '(':
                res = self._buildPostfix(exp, i+1, varIdx+1)

                if isinstance(prevVal, list) or isinstance(prevVal, Boolean):
                    consecTerms += 1

                postfix = postfix[:curListIdx] + [res[0]] + postfix[curListIdx:]
                curListIdx += 1

                i = res[1]
                varIdx = i + 1
                prevVal = res[0]
            elif exp[i] is ')':
                while consecTerms > 0:
                    postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
                    curListIdx += 1
                    consecTerms -= 1

                return (postfix, i)
            elif exp[i] is '+':
                while consecTerms > 0:
                    postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
                    curListIdx += 1
                    consecTerms -= 1

                postfix = postfix[:curListIdx] + ['+'] + postfix[curListIdx:]
                varIdx = i + 1
                prevVal = None
            elif exp[i] is '*':
                while consecTerms > 0:
                    postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
                    curListIdx += 1
                    consecTerms -= 1

                postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
                varIdx = i + 1
                prevVal = None
            elif exp[i] is '\'':
                postfix = postfix[:curListIdx] + ['\''] + postfix[curListIdx:]
                curListIdx += 1
                varIdx = i + 1
            elif exp[varIdx:i+1] in self._varSet:
                var = exp[varIdx:i+1]

                if isinstance(prevVal, list) or isinstance(prevVal, Boolean):
                    consecTerms += 1

                term = Boolean({1}, {var})
                postfix = postfix[:curListIdx] + [term] + postfix[curListIdx:]

                curListIdx += 1
                varIdx = i + 1
                prevVal = term
            i += 1

        while consecTerms > 0:
            postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
            curListIdx += 1
            consecTerms -= 1

        return (postfix, -1)

    def _doAdd(self, exp):
        if type(exp) is Boolean:
            union = self._varSet | exp._varSet

            newSelfMinTerm = Boolean._maskTermToVarSet(self._minterm, self._varSet, union)
            new_expMinTerm = Boolean._maskTermToVarSet(exp._minterm, exp._varSet, union)

            newMinTerm = newSelfMinTerm | new_expMinTerm

            return (newMinTerm, union)
        else:
            message = "unsupported operand type(s) for +: "
            message += type(self).__name__ + " and " + type(exp).__name__
            raise TypeError(message)

    def _doMult(self, exp):
        if type(exp) is Boolean:
            union = self._varSet | exp._varSet

            newSelfMinTerm = Boolean._maskTermToVarSet(self._minterm, self._varSet, union)
            new_expMinTerm = Boolean._maskTermToVarSet(exp._minterm, exp._varSet, union)

            newMinTerm = newSelfMinTerm & new_expMinTerm
            
            return (newMinTerm, union)
        else:
            message = "unsupported operand type(s) for +: "
            message += type(self).__name__ + " and " + type(exp).__name__
            raise TypeError(message)

    def __add__(self, exp):
        vals = self._doAdd(exp)
        return Boolean(vals[0], vals[1])

    def __radd__(self, exp):
        return self + exp

    def __iadd__(self, exp):
        vals = self._doAdd(exp)
        self._minterm = vals[0]
        self._varSet = vals[1]
        return self

    def __mul__(self, exp):
        vals = self._doMult(exp)
        return Boolean(vals[0], vals[1])

    def __rmul__(self, exp):
        return self + exp

    def __imul_(self, exp):
        vals = self._doMult(exp)
        self._minterm = vals[0]
        self._varSet = vals[1]
        return self

    def __invert__(self):
        superSet = Boolean._getTermSuperSet(len(self._varSet))

        return Boolean(superSet - self._minterm, self._varSet)

    def __eq__(self, val):
        return self._minterm == val._minterm and self._varSet == val._varSet

    def __repr__(self):
        return (self._minterm, self._dont_care, self._varSet).__str__()

    def __str__(self):
        return (self._minterm, self._dont_care, self._varSet).__str__()

    @staticmethod
    def _getMaxTerm(varSet, minterm):
        superset = Boolean._getTermSuperSet(len(varSet))
        return superset - minterm

    @staticmethod
    def _getTermSuperSet(numVars):
        return set(range(2**numVars))

    @staticmethod
    def _itob(termSet, size):
        return {(size - len(b))*'0' + b for b in map(lambda n: bin(n)[2:], termSet)}

    @staticmethod
    def _btoi(termSet):
        return {int(t, 2) for t in termSet}

    @staticmethod
    def _maskTermToVarSet(minterm, oldSet, newSet):
        binMinTerm = Boolean._itob(minterm, len(oldSet))

        diff = newSet - oldSet
        diffList = sorted(diff)
        newSetList = sorted(newSet)
        
        termQueue = []
        for term in binMinTerm:
            for v in diffList:
                i = newSetList.index(v)
                term = term[:i] + '-' + term[i:]
            termQueue.append(term)
        
        newBinMinTerm = map(lambda t: "".join(t), Boolean._expandToMinTerm(termQueue))

        return Boolean._btoi(newBinMinTerm)

    @staticmethod
    def _expandToMinTerm(binTermList):
        return {b for arr in map(lambda b: Boolean._expandTerm(b), binTermList) for b in arr}

    @staticmethod
    def _expandTerm(binTerm):
        c = Counter(binTerm)['-']
        perm = map(lambda p: iter(p), product('01', repeat=c))
        res = map(lambda p: map(lambda c: next(p) if c == '-' else c, binTerm), perm)
        return res
