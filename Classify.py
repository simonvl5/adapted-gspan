import sys
from buildARfromlogs import AR,parseLine
from collections import defaultdict
import time

def ARfromString(line):
    """
        Parse an Association Rule from a string
    """
    items = line.split('  ==>  ')
    lhs = items[0]
    lhs = lhs.replace('[','').replace(']','').split('), (')

    newlhs = []
    for edge in lhs:
        newlhs.append(parseLine(edge))
    rhs = items[1].split('  : ')[0]
    confidence = float(items[1].split('  : ')[1].replace('\n',''))
    return AR(newlhs,rhs,confidence)

def predict(ARs, graph,top=10):
    """
        Returns a predicted label for a graph, given a list of Association Rules
        top defines how many highest confidence Association Rules should be used
        increase top if your list of Association Rules is large (> 100)
    """

    relevantARs = []

    for i, ar in enumerate(ARs):
        #This is just some pretty printing of progress
        sys.stdout.write('\r                                \r')
        sys.stdout.write("Predicting label " + str(round(float(i)/float(len(ARs)) * 10000) / 100.0) + "%")
        sys.stdout.flush()
        if graph.subgraphIsomorphism(ar.lhs):
            relevantARs.append(ar)

    print "\r                                                           \rPredicting label 100%"
    labels = set()
    for ar in relevantARs:
        labels.add(ar.rhs)

    if len(labels) == 1:
        return labels.pop()

    if len(labels) == 0:
        return 'Support of every rule is 0'

    relevantARs = sorted(relevantARs,key=lambda x: x.confidence,reverse=True)
    groupscores = defaultdict(lambda: 0)
    for i in range(min(len(relevantARs),top)):
        rule = relevantARs[i]
        groupscores[rule.rhs] += 1

    return max(groupscores.iterkeys(),key=lambda x: groupscores[x])
