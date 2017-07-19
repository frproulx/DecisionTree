"""Utility functions for data prep."""
import pandas as pd
import jenkspy


def jenks_bin(x, k):
    """Jenks bin a pd.Series"""
    if type(x) is not pd.Series:
        raise TypeError()
    breaks = jenkspy.jenks_breaks(x, nb_class=k)
    return pd.cut(x, bins=breaks)
