from graph import Graph

def read(filename):
    """
        Reads a file of the form:
            edges
            id1,id2
            idx,idy
            .
            .
            .
            labels
            idx,label1,label2,label3
            idy,label4,label5
            .
            .
            .

        where id is the id of a node and label is one of the labels of a node

        returns a graph of type graph.Graph
    """
    with open(filename, 'r') as data:

        g = Graph()
        mode = 1
        for line in data:
            if 'edges' in line:
                continue
            if 'labels' in line:
                mode = 2
                continue

            items = line.replace('\n','').split(',')

            if len(items) <= 1:

                continue
            if mode == 1:
                g.connect(items[0],items[1])
            if mode == 2:
                g.setLabels(items[0],items[1:])

        return g

if __name__ == "__main__":
    g = read("../data/testGraph.csv")
    print g.subgraphIsomorphism([(0,1,'D','T','_'),(1,2,'T','B','_'),(2,3,'B','C','_')])
