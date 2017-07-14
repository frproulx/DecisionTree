import pandas as pd
import pydot
import numpy as np
from collections import defaultdict

import xlsxwriter

import itertools

class decisionNode(object):
    newid = itertools.count().next
    def __init__(self, parent=None, qstr=None, df=None):
        """A decision tree node.

        parent := The parent node. None for root node.
        qstr := Query string to define this level. None for root node.
        df := pd.DataFrame containing the data. ONLY for root node.
        """
        self.id = decisionNode.newid()
        self.parent = parent
        if self.parent is None:
            self.qstr = ""
        else:
            self.qstr = qstr

        self.children = list()

        if df is not None:
            self.df = df
        elif self.parent is None:
            raise Exception()
        else:
            self.df = self.parent.df.query(self.qstr)

        self.size = len(self.df)
        if self.parent is None:
            self.marginal_prob = float(1.)
            self.overall_prob = float(1.)
        else:
            self.marginal_prob = float(self.size)/float(self.parent.size)
            self.overall_prob = self.marginal_prob * self.parent.marginal_prob

        self.depth = self._depth()

    def __repr__(self):
        return "%s%s (%d, %0.1f%%, %0.1f%%)" % ('\t'*self.depth,
                                           self.qstr,
                                           self.size,
                                           self.marginal_prob*100.,
                                           self.overall_prob*100.
                                           )

    def _print_children(self):
        print self
        for child in self.children:
            child._print_children()

    def _tofile(self, file):
        file.write(str(self) + '\n')
        for child in self.children:
            child._tofile(file)

    def _depth(self):
        if self.parent is not None:
            return self.parent._depth() + 1
        else:
            return 0

    def spawn_child(self, qstr):
        """ Creates a child.
        qstr := Marginal query string
        """
        self.children.append(decisionNode(self, qstr))

    def spawn_children(self, split_var, split_vals=None, dtype='cat'):
        if dtype == 'cat':
            if type(split_var) == tuple:
                raise TypeError()
            for v in np.unique(self.df[split_var]):
                qstr = "%s == '%s'" % (split_var, str(v))
                self.spawn_child(qstr)

        elif dtype == 'cont':
            # TODO implement this with pd.cut and create a categorical
            if type(split_vals) != list:  # if cont, should be cut points
                raise TypeError()
            raise NotImplementedError()
        else:
            raise NotImplementedError()

    def find_bottom(self):
        if self.children == []:
            return [self]
        else:
            found_children = [c.find_bottom() for c in self.children]
            return [item for sublist in found_children for item in sublist]

    def siblings(self):
        if self.parent is None:
            return []
        else:
            return [a for a in self.parent.children if a is not self]


class dtree(object):

    def __init__(self, data):
        """Initialize a Decision Tree object.

        data := The full dataset in a Pandas Dataframe
        """
        self.data = data
        self.tree = decisionNode(df=self.data.copy())


    def __repr__(self):
        if self.pretty_print() is not None:
            return self.pretty_print()
        else:
            return "A decision tree that has yet to be constructed."

    def _reset(self):
        self.tree = decisionNode(df=self.data.copy())

    def split_tree(self, split_vars, reset=False):
        """Construct the tree splits

        split_vars := The variables you want the tree split on as a list
        reset := Boolean. Do you want a fresh tree?
        """
        self._reset()
        # TODO implement the split_vars for continuous variables to take cut points
        for s in split_vars:
            # This needs to go to the deepest children and do the splits
            for c in self.tree.find_bottom():
                c.spawn_children(s)

    def pretty_print(self):
        self.tree._print_children()

    def to_excel(self, output_name, output_sheet):
        raise NotImplementedError()
        if output_name[-5:] != '.xlsx':
            output_name += '.xlsx'
        with xlsxwriter.Workbook(output_name) as workbook:
            worksheet = workbook.add_worksheet(name=output_sheet)

    def to_text(self, file_name):
        """ Dumps pretty printed tree to <file_name>.txt"""
        with open(file_name, mode='w') as fi:
            fi.write("Structured as 'leaf details (Number records, Marginal Share, Overall Share)'")
            self.tree._tofile(fi)


class Blah(object):
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
