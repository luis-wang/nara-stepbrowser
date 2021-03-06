#!/usr/bin/env python

import re, os

from PyQt4 import QtGui
import matplotlib.pyplot as PLT
import networkx as NX
import numpy

class GraphCoOccurence(object):
    def __init__(self, parent = None):
        self.parent = parent

        #Dialog for step directory if not set
        if self.parent.step_path == None:
            filedialog = QtGui.QFileDialog()
            step_path = filedialog.getExistingDirectory(None, 'Open Directory', '')
            self.parent.set_step_path(str(step_path))

        #self.parent.parent = stepBrowser
        os.chdir(self.parent.parent.step_path)
        dirlist = os.listdir(self.parent.parent.step_path)

        #Build dictionary
        stepdict = dict()
        term_lists = dict()
        for f in dirlist:
            if os.path.isfile(os.path.join(self.parent.parent.step_path, f)) and self.isStepFilename(f):
                #print(f)
                term_lists[f] = set()
                for line in open(f):
                    line_parts = line.split("'")
                    for i in range(1,len(line_parts),2):
                        string = line_parts[i]
                        if string != '' and string[0] != '#':

                            tokens = re.split('\W+', string)
                            for token in tokens:
                                if token != '':
                                    term_lists[f].add(token)
                                    if token in stepdict:
                                        stepdict[token] = stepdict[token] + 1
                                    else:
                                        stepdict[token] = 1
                                        
        #print term_lists

        n = len(term_lists)
        A = numpy.zeros((n,n))               

        #find cooccurences using intersect
        index1 = 0
        for key1, value1 in term_lists.items():
            print index1, key1
            index2 = 0
            for key2, value2 in term_lists.items():
                c = len(value1 & value2)
                A[index1, index2] = c
                A[index2, index1] = c
                index2 = index2 + 1
                
            index1 = index1 + 1
    
        Gh = NX.Graph(data=A)
        all_nodes = Gh.nodes()
        edges = Gh.edges()
        ecolors = [A[node[0], node[1]] for node in edges]

        # to scale node size with degree:
        scaled_node_size = lambda(node) : NX.degree(Gh, node) * 15
        #position = NX.circular_layout(Gh)    # just choose a layout scheme
        position = NX.spring_layout(Gh)    # just choose a layout scheme
        #position = NX.shell_layout(Gh)    # just choose a layout scheme
        NX.draw_networkx_nodes(Gh, position, node_size=map(scaled_node_size, all_nodes), 
                               node_color='w', alpha = .75, ax=self.parent.axes)
                
        NX.draw_networkx_edges(Gh, position, Gh.edges(), width=1.0, 
                               alpha=0.75, edge_color = ecolors, edge_cmap=PLT.cm.Blues,
                               edge_vmin = A.min(), edge_vmax = A.max(), ax=self.parent.axes)
                
        NX.draw_networkx_labels(Gh, position, fontsize = 14, ax=self.parent.axes)


    def intersect(self, a, b):
        '''return the intersection of two lists'''
        return list(set(a) & set(b))


    def isStepFilename(self, f):
        return f.endswith('.stp') or f.endswith('.STP') or f.endswith('.step') or f.endswith('.STEP')
