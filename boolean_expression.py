from quine_mccluskey import QuineMcCluskeyChart
from itertools import product
from collections import Counter
import re

class Boolean:
    def __init__(self, val, varSet):
        self._minTermExp = ''
        self._simpleExp = ''
        self._maxTermExp = ''
        self._minTerm = set()
        self._maxTerm = set()
        self._varSet = set()

        if type(varSet) is not set:
            raise TypeError("Invalid argument type")
        if type(val) is str:
            val = val.replace(' ', '')
            self._varSet = varSet
            self._parseExp(val)
            self._maxTerm = Boolean._getMaxTerm(self._varSet, self._minTerm)
        elif type(val) is set:
            self._minTerm = val
            self._varSet = varSet
            self._maxTerm = Boolean._getMaxTerm(self._varSet, self._minTerm)
        else:
            raise TypeError("Invalid argument type")

    def getMinTerm(self):
        return self._minTerm

    def getMaxTerm(self):
        return self._maxTerm

    def getMinTermExp(self):
        if self._minTermExp is '':
            self._minTermExp = None

        return self._minTermExp
    
    def getSimpleExp(self):
        if self._simpleExp is '':
           pass 

    def getVarSet(self):
        return self._varSet

    def _generateExpressions(self):
        varList = sorted(list(self._varSet))

        binMinTerm = Boolean._itob(self._minTerm, len(self._varSet))
        self._minTermExp = ''
        for term in binMinTerm:
            for i in range(0, len(term)):
                self._minTermExp += varList[i]
                if term[i] is '0':
                    self._minTermExp += '\''

        simpTerm = QuineMcCluskeyChart(binMinTerm).getMinTerm()
        print(self._minTerm)
        print(simpTerm)

    def _parseExp(self, exp):
        postfix = self._buildPostfix(exp)[0]
        temp = Boolean._processPostfix(postfix)
        
        self._minTerm = Boolean._maskTermToVarSet(temp._minTerm, temp._varSet, self._varSet)

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
        bExp = Boolean(set(), self._varSet)

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

            newSelfMinTerm = Boolean._maskTermToVarSet(self._minTerm, self._varSet, union)
            newExpMinTerm = Boolean._maskTermToVarSet(exp._minTerm, exp._varSet, union)

            newMinTerm = newSelfMinTerm | newExpMinTerm

            return (newMinTerm, union)
        else:
            message = "unsupported operand type(s) for +: "
            message += type(self).__name__ + " and " + type(exp).__name__
            raise TypeError(message)

    def _doMult(self, exp):
        if type(exp) is Boolean:
            union = self._varSet | exp._varSet

            newSelfMinTerm = Boolean._maskTermToVarSet(self._minTerm, self._varSet, union)
            newExpMinTerm = Boolean._maskTermToVarSet(exp._minTerm, exp._varSet, union)

            newMinTerm = newSelfMinTerm & newExpMinTerm
            
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
        self._minTerm = vals[0]
        self._varSet = vals[1]
        return self

    def __mul__(self, exp):
        vals = self._doMult(exp)
        return Boolean(vals[0], vals[1])

    def __rmul__(self, exp):
        return self + exp

    def __imul_(self, exp):
        vals = self._doMult(exp)
        self._minTerm = vals[0]
        self._varSet = vals[1]
        return self

    def __invert__(self):
        superSet = Boolean._getTermSuperSet(len(self._varSet))

        return Boolean(superSet - self._minTerm, self._varSet)

    def __eq__(self, val):
        return self._minTerm == val._minTerm and self._varSet == val._varSet

    def __repr__(self):
        return (self._minTerm, self._varSet).__str__()

    def __str__(self):
        return (self._minTerm, self._varSet).__str__()

    @staticmethod
    def _getMaxTerm(varSet, minTerm):
        superset = Boolean._getTermSuperSet(len(varSet))
        return superset - minTerm

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
    def _maskTermToVarSet(minTerm, oldSet, newSet):
        binMinTerm = Boolean._itob(minTerm, len(oldSet))

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
