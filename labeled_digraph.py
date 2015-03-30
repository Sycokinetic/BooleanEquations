class LabeledDigraph:
	# == CONSTRUCTOR ==
	def __init__(self):
		self._vertexSet = []
		self._graphData = {}

	# == ACCESSORS ==
	def is_empty(self):
		if len(self._vertexSet) == 0:
			return True
		else:
			return False

	def has_vertex(self, v):
		if v in self._vertexSet:
			return True
		else:
			return False

	def get_vertex(self, n):
		if n < len(self._vertexSet):
			return self._vertexSet[n]
		else:
			return None

	def get_vertex_index(self, v):
		if v in self._vertexSet:
			return self._vertexSet.index(v)
		else:
			return None

	def get_vertex_label(self, v):
		if v in self._graphData:
			return self._graphData[v][0]
		else:
			return None

	def has_edge(self, item1, item2=None):
		if item2 is not None:
			if item1 in self._graphData.keys() and item2 in self._graphData[item1][1]:
				return True
			else:
				return False
		else:
			return self.has_edge(item1[0], item1[1])

	def get_edge_label(self, item1, item2=None):
		if item2 is not None:
			if item1 in self._graphData and item2 in self._graphData[item1][1]:
				return self._graphData[item1][1][item2]
			else:
				return None
		else:
			return self.get_edge_label(item1[0], item1[1])

	def all_vertices(self):
		return list(self._vertexSet)

	def from_edges(self, v):
		if v in self._graphData:
			edgeSet = []
			for v_i in self._graphData[v][1].keys():
				edgeSet.append([v, v_i])

			return edgeSet
		else:
			return None

	# == MUTATORS ==
	def add_vertex(self, l, v):
		if v not in self._vertexSet:
			self._vertexSet.append(v)
			self._graphData[v] = [l, {}]
		
	def update_vertex(self, l, v):
		if v in self._graphData:
			self._graphData[v][0] = l

	def remove_vertex(self, v):
		if v in self._vertexSet:
			self._vertexSet.remove(v)
			del self._graphData[v]
			for v_i in self._graphData:
				if self.has_edge(v_i, v):
					del self._graphData[v_i][1][v]

	def add_edge(self, l, item1, item2=None):
		if item2 is not None:
			if not self.has_edge(item1, item2):
				if self.has_vertex(item1) and self.has_vertex(item2):
					self._graphData[item1][1][item2] = l
		else:
			self.add_edge(l, item1[0], item1[1])

	def remove_edge(self, item1, item2=None):
		if item2 is not None:
			if self.has_edge(item1, item2):
				del self._graphData[item1][1][item2]
		else:
			self.remove_edge(item1[0], item1[1])

	def update_edge(self, l, item1, item2=None):
		if item2 is not None:
			if self.has_edge(item1, item2):
				self._graphData[item1][1][item2] = l
		else:
			self.update_edge(l, item1[0], item1[1])
