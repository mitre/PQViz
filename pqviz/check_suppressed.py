import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import glob
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from pathlib import Path


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
