from collections import defaultdict
import os
from algorithms import Graph as gspanGraph,Vertex,Edge,subgraph_isomorphism
from copy import copy as clone
import time
from multiprocessing import Queue,Value,Process

class Graph:

    def __init__(self):
        self._graph = defaultdict(set)
        self._labels = defaultdict(set)
        self.support = None
        self.dfs_code = None
        self.dfsToNode = dict()

    def connect(self, node1, node2):
        """
            connect two nodes together
        """
        self._graph[node1].add(node2)
        self._graph[node2].add(node1)

    def deConnect(self, node1, node2):
        """
            remove connection
        """
        self._graph[node1].remove(node2)
        self._graph[node2].remove(node1)

    def next(self, node):
        """
            Return adjecent nodes
        """
        return self._graph[node]

    def out(self):
        """
            Function to print graph, will only be usefull for smaller graphs
        """
        for key in self._graph.keys():
            outStr = str(key) + " -- {"
            for value in self._graph[key]:
                outStr += str(value) + ", "
            if len(outStr) > 5:
                outStr = outStr[:-2]
            outStr += "}\t\t"
            for label in self.getLabels(key):
                outStr += str(label) + ", "
            outStr = outStr[:-2]
            print outStr

    def toPNG(self, filename,render=False):
        """
            Will output graph to a .dot file
            If render is set to True it will render the png using graphviz dot
        """

        dotname = filename.split('.')[0] + ".dot"

        with open(dotname,'w') as outfile:
            outfile.write("strict graph g {")

            for key in self._graph.keys():
                outStr = ''
                #set the label (now arbitrarily a label is chosen if more than one is present)
                if len(self.getLabels(key)) > 0:
                    labels = ""
                    for l in self.getLabels(key):
                        labels += str(l) + ","
                    labels = labels[:-1]
                    outStr += str(key) + " [label=\"" + str(labels) + "\"]\n"
                #set the connections if there are
                if len(self._graph[key]) == 0:
                    break
                outStr += str(key) + " -- {"

                for value in self._graph[key]:
                    outStr += str(value) + " "
                if len(outStr) > 5:
                    outStr = outStr[:-1]
                outStr += "}\n"

                outfile.write(outStr)
            outfile.write("}")
        if render:
            os.system("dot -Tpng " + dotname + " > " + filename)
            os.system("rm " + dotname)

    def setLabel(self, node, label):
        """
            Set a single label to a node
        """
        self._labels[node].add(label)

    def setLabels(self, node, labels):
        """
            Set a list/set of labels to a node
        """
        for label in labels:
            self.setLabel(node, label)

    def getLabels(self, node):
        """
            Return labels of a node as a set
        """
        return self._labels[node]

    #when working with only one label in testing phase
    def getLabel(self,node):
        """
            Returns the top label of a node, not usefull when working with multiple labels
        """
        return self._labels[node].copy().pop()

    def getNodes(self):
        """
            Get list of nodes
        """
        nodes = []
        for key,value in self._graph.items():
            nodes.append(key)
        nodes = list(set(nodes))
        return nodes

    def getEdges(self):
        """
            Get list of edges
        """
        edges = []
        for key,value in self._graph.items():
            for v in value:
                if v >= key:
                    edges.append((key,v))

        edges = list(set(edges))
        return edges

    def removeNode(self,node):
        """
            Remove a node and its connections from the graph
        """
        for neighbour in self.next(node).copy():
            self.deConnect(node,neighbour)
        self._graph.pop(node)

    def contains(self, node):
        """
            True if node in graph
        """
        S = set()
        for key,values in self._graph.items():
            S = S.union(key)
            S = S.union(values)

        return node in S

    # depth first search to see if nodes are connected
    def areConnected(self, node1, node2):
        """
            True if two nodes are connected in some path
        """
        self.visited = set()
        self.path = list()
        connected = self.connected(node1, node2)
        # self.path = self.path.reverse()
        return connected

    def connected(self, node1, node2):
        """
            Recursive call, not to be called directly
        """
        if node1 == node2:
            return True

        neighbours = self.next(node1)
        self.visited.add(node1)

        if node2 in neighbours:
            self.path.append(node2)
            return True

        for node in neighbours:
            if not(node in self.visited):
                if self.connected(node, node2):
                    self.path.append(node)
                    return True
        return False

    def shortestPath(self, node1, node2):
        """
            Implementation of dijkstra's algorithm
            Returns the length of the shortes path as well as the Shortest path
        """

        if not(self.areConnected(node1, node2)):
            return -1, []

        values = dict()
        for key in self._graph.keys():
            values[key] = float("inf")
        values[node1] = 0
        visited = set()
        visited.add(node1)
        current = node1

        while not(node2 in visited):
            l = values[current]
            for neighbour in self.next(current):
                if not(neighbour in visited):
                    newlength = l + 1
                    if newlength < values[neighbour]:
                        values[neighbour] = newlength

            visited.add(current)

            lowest = ('', float("inf"))
            for key in values.keys():
                if not(key in visited) and (values[key] < lowest[1]):
                    lowest = (key, values[key])

            current = lowest[0]

        #backtrack
        length = values[node2]
        path = [node2]
        previous = node2
        for i in range(length-1,-1,-1):
            newnode = [node for node in values.keys() if values[node] == i and node in self.next(previous)][0]
            path.append(newnode)
            previous = newnode

        return length, list(reversed(path))

    def maxpathfrom(self,a,nodes,q):
        diameter = -1
        for b in range(a+1,len(nodes)):
            if a != b:
                pathlength, _ = self.shortestPath(nodes[a],nodes[b])
                if pathlength > diameter:
                    diameter = pathlength
        q.put(diameter)

    def diameter(self,cores=1):
        """
            Returns the diameter of the Graph, i.e. max(shortestPath(a,b) for all a and b)
            Set number of cores to parallellise the process as it is an intensive operation
        """
        nodes = self.getNodes()
        allnodes = len(nodes)
        it = 0
        q = Queue()
        a = 0
        while a < len(nodes):
            pool = []
            for i in range(0,cores):
                if (a+i) < len(nodes):
                    p = Process(target=self.maxpathfrom,args=(a+i,nodes,q))
                    p.start()
                    pool.append(p)

            for p in pool:
                p.join()
            a += cores

        get = True
        diameters = []
        while get:
            try:
                top = q.get(block=False)
                diameters.append(top)
            except:
                get = False

        return max(diameters)

    def EVCentrality(self,maxit=100):
        """
            returns a dict of all Eigen Vector Centrality values
        """
        nodes = self.getNodes()
        V = defaultdict(lambda: 1)

        for i in range(0,maxit):
            W = defaultdict(lambda: 0)
            for node in nodes:
                for neighbour in self.next(node):
                    W[neighbour] = W[neighbour] + V[node]
            V = clone(W)
        S = 0
        for _,i in V.items():
            S += i
        for key,value in V.items():
            V[key] = float(value)/float(S)

        return V


    emptylabelnumber = 0

    def clusteringCoefficient(self,node):
        """
            Returns local clustering coefficient of a node
        """
        neighbours = self.next(node)
        k = len(neighbours)
        if k < 2:
            return 0
        closedNeighbours = 0
        for j in neighbours:
            for n in neighbours:
                if j != n:
                    if n in self.next(j):
                        closedNeighbours += 1
        #each edge would be counted twice so drop the two
        return float(closedNeighbours)/ float(k * (k-1))


    def globalClusteringCoefficient(self):
        """
            Returns global clustering coefficient (avg local CC) of a graph
        """
        nodes = self.getNodes()
        C = 0
        for i in nodes:
            Ci = self.clusteringCoefficient(i)
            # print Ci
            C += Ci
        return C/len(nodes)

    def convert(self,id,maxlabels=99999,uniqueEmptylabels=True):
        """
            Convert this graph to the format needed for the gSpan algorithm
        """
        newGraph = gspanGraph(id=id)

        for key,values in self._graph.items():
            l = self.getLabels(key).copy().pop();

            if uniqueEmptylabels:
                #make sure an empty label will get assigned a unique label so that no two empty labels are the same
                if l == '':
                    l = "EMPTYLABEL" + str(Graph.emptylabelnumber)
                    Graph.emptylabelnumber += 1

            v = Vertex(id=int(key.encode("hex"),16), label=l)
            newGraph.add_vertex(vertex=v)
            if "EMPTYLABEL" in l:
                newGraph.labeldict[v.id] = set([l])
            else:
                newGraph.labeldict[v.id] = set(list(self.getLabels(key))[:maxlabels])

        for key,values in self._graph.items():
            for value in values:
                e = Edge(label='_',from_vertex=newGraph.get_vertex(id=int(key.encode("hex"),16)), to_vertex=newGraph.get_vertex(id=int(value.encode("hex"),16)))
                newGraph.add_edge(edge = e)

        return newGraph

    def subgraphIsomorphism(self,subgraph):
        """
            True if there is a subgraph isomorphism of the subgraph in this graph
            subgraph must be a gSpan DFS code
        """
        return subgraph_isomorphism(subgraph,self.convert(0,uniqueEmptylabels=False))
