import pandas as pd
import pydot
import numpy as np
from collections import defaultdict

import itertools

class node(object):
    newid = itertools.count().next
    def __init__(self, split_var, split_val, dtype, parent):
        """A decision tree node.

        split_var := Variable that the data will get split on
        split_val := Value that this node takes for the split_var
        dtype := datatype for the split_var. Options are 'cat', 'cont'
        parent := id for the parent node
        """
        self.id = node.newid()
        if dtype == 'cat':
            if type(split_var) == tuple:
                raise TypeError()
            self.qstr = "%s == %s" % (split_var, split_val)
        elif dtype == 'cont':
            if type(split_var) != tuple:  # if it's a continuous value, should be a twople
                raise TypeError()
            self.qstr =

class dtree(object):

    def __init__(self, data):
        """Initialize a Decision Tree object.

        data := The full dataset in a Pandas Dataframe
        """
        self.df = data
        return None

    def _draw(self, parent_name, child_name):
        edge = pydot.Edge(parent_name, child_name)
        graph.add_edge(edge)

    def _visit(self, node, parent=None):
        for k, v in node.iteritems():
            if isinstance(v, dict):
                if parent:
                    self._draw(parent, k)
                self._visit(v, k)
        else:
            self._draw(parent, k)
            draw(k, k+'_'+v)

    def constructTree(self, splits):
        """
        splits should be a list of categorical variables.
        """
        self.dtree = defaultdict(dict)
        for s in splits:
            for v in np.unique(self.df[splits].values):
                self.dtree[v] = dict()


    def visualizeTree(self, output_path='./output.png'):
        graph = pydot.Dot(graph_type='graph')
        self._visit(output_tree)
        graph.write_png(output_path)
        return None
