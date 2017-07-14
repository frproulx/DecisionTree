# DecisionTree
This is a simple little tool for generating manually determined decision trees from data in a pandas dataframe.

Specifically, the goal is to be able to feed in a dataframe, a list of columns you want splits (and cut points if they're categorical), and to get back the number of records, marginal shares, and overall shares in each of the nodes in a usable format (e.g. in a graphic and/or a spreadsheet).

The trees are generated recursively.
