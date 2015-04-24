from quine_mccluskey import QuineMcCluskeyChart
import re

class BooleanExpression:
    def __init__(self, val, varSet):
        self._expression = ''
        self._minTerm = set()
        self._varSet = set()

        if type(varSet) is not set:
            raise TypeError("Invalid argument type")
        if type(val) is str:
            val = val.replace(' ', '')
            self._expression = val
            self._varSet = varSet
            self._parseExp(val)
        elif type(val) is set:
            self._minTerm = val
            self._varSet = varSet
        else:
            raise TypeError("Invalid argument type")

    def _parseExp(self, exp):
        postfix = self._buildPostfix(exp)[0]
        self._minTerm = BooleanExpression._processPostfix(postfix)._minTerm

    @staticmethod
    def _processPostfix(postfix):
        del postfix[0]
        stack = []
        
        for val in postfix:
            if isinstance(val, list):
                stack.append(BooleanExpression._processPostfix(val))
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
        bExp = BooleanExpression(set(), self._varSet)

        curListIdx = 1
        consecTerms = 0
        while i < len(exp):
            if exp[i] is '(':
                res = self._buildPostfix(exp, i+1, varIdx+1)

                if postfix[curListIdx-1] is '\'' or isinstance(postfix[curListIdx-1], list) or isinstance(postfix[curListIdx-1], BooleanExpression):
                    consecTerms += 1

                postfix = postfix[:curListIdx] + [res[0]] + postfix[curListIdx:]
                curListIdx += 1

                i = res[1]
                varIdx = i + 1
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
            elif exp[i] is '*':
                while consecTerms > 0:
                    postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
                    curListIdx += 1
                    consecTerms -= 1

                postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
                varIdx = i + 1
            elif exp[i] is '\'':
                postfix = postfix[:curListIdx] + ['\''] + postfix[curListIdx:]
                curListIdx += 1
                varIdx = i + 1
            elif exp[varIdx:i+1] in self._varSet:
                var = exp[varIdx:i+1]

                if postfix[curListIdx-1] is '\'' or isinstance(postfix[curListIdx-1], list) or isinstance(postfix[curListIdx-1], BooleanExpression):
                    consecTerms += 1

                term = BooleanExpression({1}, {var})
                postfix = postfix[:curListIdx] + [term] + postfix[curListIdx:]

                curListIdx += 1
                varIdx = i + 1
            i += 1

        while consecTerms > 0:
            postfix = postfix[:curListIdx] + ['*'] + postfix[curListIdx:]
            curListIdx += 1
            consecTerms -= 1

        return (postfix, -1)

    def _doAdd(self, exp):
        if type(exp) is BooleanExpression:
            union = self._varSet | exp._varSet

            newSelfMinTerm = BooleanExpression._maskTermToVarSet(self._minTerm, self._varSet, union)
            newExpMinTerm = BooleanExpression._maskTermToVarSet(exp._minTerm, exp._varSet, union)

            newMinTerm = newSelfMinTerm | newExpMinTerm

            return (newMinTerm, union)
        else:
            message = "unsupported operand type(s) for +: "
            message += type(self).__name__ + " and " + type(exp).__name__
            raise TypeError(message)

    def _doMult(self, exp):
        if type(exp) is BooleanExpression:
            union = self._varSet | exp._varSet

            newSelfMinTerm = BooleanExpression._maskTermToVarSet(self._minTerm, self._varSet, union)
            newExpMinTerm = BooleanExpression._maskTermToVarSet(exp._minTerm, exp._varSet, union)

            newMinTerm = newSelfMinTerm & newExpMinTerm
            
            return (newMinTerm, union)
        else:
            message = "unsupported operand type(s) for +: "
            message += type(self).__name__ + " and " + type(exp).__name__
            raise TypeError(message)

    def __add__(self, exp):
        vals = self._doAdd(exp)
        return BooleanExpression(vals[0], vals[1])

    def __radd__(self, exp):
        return self + exp

    def __iadd__(self, exp):
        vals = self._doAdd(exp)
        self._minTerm = vals[0]
        self._varSet = vals[1]
        return self

    def __mul__(self, exp):
        vals = self._doMult(exp)
        return BooleanExpression(vals[0], vals[1])

    def __rmul__(self, exp):
        return self + exp

    def __imul_(self, exp):
        vals = self._doMult(exp)
        self._minTerm = vals[0]
        self._varSet = vals[1]
        return self

    def __invert__(self):
        superSet = BooleanExpression._getTermSuperSet(len(self._varSet))

        return BooleanExpression(superSet - self._minTerm, self._varSet)

    def __repr__(self):
        return (self._minTerm, self._varSet).__str__()

    def __str__(self):
        return (self._minTerm, self._varSet).__str__()

    @staticmethod
    def _getTermSuperSet(numVars):
        superSet = set()
        for i in range(0, 2**numVars):
            superSet.add(i)

        return superSet

    @staticmethod
    def _itob(termSet, size):
        binSet = set()
        for n in termSet:
            binSet.add(('{0:0' + str(size) + 'b}').format(n))

        return binSet

    @staticmethod
    def _btoi(termSet):
        intSet = set()
        for t in termSet:
            intSet.add(int(t, 2))

        return intSet

    @staticmethod
    def _maskTermToVarSet(minTerm, oldSet, newSet):
        binMinTerm = BooleanExpression._itob(minTerm, len(oldSet))

        diff = newSet - oldSet
        diffList = sorted(list(diff))
        newSetList = sorted(list(newSet))
        
        termQueue = []
        for term in binMinTerm:
            for v in diffList:
                i = newSetList.index(v)
                term = term[:i] + '-' + term[i:]
            termQueue.append(term)
        
        newBinMinTerm = BooleanExpression._expandToMinTerm(termQueue)

        return BooleanExpression._btoi(newBinMinTerm)

    @staticmethod
    def _expandToMinTerm(binTermList):
        newMinTerm = set()
        for term in binTermList:
            hasDash = False
            for i in range(0, len(term)):
                if term[i] is '-':
                    hasDash = True
                    binTermList.append(term[:i] + '0' + term[i+1:])
                    binTermList.append(term[:i] + '1' + term[i+1:])
                    break
            if not hasDash:
                newMinTerm.add(term)

        return newMinTerm
