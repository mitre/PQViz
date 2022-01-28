import glob
from pathlib import Path

from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def check_suppressed(df, attribute):
    suppressed_values = df.groupby(["Weight Category", attribute])
    suppressed_values = suppressed_values.count().rsub(suppressed_values.size(), axis=0)
    suppressed_values = suppressed_values[
        suppressed_values["Prevalence"] > 0
    ].reset_index()
    if suppressed_values.empty:
        print("There are no suppressed values for this demographic level.")
    else:
        kept_cols = ["Weight Category", attribute, "Prevalence"]
        suppressed_values = suppressed_values.loc[:, kept_cols].copy()
        suppressed_values = suppressed_values.rename(
            columns={"Prevalence": "Number of subpopulations with suppressed values"}
        )
        return suppressed_values


def suppressed_zcta3(df, category, prevalence_type):
    """
    Return an array of suppressed ZCTA3 values for the specified category and
    prevalence type suppressed zcta3s.

    Parameters:
    df: DataFrame of prevalence data
    category: Weight category/class
    prevalence_type: Prevalence type, one of ['Age-Adjusted', 'Crude', 'Weighted']

    Returns:
    A numpy array of ZCTA3s with suppressed prevalence values.
    """
    return df.loc[
        (df["Weight Category"] == category)
        & (df["Prevalence type"] == prevalence_type)
        & (df["Prevalence"].isna())
    ]["zcta3"].values.tolist()
