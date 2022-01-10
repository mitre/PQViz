from pathlib import Path

from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import us


def create_prevalence_df(file_path, population_group):
    """
    Creates a data frame that includes the prevalences and the demographic data

    Parameters:
    file_path: A folder with pq outputs to compare
    population_group: Type of population, expected inputs ['Pediatric', 'Adult']

    Returns:
    A DataFrame where the rows are distinct demographic and prevalence numbers."""

    # create a list of al the csvs in path
    all_files = list(file_path.glob("**/*"))
    # import census location data
    # define an emptylist to create df from
    all_df = []
    # import files
    if population_group == "Pediatric":
        for filename in all_files:
            print(f"Reading {filename}")
            # read in csv

            # Adding error-catching loop with output note for debugging
            try:
                df = pd.read_csv(filename, index_col=None, header=0)
                sex = (
                    df[df["Order"] == 6]["Weight Category"]
                    .str.extract("\(([^)]+)\)", expand=True)
                    .reset_index()
                    .at[0, 0]
                )
            except Exception as e:
                print(f"File {filename} has no data, skipping")
                continue

            # read in sex as outputed from pq
            sex = (
                df[df["Order"] == 6]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )

            df["sex"] = sex

            # read in race as outputed from pq
            race = (
                df[df["Order"] == 7]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["race"] = race

            # read in location code as outputed from pq
            location_code = (
                df[df["Order"] == 10]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # identify state
            if len(location_code) == 2:
                state_cd = location_code
                df["zcta3"] = np.nan

            else:
                zcta3 = []
                states = []
                for loc in [l.strip() for l in location_code.split(",")]:
                    zcta3.append(loc[2:])
                    states.append(loc[:2])
                df["zcta3"] = ",".join(zcta3)
                states = list(set(states))
                state_cd = ",".join(states)

            state = us.states.lookup(state_cd)
            df["state"] = state
            # read in age as outputed from pq
            age = (
                df[df["Order"] == 5]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # converting to list
            df["age"] = age
            df["filename"] = filename
            year = (
                df[df["Order"] == 11]["Weight Category"]
                .str.extract(":(.*)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["year"] = year

            # add dataframe to list
            all_df.append(df)
    if population_group == "Adult":
        for filename in all_files:
            print(f"Reading {filename}")
            # read in csv

            # Adding error-catching loop with output note for debugging
            try:
                df = pd.read_csv(filename, index_col=None, header=0)
                sex = (
                    df[df["Order"] == 6]["Weight Category"]
                    .str.extract("\(([^)]+)\)", expand=True)
                    .reset_index()
                    .at[0, 0]
                )
            except Exception as e:
                print(f"File {filename} has no data, skipping")
                continue

            # read in sex as outputed from pq
            sex = (
                df[df["Order"] == 6]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )

            df["sex"] = sex

            # read in race as outputed from pq
            race = (
                df[df["Order"] == 8]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["race"] = race

            # read in location code as outputed from pq
            location_code = (
                df[df["Order"] == 11]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # identify state
            if len(location_code) == 2:
                state_cd = location_code
                df["zcta3"] = np.nan

            else:
                zcta3 = []
                states = []
                for loc in [l.strip() for l in location_code.split(",")]:
                    zcta3.append(loc[2:])
                    states.append(loc[:2])
                df["zcta3"] = ",".join(zcta3)
                states = list(set(states))
                state_cd = ",".join(states)

            state = us.states.lookup(state_cd)
            df["state"] = state
            # read in age as outputed from pq
            age = (
                df[df["Order"] == 5]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # converting to list
            df["age"] = age
            df["filename"] = filename

            year = (
                df[df["Order"] == 12]["Weight Category"]
                .str.extract(":(.*)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["year"] = year
            # add dataframe to list
            all_df.append(df)
    all_df = pd.concat(all_df, axis=0, ignore_index=True, sort=True)
    all_data = all_df[all_df["Order"] == 1].drop(columns="Order")
    std_data = all_data.drop(
        columns=[
            "Crude Prevalence",
            "Weighted Prevalence",
            "Age-Adjusted Prevalence",
            "Sample",
            "Population",
        ]
    )

    prev_data = all_data.drop(
        columns=[
            "Crude Prevalence Standard Error",
            "Weighted Prevalence Standard Error",
            "Age-Adjusted Prevalence Standard Error",
            "Sample",
            "Population",
        ]
    )
    prev_data_melt = prev_data.melt(
        id_vars=[
            "Weight Category",
            "sex",
            "race",
            "state",
            "zcta3",
            "age",
            "filename",
            "year",
        ],
        value_name="Prevalence",
        var_name="Prevalence type",
    )
    std_melt = std_data.melt(
        id_vars=[
            "Weight Category",
            "sex",
            "race",
            "state",
            "zcta3",
            "age",
            "filename",
            "year",
        ],
        value_name="Standard Error",
        var_name="Prevalence type",
    )
    prev_data_melt["Prevalence type"] = prev_data_melt["Prevalence type"].str.split(
        expand=True
    )[0]
    std_melt["Prevalence type"] = std_melt["Prevalence type"].str.split(expand=True)[0]
    output_name = prev_data_melt.merge(
        std_melt,
        on=[
            "Weight Category",
            "sex",
            "race",
            "state",
            "zcta3",
            "age",
            "filename",
            "year",
            "Prevalence type",
        ],
        how="left",
    )

    output_name["Prevalence"] = output_name["Prevalence"].replace({".": np.NAN})
    output_name["Standard Error"] = output_name["Standard Error"].replace({".": np.NAN})
    return output_name


def create_population_df(file_path, population_group):
    """creates a data frame that includes the population numbers and the demographic data.
    Population numbers come from American Community Survey

    Parameters:
    file_path: A folder with pq outputs to compare
    population_group: Type of population, expected inputs ['Pediatric', 'Adult']

    Returns:
    A DataFrame where the rows are distinct demographic and prevalence numbers."""
    # create a list of al the csvs in path
    all_files = list(file_path.glob("**/*"))

    # define an emptylist to create df from
    all_df = []
    # import files
    if population_group == "Pediatric":
        for filename in all_files:
            print(f"Reading {filename}")
            # read in csv

            # Adding error-catching loop with output note for debugging
            try:
                df = pd.read_csv(filename, index_col=None, header=0)
                sex = (
                    df[df["Order"] == 6]["Weight Category"]
                    .str.extract("\(([^)]+)\)", expand=True)
                    .reset_index()
                    .at[0, 0]
                )
            except Exception as e:
                print(f"File {filename} has no data, skipping")
                continue

            # read in sex as outputed from pq
            sex = (
                df[df["Order"] == 6]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )

            df["sex"] = sex

            # read in race as outputed from pq
            race = (
                df[df["Order"] == 7]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["race"] = race

            # read in location code as outputed from pq
            location_code = (
                df[df["Order"] == 10]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # identify state
            if len(location_code) == 2:
                state_cd = location_code
                df["zcta3"] = np.nan

            else:
                zcta3 = []
                states = []
                for loc in [l.strip() for l in location_code.split(",")]:
                    zcta3.append(loc[2:])
                    states.append(loc[:2])
                df["zcta3"] = ",".join(zcta3)
                states = list(set(states))
                state_cd = ",".join(states)

            state = us.states.lookup(state_cd)
            df["state"] = state
            # read in age as outputed from pq
            age = (
                df[df["Order"] == 5]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # converting to list
            df["age"] = age
            df["filename"] = filename
            year = (
                df[df["Order"] == 11]["Weight Category"]
                .str.extract(":(.*)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["year"] = year

            # add dataframe to list
            all_df.append(df)
    if population_group == "Adult":
        for filename in all_files:
            print(f"Reading {filename}")
            # read in csv

            # Adding error-catching loop with output note for debugging
            try:
                df = pd.read_csv(filename, index_col=None, header=0)
                sex = (
                    df[df["Order"] == 6]["Weight Category"]
                    .str.extract("\(([^)]+)\)", expand=True)
                    .reset_index()
                    .at[0, 0]
                )
            except Exception as e:
                print(f"File {filename} has no data, skipping")
                continue

            # read in sex as outputed from pq
            sex = (
                df[df["Order"] == 6]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )

            df["sex"] = sex

            # read in race as outputed from pq
            race = (
                df[df["Order"] == 8]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["race"] = race

            # read in location code as outputed from pq
            location_code = (
                df[df["Order"] == 11]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # identify state
            if len(location_code) == 2:
                state_cd = location_code
                df["zcta3"] = np.nan

            else:
                zcta3 = []
                states = []
                for loc in [l.strip() for l in location_code.split(",")]:
                    zcta3.append(loc[2:])
                    states.append(loc[:2])
                df["zcta3"] = ",".join(zcta3)
                states = list(set(states))
                state_cd = ",".join(states)
            state = us.states.lookup(state_cd)
            df["state"] = state
            # read in age as outputed from pq
            age = (
                df[df["Order"] == 5]["Weight Category"]
                .str.extract("\(([^)]+)\)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            # converting to list
            df["age"] = age
            df["filename"] = filename
            year = (
                df[df["Order"] == 12]["Weight Category"]
                .str.extract(":(.*)", expand=True)
                .reset_index()
                .at[0, 0]
            )
            df["year"] = year
            # add dataframe to list
            all_df.append(df)
    all_df = pd.concat(all_df, axis=0, ignore_index=True, sort=True)
    all_data = all_df[all_df["Order"] == 1].drop(columns="Order")

    pop_data = all_data.drop(
        columns=[
            "Crude Prevalence",
            "Weighted Prevalence",
            "Age-Adjusted Prevalence",
            "Crude Prevalence Standard Error",
            "Weighted Prevalence Standard Error",
            "Age-Adjusted Prevalence Standard Error",
        ]
    )
    output_name = pop_data.melt(
        id_vars=[
            "Weight Category",
            "sex",
            "race",
            "state",
            "zcta3",
            "age",
            "filename",
            "year",
        ],
        value_name="Population",
        var_name="Population type",
    )

    output_name["Population"] = output_name["Population"].replace({".": np.NAN})
    output_name["Population"] = (
        output_name["Population"].astype(str).str.replace(",", "").astype(float)
    )
    return output_name
