#!/usr/bin/python3
from labeled_digraph import LabeledDigraph

class BooleanExpression:
    _expression = []
    _minTerm = []
    _varList = []

    def parseExp(self, exp):
        if type(exp) is str:
            exp = exp.split(' ')

        minTerm = []

        term = ""
        for b in exp:
            if b == "+":
                minTerm.append(term)
                term = ""
                continue
            elif b[-1] == "'":
                term += "0"
                b = b[:-1]
            else:
                term += "1"

            if b not in self._varList:
                self._varList.append(b)

        minTerm.append(term)

        self._expression = exp
        self._minTerm = minTerm

    def simplify(self):
        termChart = QuineMcCluskyChart()
        for term in self._minTerm:
            termChart.addTerm(term)

        simTerms = termChart.simplify()
        print(simTerms)
        newExp = ""
        for t in simTerms:
            for i in range(0, len(t)):
                if t[i] is "1":
                    newExp += self._varList[i] + " "
                elif t[i] is "0":
                    newExp += self._varList[i] + "' "

            newExp += "+ "

        self._expression = newExp[:-3]

class QuineMcCluskyChart:
    _maxN = -1
    _groupingMap = {}
    _overlapGraph = LabeledDigraph()

    def addTerm(self, term):
        n = term.count("1")
        if n > self._maxN:
            for i in range(self._maxN + 1, n):
                self._groupingMap[i] = []

            self._maxN = n
            self._groupingMap[n] = [term]
        else:
            self._groupingMap[n].append(term)

        self._overlapGraph.addVertex(Status.NEW, term)

    def removeTerm(self, term):
        n = term.count("1")
        idx = self._groupingMap[n].index(term)
        del self._groupingMap[n][idx]
        self._overlapGraph.removeVertex(term)

    def simplify(self):
        self._simplifyRecurse(False)
        return self._overlapGraph.allVertices()

    def _simplifyRecurse(self, recursion):
        # Add case for empty minterm
        if recursion:
            finished = True
            for t in self._overlapGraph.allVertices():
                if self._overlapGraph.getVertexLabel(t) is Status.NEW:
                    finished = False
                    break
            if finished:
                return

        for k in self._groupingMap.keys():
            for t in self._groupingMap[k]:
                if k + 1 in self._groupingMap.keys():
                    self.findOverlapInGroup(t, k + 1)

                if self._overlapGraph.getVertexLabel(t) is Status.NEW and k - 1 in self._groupingMap.keys():
                    self.findOverlapInGroup(t, k - 1)

                if self._overlapGraph.getVertexLabel(t) is Status.NEW:
                    self._overlapGraph.updateVertex(Status.FIN, t)


        for t in self._overlapGraph.allVertices():
            print(t)
            if self._overlapGraph.getVertexLabel(t) is Status.USED:
                print("USED")
                self.removeTerm(t)

        self._simplifyRecurse(True)

    def findOverlapInGroup(self, term, groupNum):
        for t in self._groupingMap[groupNum]:
            idx = self.getDiffIdx(term, t)
            if idx != -1:
                self._overlapGraph.updateVertex(Status.USED, term)
                self._overlapGraph.updateVertex(Status.USED, t)

                newTerm = term[:idx] + "-" + term[idx + 1:]
                self.addTerm(newTerm)

    def getDiffIdx(self, term1, term2):
        if len(term1) is not len(term2):
            return -1

        diffCount = 0
        idx = -1

        for i in range(0, len(term1)):
            if term1[i] != term2[i]:
                diffCount += 1
                idx = i

        if diffCount is 1 and term1[idx] != "-" and term2[idx] != "-":
            return idx
        else:
            return -1

class Status:
    NEW = 0
    USED = 1
    FIN = 2

myBool = BooleanExpression()
exp = "a b c + a' b c' + a' b' c'"
myBool.parseExp(exp)

print(exp)
print(myBool._expression)
print(myBool._minTerm)
print(myBool._varList)
myBool.simplify()
print(myBool._expression)
