"""This is the main module for making manual decision trees."""

import pandas as pd
import pydot
import numpy as np
from collections import defaultdict

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

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
            self.var = 'All data'
            self.val = 'All data'
        else:
            self.qstr = qstr
            self.var, self.val = self.qstr.split(' == ')
            self.val = self.val.strip("'")

        self.children = list()
        self.n_terminal = 0

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
        """Prints out the children of this node."""
        print self
        for child in self.children:
            child._print_children()

    def _tofile(self, file):
        """Utility function for writing a node to a text file."""
        file.write(str(self) + '\n')
        for child in self.children:
            child._tofile(file)

    def _toexcel(self, worksheet, merge_format, pct_format):
        """Prepare the data in the node for Excel writing."""
        global depth_used
        if self.n_terminal == 0:
            height = 1
        else:
            height = self.n_terminal
        start_col = self.depth * 4
        if depth_used[self.depth] == 1:
            worksheet.write(0, start_col, self.var)
            worksheet.write(0, start_col + 1, 'N')
            worksheet.write(0, start_col + 2, 'Marginal Share')
            worksheet.write(0, start_col + 3, 'Overall Share')
        start_row = depth_used[self.depth]
        self.start_row = start_row

        # Needs the leaf description, number of records, marginal share,
        # tot share, height,
        marg_prob_function = '=%s/%s'  # String for writing marg calc
        overall_prob_function = '=%s*%s'
        if self.parent is None:
            parent_start_row = self.start_row
            parent_start_col = start_col
        else:
            parent_start_row = self.parent.start_row
            parent_start_col = start_col - 4
        if height == 1:
            worksheet.write(start_row, start_col, self.val, merge_format)
            worksheet.write(start_row, start_col + 1, self.size, merge_format)
            worksheet.write(start_row, start_col + 2,
                            marg_prob_function %
                            (xl_rowcol_to_cell(self.start_row,
                                               start_col+1),
                             xl_rowcol_to_cell(parent_start_row,
                                               parent_start_col+1)),
                            pct_format)
            if parent_start_col == start_col:
                worksheet.write(start_row, start_col + 3,
                                '=%s' % xl_rowcol_to_cell(start_row,
                                                          start_col + 2),
                                pct_format)
            else:
                worksheet.write(start_row, start_col + 3,
                            overall_prob_function %
                            (xl_rowcol_to_cell(self.start_row,
                                               start_col + 2),
                             xl_rowcol_to_cell(parent_start_row,
                                               parent_start_col+3)),
                                               pct_format)

        else:
            worksheet.merge_range(start_row, start_col,
                                      start_row + height - 1, start_col,
                                      self.val, merge_format)
            worksheet.merge_range(start_row, start_col + 1,
                                  start_row + height - 1, start_col + 1,
                                  self.size, merge_format)
            worksheet.merge_range(start_row, start_col + 2,
                                  start_row + height - 1, start_col + 2,
                                  marg_prob_function %
                                  (xl_rowcol_to_cell(self.start_row,
                                                     start_col+1),
                                   xl_rowcol_to_cell(parent_start_row,
                                                     parent_start_col+1)),
                                  pct_format)
            if parent_start_col == start_col:
                worksheet.merge_range(start_row, start_col + 3,
                                      start_row + height - 1, start_col + 3,
                                      '=%s' % xl_rowcol_to_cell(start_row,
                                                                start_col + 2))
            else:
                worksheet.merge_range(start_row, start_col + 3,
                                      start_row + height - 1, start_col + 3,
                                      overall_prob_function %
                                      (xl_rowcol_to_cell(self.start_row,
                                                         start_col + 2),
                                       xl_rowcol_to_cell(parent_start_row,
                                                         parent_start_col+3)),
                                                         pct_format)
        depth_used[self.depth] += height
        if self.n_terminal != 0:
            for child in self.children:
                child._toexcel(worksheet, merge_format, pct_format)

    def _depth(self):
        """Calculate depth of this node."""
        if self.parent is not None:
            return self.parent._depth() + 1
        else:
            return 0

    def _terminal_children(self):
        """Count number of terminal children under this node."""
        self.n_terminal = 0
        if self.children != []:
            for child in self.children:
                child._terminal_children()
            if self.parent is not None:
                self.parent.n_terminal += self.n_terminal
        else:
            self.parent.n_terminal += 1

    def _visualize(self):
        """Make a set of pydot Edges for all links."""
        edges = []
        if self.children != []:
            for child in self.children:
                edges.append(pydot.Edge(str(self), str(child)))
                edges.extend(child._visualize())
        return edges

    def spawn_child(self, qstr):
        """ Create a child.
        qstr := Marginal query string
        """
        self.children.append(decisionNode(self, qstr))

    def spawn_children(self, split_var, split_vals=None, dtype='cat'):
        if dtype == 'cat':
            if type(split_var) == tuple:
                raise TypeError()
            self.df[split_var] = self.df[split_var].astype(str)
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
        self.root = decisionNode(df=self.data.copy())


    def __repr__(self):
        if self.pretty_print() is not None:
            return self.pretty_print()
        else:
            return "A decision tree that has yet to be constructed."

    def _reset(self):
        self.root = decisionNode(df=self.data.copy())

    def split_tree(self, split_vars, reset=False):
        """Construct the tree splits

        split_vars := The variables you want the tree split on as a list
        reset := Boolean. Do you want a fresh tree?
        """
        self._reset()
        # TODO implement the split_vars for continuous variables to take cut points
        # TODO accept splitting constraints
        for s in split_vars:
            # This needs to go to the deepest children and do the splits
            for c in self.root.find_bottom():
                c.spawn_children(s)

    def pretty_print(self):
        self.root._print_children()

    def to_excel(self, workbook, output_sheet,
                 highlight_leaves=True, closeit=True):
        """Write a tree to an excel sheet.

        workbook := An xlsxwriter.workbook
        output_sheet := Name for the worksheet
        """
        merge_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter'})
        pct_format = workbook.add_format({'align': 'center',
                                          'valign': 'vcenter'
                                          })
        pct_format.set_num_format('0.0%')

        global depth_used
        depth_used = defaultdict(lambda: 1)

        self.root._terminal_children()
        #if output_name[-5:] != '.xlsx':
        #    output_name += '.xlsx'
        worksheet = workbook.add_worksheet(name=output_sheet)
        self.root._toexcel(worksheet, merge_format, pct_format)

        if highlight_leaves:
            for d in depth_used.keys():
                if d == 0:
                    continue
                worksheet.conditional_format(1, d*4+3,
                                             depth_used[d], d*4+3,
                                             {'type': '2_color_scale',
                                              'min_type': 'min',
                                              'max_type': 'max',
                                              'min_color': 'white',
                                              'max_color': 'red'})
        if closeit:
            workbook.close()

    def many_trees_to_excel(self, defdict, workbook):
        """ Generate many trees and write them to a common Excel workbook.

        defdict := dictionary with keys as sheet names and values as list of
                   columns to construct the tree
        workbook_path := name of the workbook
        """
        for name, cols in defdict.iteritems():
            print name
            self.split_tree(cols, reset=True)
            self.to_excel(workbook, name, closeit=False)

        workbook.close()

    def to_text(self, file_name):
        """ Dumps pretty printed tree to <file_name>.txt"""
        with open(file_name, mode='w') as fi:
            fi.write("Structured as 'leaf details (Number records, Marginal Share, Overall Share)'")
            self.root._tofile(fi)

    def to_png(self, output_path):
        """ Uses graphviz to make a graph picture
        output_path := .png for the output"""
        graph = pydot.Dot(graph_type='graph')
        edges = self.root._visualize()
        for e in edges:
            graph.add_edge(e)
        graph.write(output_path)
