from algorithms import gSpan
from readGraph import read
import os
from buildARfromlogs import buildARfromlogs
from Classify import predict

def logPatterns(patterns,filename):
    """
        Write out gSpan patterns to a file
    """
    with open(filename,'w') as out:
        for i, ext in enumerate(patterns):
            labeldict = {}
            out.write('Pattern ' + str(i+1) + '\n')
            for _c in ext:
                out.write(str(_c) + '\n')
            out.write('\n')

if __name__ == '__main__':
    group1folder = "data/TestGroup1/"
    group2folder = "data/TestGroup2/"
    testgraphFile = "data/classifyme.csv"

    group1 = []
    group2 = []

    for filename in os.listdir(group1folder):
        graph = read(group1folder+filename)
        group1.append(graph)

    for filename in os.listdir(group2folder):
        graph = read(group2folder+filename)
        group2.append(graph)

    testgraph = read(testgraphFile)

    print "Frequent subgraphs in group 1:"
    extensionlist = gSpan(group1,minSup=4,maxthreads=1)

    logPatterns(extensionlist,'group1.out')

    print "Frequent subgraphs in group 2:"
    extensionlist = gSpan(group2,minSup=4,maxthreads=1)

    logPatterns(extensionlist,'group2.out')

    graphs = {
        'group1': group1,
        'group2': group2
    }

    labels = {
        'group1':
            [
                ('group1.out',4)
            ],
        'group2':
            [
                ('group2.out',4)
            ]
    }
    #list of association rules derived from frequent patterns
    ARs = buildARfromlogs(labels,graphs)

    print "Predicted label for graph '" + testgraphFile + "': " + predict(ARs,testgraph,top=5)
