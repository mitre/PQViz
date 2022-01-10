import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import glob
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from pathlib import Path
import matplotlib.ticker as mticker
import os
import warnings
from textwrap import wrap


def plot_pop(df, selected_demo, sam_type, demographic_type, population_group):
    """
    Creates a horizontal bar plot that plots the counts of the perscribed sample type by BMI category

    Parameters:
    df: Data frame created using create_population_df() function
    selected_demo: selected subsected demographic from dropdown. Options will change depending on demographic type.
    sam_type: type of population, selected from dropdown, expected Values ['Population', 'Sample']
    demographic_type: Demographic that they are comparing, select from dropdown earlier in notebook, expected values ['sex', 'race', 'age']
    population_group: Type of population, expected inputs ['Pediatric', 'Adult']

    Returns:
    A horizontal bar plot that plots the counts of the perscribed sample type by BMI category."""
    if population_group == "Pediatric":
        plt.figure(figsize=(10, 8))
        selected_demo_mask = df[demographic_type] == selected_demo
        prev_type_mask = df["Population type"] == sam_type
        subsected_df = df[selected_demo_mask & prev_type_mask]
        subsected_df["Population"] = subsected_df["Population"].fillna(0)
        ax = sns.barplot(
            data=subsected_df, y="Weight Category", x="Population", ci=None
        )
        max_x = max(subsected_df["Population"])
        plt.xlim(left=0, right=max_x + max_x / 10)  # set the xlim to left, right
        for p in ax.patches:
            width = p.get_width()  # get bar length
            if width == 0:
                ax.text(
                    width + max_x / 2.3,
                    p.get_y()
                    + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                    "Suppressed Data",  # set Name to ad
                    ha="left",  # horizontal alignment
                    va="center",  # vertical alignment
                    size=16,
                )  # font size
            else:
                ax.text(
                    width + 1,  # set the text at 1 unit right of the bar
                    p.get_y()
                    + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                    "{:,.0f}".format(width),  # set variable to display, 2 decimals
                    ha="left",  # horizontal alignment
                    va="center",
                )  # vertical alignment
        # after plotting the data, format the labels
        label_format = "{:,.0f}"
        ax.xaxis.set_major_locator(mticker.MaxNLocator(3))
        ticks_loc = ax.get_xticks().tolist()
        ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        ax.set_xticklabels([label_format.format(x) for x in ticks_loc])
        # plt.savefig(path + '{}'.format(Type) + "_{}".format(Race)+".png")
        state = list(subsected_df["state"])[0]
        plt.title(
            "{}".format(sam_type)
            + " Size by BMI Category for \n{}".format(selected_demo)
            + " {} Data".format(population_group)
            + " in {}".format(state),
            fontsize=20,
            pad=20,
        )
        plt.xlabel("{}".format(sam_type), fontsize=16)
        # subsected_df['Weight Category'] = ['\n'.join(wrap(x, 12)) for x in  subsected_df['Weight Category']]
        peds_labels = [
            "(1) Underweight \n(<5th percentile)",
            "(2) Healthy Weight \n(5th to <85th percentile)",
            "(3) Overweight \n(85th to <95th percentile)",
            "(4) Obesity \n(>95th percentile)",
            "(4b) Severe Obesity \n(>120% of the 95th percentile)",
        ]
        ax.yaxis.set_ticklabels(peds_labels)
        plt.ylabel("BMI Category", fontsize=16)
        plt.show()
    elif population_group == "Adult":
        plt.figure(figsize=(10, 8))
        selected_demo_mask = df[demographic_type] == selected_demo
        sample_type_mask = df["Population type"] == sam_type
        summary_mask = df["Weight Category"] != "(4) Obesity (Classes 1, 2, and 3) (BMI 30+)"
        subsected_df = df[selected_demo_mask & sample_type_mask & summary_mask]
        subsected_df["Population"] = subsected_df["Population"].fillna(0)
        ax = sns.barplot(
            data=subsected_df, y="Weight Category", x="Population", ci=None
        )
        max_x = max(subsected_df["Population"])
        plt.xlim(left=0, right=max_x + max_x / 10)  # set the xlim to left, right
        for p in ax.patches:
            width = p.get_width()  # get bar length
            if width == 0:
                ax.text(
                    width + max_x / 2.3,
                    p.get_y()
                    + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                    "Suppressed Data",  # set Name to ad
                    ha="left",  # horizontal alignment
                    va="center",  # vertical alignment
                    size=16,
                )  # font size
            else:
                ax.text(
                    width + 1,  # set the text at 1 unit right of the bar
                    p.get_y()
                    + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                    "{:,.0f}".format(width),  # set variable to display, 2 decimals
                    ha="left",  # horizontal alignment
                    va="center",
                )  # vertical alignment
        # after plotting the data, format the labels
        label_format = "{:,.0f}"
        ax.xaxis.set_major_locator(mticker.MaxNLocator(3))
        ticks_loc = ax.get_xticks().tolist()
        ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        ax.set_xticklabels([label_format.format(x) for x in ticks_loc])
        # plt.savefig(path + '{}'.format(Type) + "_{}".format(Race)+".png")
        state = list(subsected_df["state"])[0]
        plt.title(
            "{}".format(sam_type)
            + " Size by BMI Category for \n{}".format(selected_demo)
            + " {}".format(population_group)
            + " Data"
            + " in {}".format(state),
            fontsize=20,
            pad=20,
        )
        plt.xlabel("{}".format(sam_type), fontsize=16)
        # subsected_df['Weight Category'] = ['\n'.join(wrap(x, 12)) for x in  subsected_df['Weight Category']]
        adult_labels = [
            "(1) Underweight \n(BMI<18.5)",
            "(2) Healthy Weight \n(18.5<=BMI<25)",
            "(3) Overweight \n(25<=BMI<30)",
            "(4a) Obesity (Class 1) \n(30<=BMI<35)",
            "(4b) Obesity (Class 2) \n(35<=BMI<40)",
            "(4c) Obesity (Class 3) - Severe Obesity \n(BMI 40+)",
        ]

        ax.yaxis.set_ticklabels(adult_labels)
        plt.ylabel("BMI Category", fontsize=16)
        plt.show()


def plot_prevalence(df, selected_demo, prevalence_type, demographic_type, population_group):
    """
    Creates a horizontal bar plot that plots the prevelance of the perscribed sample type by BMI category

    Parameters:
    df: Data frame created using create_population_df() function
    selected_demo: selected subsected demographic from dropdown. Options will change depending on demographic type.
    prevalence_type: type of prevalence, selected from dropdown, expected Values ['Crude', 'Age-Adjusted', 'Weighted']
    demographic_type: Demographic that they are comparing, select from dropdown earlier in notebook, expected values ['sex', 'race', 'age']
    population_group: Type of population, expected inputs ['Pediatric', 'Adult']

    Returns:
    A horizontal bar plot that plots the perevalence of the perscribed sample type by BMI category with the
    standard error calculated with CODI-PQ represented by error bars. """


    if population_group == "Pediatric":
        plt.figure(figsize=(10, 8))
        selected_demo_mask = (df[demographic_type] == selected_demo)
        prev_type_mask = df["Prevalence type"] == prevalence_type
        subsected_df = df[selected_demo_mask & prev_type_mask]
        subsected_df = subsected_df.fillna(0)
        subsected_df["Prevalence"] = pd.to_numeric(subsected_df["Prevalence"])
        subsected_df["Standard Error"] = pd.to_numeric(subsected_df["Standard Error"])
        ax = sns.barplot(data=subsected_df, y="Weight Category", x="Prevalence", ci=None)
        max_x = max(subsected_df["Prevalence"])
        plt.xlim(left=0, right=max_x + max_x / 10)  # set the xlim to left, right
        for p in ax.patches:
            width = p.get_width()  # get bar length
            if width == 0:
                ax.text(
                    width + max_x / 2.3,
                    p.get_y() + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                    "Suppressed Data",  # set Name to ad
                    ha="left",  # horizontal alignment
                    va="center",  # vertical alignment
                    size=16,
                )  # font size
        ax.errorbar(
            y=subsected_df["Weight Category"],
            x=subsected_df["Prevalence"],
            xerr=subsected_df["Standard Error"],
            linewidth=1.5,
            color="black",
            alpha=0.4,
            capsize=8,
            ls="none",
            capthick = 2
        )
        label_format = "{:,.0f}"

        ax.xaxis.set_major_locator(mticker.MaxNLocator(3))
        ticks_loc = ax.get_xticks().tolist()
        ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        ax.set_xticklabels([label_format.format(x) for x in ticks_loc])
        state = subsected_df["state"].unique()[0]
        plt.title(
            "BMI Category {}".format(prevalence_type)
            + "\n Prevalence for {}".format(selected_demo)
            + " {}".format(population_group)
            + " Data"
            + " in {}".format(state),
            fontsize=14,
            pad=20,
        )
        plt.xlabel("Prevalence", fontsize=16)
        # subsected_df['BMI Category'] = ['\n'.join(wrap(x, 12)) for x in  subsected_df['BMI Category']]
        plt.ylabel("BMI Category", fontsize=16)
        peds_labels = [
            "(1) Underweight \n(<5th percentile)",
            "(2) Healthy Weight \n(5th to <85th percentile)",
            "(3) Overweight \n(85th to <95th percentile)",
            "(4) Obesity \n(>95th percentile)",
            "(4b) Severe Obesity \n(>120% of the 95th percentile)",
        ]
        ax.yaxis.set_ticklabels(peds_labels)
        plt.show()
    elif population_group == 'Adult':
            plt.figure(figsize=(10, 8))
            selected_demo_mask = df[demographic_type] == selected_demo
            prev_type_mask = df["Prevalence type"] == prevalence_type
            summary_mask = df["Weight Category"] != "(4) Obesity (Classes 1, 2, and 3) (BMI 30+)"
            subsected_df = df[selected_demo_mask & prev_type_mask & summary_mask]
            subsected_df = subsected_df.fillna(0)
            subsected_df["Prevalence"] = pd.to_numeric(subsected_df["Prevalence"])
            subsected_df["Standard Error"] = pd.to_numeric(subsected_df["Standard Error"])
            ax = sns.barplot(data=subsected_df, y="Weight Category", x="Prevalence", ci=None)
            max_x = max(subsected_df["Prevalence"])
            plt.xlim(left=0, right=max_x + max_x / 10)  # set the xlim to left, right
            for p in ax.patches:
                width = p.get_width()  # get bar length
                if width == 0:
                    ax.text(
                        width + max_x / 2.3,
                        p.get_y() + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                        "Suppressed Data",  # set Name to ad
                        ha="left",  # horizontal alignment
                        va="center",  # vertical alignment
                        size=16,
                    )  # font size
            ax.errorbar(
                y=subsected_df["Weight Category"],
                x=subsected_df["Prevalence"],
                xerr=subsected_df["Standard Error"],
                linewidth=1.5,
                color="black",
                alpha=0.4,
                capsize=8,
                ls="none",
                capthick = 2
            )
            label_format = "{:,.0f}"

            ax.xaxis.set_major_locator(mticker.MaxNLocator(3))
            ticks_loc = ax.get_xticks().tolist()
            ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
            ax.set_xticklabels([label_format.format(x) for x in ticks_loc])
            state = subsected_df["state"].unique()[0]
            plt.title(
                "BMI Category {}".format(prevalence_type)
                + "\n Prevalence for {}".format(selected_demo)
                + " {}".format(population_group)
                + " Data"
                + " in {}".format(state),
                fontsize=14,
                pad=20,
            )
            plt.xlabel("Prevalence", fontsize=16)
            # subsected_df['BMI Category'] = ['\n'.join(wrap(x, 12)) for x in  subsected_df['BMI Category']]
            plt.ylabel("BMI Category", fontsize=16)
            adult_labels = [
                "(1) Underweight \n(BMI<18.5)",
                "(2) Healthy Weight \n(18.5<=BMI<25)",
                "(3) Overweight \n(25<=BMI<30)",
                "(4a) Obesity (Class 1) \n(30<=BMI<35)",
                "(4b) Obesity (Class 2) \n(35<=BMI<40)",
                "(4c) Obesity (Class 3) - Severe Obesity \n(BMI 40+)",
            ]

            ax.yaxis.set_ticklabels(adult_labels)
            # plt.savefig(path + '{}'.format(prevalence_type) + "_{}".format(selected_demo)+".png")
            plt.show()
