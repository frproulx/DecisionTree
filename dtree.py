import pandas as pd
import pydot
from collections import defaultdict

class dtree(object):

    def __init__(self, data):
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


    def visualizeTree(self, output_path='./output.png'):
        graph = pydot.Dot(graph_type='graph')
        self._visit(output_tree)
        graph.write_png(output_path)
        return None
