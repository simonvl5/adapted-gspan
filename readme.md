# Multi-labelled graph mining and graph classification
An adaptation on [this gSpan algorithm](https://github.com/LasseRegin/gSpan) to allow frequent subgraph mining in graphs that have zero or more labels per node. This implementation allows parallelisation which greatly increases its performance. Additionally the frequent subgraphs are good features for graph classification so a simple yet effective classification technique is included.
## Dependencies

* [Numpy](http://www.numpy.org/)
* [Graphviz (optional)](http://www.graphviz.org/)

# Documentation
## Test
An example to test both the graph mining and classification is provided in classificationWorkflow.py.
```bash
python classificationWorkflow.py
```
It should display DFS codes of frequent subgraphs found in both groups, and will classify a test graph into group 1.
## Multi-labelled graph mining

### Graph file format
```
edges
1,2
2,3
1,3
2,4
3,4
4,6
6,5
5,7
5,8
labels
1,A
2,B
3,C,T
4,D,A
5,E
6,
7,G
8,H
```
The first part connects all the edges given the id of each node. The second part assigns zero or more labels to each node.
The resulting graph looks like this:
![](https://github.com/simonvl5/adapted-gspan/blob/master/data/example.png)

```python
from readGraph import read

graph = read('data/example.csv')
```
### Graph class
The graph.Graph class has a few useful methods.
#### Graph.toPNG(filename [,render])
* filename: `string`
* render: `bool`

Will output graph to a .dot file. If render is set to True and Graphiz is installed on the system it will render the graph to a PNG.

#### Graph.diameter([cores])
* cores: `int`

Returns the diameter of the Graph, i.e. the maximum shortest path between any two nodes. This process can be intensive so the number of cores can be set to parallellise the process.

#### Graph.EVCentrality([maxit])
* maxit: `int`

Returns a dictionary of all Eigen Vector Centrality values per node. Increase 'maxit' to improve precision.

#### Graph.globalClusteringCoefficient()
Returns the average local clustering coefficient of the graph.

### gSpan
#### algorithms.gSpan(DS, minSup, maxthreads [,uniqeempty])
* DS: `list`
* minSup: `int`
* maxthreads: `int`
* uniqeempty: `bool`

Will return a list of DFS codes of frequent subgraphs given a list of Graph.graph objects, a minimum support and a number of maximum threads to be used. 'uniqeempty' default to false, meaning that two nodes with no labels will be considered to be equal. When set to 'True' all nodes with no label will be considered to be unique.

## Classification

For the classification you need to save the output of the graph mining in a file of the following format. This is the output of group 1 in the classificationWorkflow file.

```
Pattern 1
(0, 1, 'B', 'T', '_')

Pattern 2
(0, 1, 'A', 'B', '_')

Pattern 3
(0, 1, 'A', 'B', '_')
(1, 2, 'B', 'T', '_')

Pattern 4
(0, 1, 'A', 'B', '_')
(1, 2, 'B', 'T', '_')
(2, 0, 'T', 'A', '_')

Pattern 5
(0, 1, 'A', 'B', '_')
(0, 2, 'A', 'T', '_')

Pattern 6
(0, 1, 'A', 'T', '_')

Pattern 7
(0, 1, 'A', 'T', '_')
(1, 2, 'T', 'B', '_')
```
The classificationWorkflow file also contains a function 'logPatterns' wich will output the results of the graph mining algorithm in the correct format.

There are two phases to classifying a graph. In the first phase you need to build a list of association rules. In the second phase you can predict the label of a graph, given the association rules.

#### buildARfromlogs.buildARfromlogs(logfiledict, graphs [,outputfile])
* logfiledict: `dict`
* graphs: `dict`
* outputfile: `string`

Returns a list of association rules: frequent subgraph => group label (confidence).
logfiledict is a dictionary with as key a group label, and as value a list of (filename,minSup) tuples. Where filename is the name of the file where the frequent patterns are logged. This is because sometimes you want to repeat the graph mining a few times with decreasing minimum supports. When outputfile is given, writes the association rules to a file.

#### Classify.predict(ARs, graph [,top])
* ARs: `list`
* graph: `Graph.graph`
* top: `int`

Returns the predicted label for 'graph'. ARs is a list of association rules returned by buildARfromlogs.buildARfromlogs(). top is the number of association rules that should be used for classification. This number highly depends on the data. The default is  
