from enum import Enum

class Status(Enum):
    NEW = 0
    USED = 1
    FIN = 2

class DiffCase(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2

class QuineMcCluskeyChart:
    def __init__(self, minTerm):
        self._maxN = -1
        self._groupingDict = {}
        self._statusDict = {}
        self._minTerm = []

        for t in minTerm:
            self._addTerm(t)

        self._simplify()

    def getMinTerm(self):
        return self._minTerm

    def _addTerm(self, term):
        n = term.count('1')
        if n > self._maxN:
            for i in range(self._maxN + 1, n):
                self._groupingDict[i] = []

            self._maxN = n
            self._groupingDict[n] = [term]
        else:
            self._groupingDict[n].append(term)

        self._statusDict[term] = Status.NEW

    def _removeTerm(self, term):
        n = term.count('1')
        self._groupingDict[n].remove(term)
        del self._statusDict[term]

    def _simplify(self):
        # Add case for empty minterm
        finished = True
        for t in self._statusDict.keys():
            if self._statusDict[t] is Status.NEW:
                finished = False
                break
        if finished:
            return

        for k in self._groupingDict.keys():
            for t in self._groupingDict[k]:
                if self._statusDict[t] is Status.NEW and k + 1 in self._groupingDict.keys():
                    self._createGroupFromOverlap(t, k + 1)

                if self._statusDict[t] is Status.NEW and k - 1 in self._groupingDict.keys():
                    self._createGroupFromOverlap(t, k - 1)

                if self._statusDict[t] is Status.NEW:
                    self._statusDict[t] = Status.FIN


        delTerms = []
        for t in self._statusDict.keys():
            if self._statusDict[t] is Status.USED:
                delTerms.append(t)

        for t in delTerms:
            self._removeTerm(t)

        self._simplify()
        self._minTerm = list(self._statusDict.keys())

    def _createGroupFromOverlap(self, term, groupNum):
        for t in self._groupingDict[groupNum]:
            idx = self._getDiffIdx(term, t)
            if idx[0] is not -1:
                if idx[1] is DiffCase.NONE:
                    self._statusDict[term] = Status.USED
                    self._statusDict[t] = Status.USED

                    newTerm = term[:idx[0]] + '-' + term[idx[0]+1:]
                    self._addTerm(newTerm)
                elif idx[1] is DiffCase.LEFT:
                    self._statusDict[term] = Status.USED
                elif idx[1] is DiffCase.RIGHT:
                    self._statusDict[t] = Status.USED
                break

    def _getDiffIdx(self, term1, term2):
        if len(term1) is not len(term2):
            return (-1, DiffCase.NONE)

        diffCount = 0
        idx = -1

        for i in range(0, len(term1)):
            if term1[i] != term2[i]:
                diffCount += 1
                idx = i

        if diffCount is 1 and term1[idx] is not '-' and term2[idx] is not '-':
            return (idx, DiffCase.NONE)
        elif diffCount is 1 and term1[idx] is not '-' and term2[idx] is '-':
            return (idx, DiffCase.LEFT)
        elif diffCount is 1 and term1[idx] is '-' and term2[idx] is not '-':
            return (idx, DiffCase.RIGHT)
        else:
            return (-1, DiffCase.NONE)
