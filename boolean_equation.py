#!/usr/bin/python3
from labeled_digraph import LabeledDigraph

class BooleanExpression:
	expression = []
	minTerm = []
	varList = []

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

			if b not in self.varList:
				self.varList.append(b)

		minTerm.append(term)

		self.expression = exp
		self.minTerm = minTerm

	def simplify(self):
		print("Test")
		if len(self.minTerm) is 0:
			self.expression = [False]
			return

		termChart = {}
		for term in self.minTerm:
			c = term.count("1")
			if c in termChart.keys():
				termChart[c].append(term)
			else:
				termChart[c] = [term]

		print(termChart)

myBool = BooleanExpression()
exp = "a b c + a' b c' + a' b' c'"
myBool.parseExp(exp)

print(exp)
print(myBool.expression)
print(myBool.minTerm)
print(myBool.varList)
myBool.simplify()
