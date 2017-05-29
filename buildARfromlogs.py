from collections import defaultdict
import sys

def parseLine(line):
    """
        Returns a DFS code edge from a string
    """
    line = line.replace('(','').replace(')','')
    line = line.split(',')
    v_from = int(line[0])
    v_to = int(line[1])
    label_from = line[2].replace(' \'','').replace('\'','')
    label_to = line[3].replace(' \'','').replace('\'','')
    edge_label = line[4].replace(' \'','').replace('\'','')
    return (v_from,v_to,label_from,label_to,edge_label)

def getPatterns(filename):
    """
        Returns a list of patterns (DFS codes) from an output file created by classificationWorkflow.logPatterns
    """
    patterns = {}
    with open(filename,'r') as log:

        current = ''
        for line in log:
            line = line.replace('\n','')
            if line == '' or 'time taken' in line:
                continue
            if 'Pattern' in line:
                current = line
                patterns[line] = []
            else:
                patterns[current].append(parseLine(line))
    return patterns.values()

class AR:
    """
        A class representing an Association Rule
    """

    def __init__(self,lhs='',rhs='',conf=0):
        self.confidence = conf
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return str(self.lhs) + "  ==>  " + str(self.rhs) + "  : " + str(self.confidence)

def buildARfromlogs(logfiledict,graphs,outputfile=None):
    """
        Params:
            - dictionary with as key the label, and as value a list of logfiles with their support
            - dictionary with as key the label, value is a list of graphs
            - optionally the name of an output file
        Returns: list of AR Association Rules
    """

    label2pattern2sup = defaultdict(list)
    for label, logfiles in logfiledict.items():
        #from high to low support to make sure only highest support is saved
        logfiles = sorted(logfiles,key=lambda x: x[1],reverse=True)
        for (filename,support) in logfiles:
            patterns = getPatterns(filename)
            for pattern in patterns:
                if len(filter(lambda x: x[0] == pattern,label2pattern2sup[label])) == 0:
                    label2pattern2sup[label].append((pattern,support))

    #list of association rules
    ARs = []

    for label, pattern2sup in label2pattern2sup.items():
        print "Building association rules for " + label + "..."
        i = 0
        for pattern, localsupport in pattern2sup:
            #pretty output
            sys.stdout.write('\r                                \r')
            sys.stdout.write( label + " finished " + str(round(float(i)/float(len(pattern2sup)) * 10000) / 100.0) + "%")
            sys.stdout.flush()
            totalsupport = localsupport
            for label2, label2graphs in graphs.items():
                if label2 != label:
                    for g in label2graphs:
                        if g.subgraphIsomorphism(pattern):
                            totalsupport += 1
            confidence = float(localsupport)/float(totalsupport)
            ARs.append(AR(pattern,label,confidence))
            i += 1
        print "\r                                                           \r" + label + " finished 100%"

    if outputfile != None:
        with open(outputfile,'w') as output:
            for rule in ARs:
                output.write(str(rule) + "\n")
    return ARs
