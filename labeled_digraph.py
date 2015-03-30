# LabeledDigraph Class
#       API Documented in AlexGunter_556_HW1_DigraphADT_Spec.txt
#       
#       Example of Data Structure:
#       _vertexSet = [
#               vertex0,
#               vertex1,
#               vertex2,
#               ...
#       ]
#
#       _graphData = {
#               vertex0 : [vLabel0, { vertex1 : eLabel0_1, vertex2 : eLabel0_2, ... }],
#               vertex1 : [vLabel1, { vertex0 : eLabel1_0, ... }],
#               vertex2 : [vLabel2, { vertex1 : eLabel2_1, ... }],
#               ...
#       }

class LabeledDigraph(object):
    _vertexSet = []
    _graphData = {}

    # == ACCESSORS ==
    def isEmpty(self):
        if len(self._vertexSet) == 0:
            return True
        else:
            return False

    def hasVertex(self, v):
        if v in self._vertexSet:
            return True
        else:
            return False

    def getVertex(self, n):
        if n < len(self._vertexSet):
            return self._vertexSet[n]
        else:
            return None

    def getVertexIndex(self, v):
        if v in self._vertexSet:
            return self._vertexSet.index(v)
        else:
            return None

    def getVertexLabel(self, v):
        if v in self._graphData:
            return self._graphData[v][0]
        else:
            return None

    def hasEdge(self, item1, item2=None):
        if item2 is not None:
            if item1 in self._graphData.keys() and item2 in self._graphData[item1][1]:
                return True
            else:
                return False
        else:
            return self.hasEdge(item1[0], item1[1])

    def getEdgeLabel(self, item1, item2=None):
        if item2 is not None:
            if item1 in self._graphData and item2 in self._graphData[item1][1]:
                return self._graphData[item1][1][item2]
            else:
                return None
        else:
            return self.getEdgeLabel(item1[0], item1[1])

    def allVertices(self):
        return list(self._vertexSet)

    def fromEdges(self, v):
        if v in self._graphData:
            edgeSet = []
            for v_i in self._graphData[v][1].keys():
                edgeSet.append([v, v_i])

            return edgeSet
        else:
            return None

    def numVertices(self):
        return len(self._vertexSet)

    def numEdges(self):
        count = 0
        for v in self._graphData.keys():
            for e in self._graphData[v][1]:
                count += 1

        return count

    # == MUTATORS ==
    def addVertex(self, l, v):
        if v not in self._vertexSet:
            self._vertexSet.append(v)
            self._graphData[v] = [l, {}]
        
    def updateVertex(self, l, v):
        if v in self._graphData:
            self._graphData[v][0] = l

    def removeVertex(self, v):
        if v in self._vertexSet:
            self._vertexSet.remove(v)
            del self._graphData[v]
            for v_i in self._graphData:
                if self.hasEdge(v_i, v):
                    del self._graphData[v_i][1][v]

    def addEdge(self, l, item1, item2=None):
        if item2 is not None:
            if not self.hasEdge(item1, item2):
                if self.hasVertex(item1) and self.hasVertex(item2):
                    self._graphData[item1][1][item2] = l
        else:
            self.add_edge(l, item1[0], item1[1])

    def removeEdge(self, item1, item2=None):
        if item2 is not None:
            if self.hasEdge(item1, item2):
                del self._graphData[item1][1][item2]
        else:
            self.remove_edge(item1[0], item1[1])

    def updateEdge(self, l, item1, item2=None):
        if item2 is not None:
            if self.hasEdge(item1, item2):
                self._graphData[item1][1][item2] = l
        else:
            self.update_edge(l, item1[0], item1[1])
