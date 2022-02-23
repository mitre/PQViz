# PQViz

PQViz was developed in partnership between the Health FFRDC and CDC to support
post-processing and data visualization output from the
[CODI Prevalence Query](https://github.com/NORC-UChicago/CODI-PQ) (CODI-PQ)
tools.

The objective of this tool is to allow users to conduct post-processing and data
visualization of CODI-PQ output. CODI-PQ is a statistical program developed to
generate weight-status-category prevalence based on BMI, which can be stratified
by age, sex, race and geography. PQViz can support the simple output of both PQ
(Youth and Teens) and APQ (Adults).

## Contents

- [Git Repository Information](#git-repository-information)
- [PQViz Purpose](#PQViz-purpose)
- [Background](#background)
- [Simple Install](#simple-install)
- [Sample data and first run testing](#sample-data-and-first-run-testing)
- [Support scripts for growthcleanr](#support-scripts-for-growthcleanr)

## Git Repository Information

The latest code for this project should run `PQViz.ipynb`.

The notebook requires Python 3, Jupyter Notebook, Pandas, Matplotlib, and
Seaborn. The `.csv` files in the repository are synthetic sample data used by
default in the notebook as a working example. Custom data should replace these
files in the same format. For more details, see
[the simple install instructions below.](#simple-install)

## PQViz Purpose

This tool allows users to conduct post-processing and data visualization of
[CODI-PQ](https://github.com/NORC-UChicago/CODI-PQ) output. CODI-PQ is a program
for weight-status-category prevalence based on BMI, which can be stratified by
age, sex, race and geography. PQViz can support the simple output of both PQ
(Youth and Teens) and APQ (Adults). This notebook supports outputs from CODI-PQ
run individually with no coniditons.

### Background

PQViz uses data sets that were developed with CODI-PQ. The tool expects the
output to be in an Excel format that is described in the notebook.

PQViz is a [Juypter Notebook](https://jupyter.org/). It provides an environment
that includes graphical user interfaces as well as interactive software
development to explore data. To achieve this, PQViz references different
software languages and packages:

- The [Python programming language](https://www.python.org/) is used to import,
  transform, visualize and analyze the output of CODI-PQ. Some of the code for
  the tool is directly included in this notebook. Other functions have been
  placed in an external file to minimize the amount of code that users see in
  order to let them focus on the actual data.

- Data analysis is performed using [NumPy](https://numpy.org/) and
  [Pandas](https://pandas.pydata.org/). The output of CODI-PQ will be loaded
  into a
  [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).
  PQViz provides functions for transforming DataFrames as well as supporting
  visualizations. It is expected that users will create views into or copies of
  the DataFrames built initially by this tool. Adding columns to the DataFrames
  created by this tool is unlikely to cause problems. Removing columns is likely
  to break some of the tool's functionality.

- Visualization in the tool is provided by [Matplotlib](https://matplotlib.org/)
  and [Seaborn](http://seaborn.pydata.org/). Users may generate their own charts
  with these utilities.

- Maps are provided by
  [ipyleaflet](https://ipyleaflet.readthedocs.io/en/latest/)

## Simple Install

If you are new to Jupyter and Python and use Windows, please use the
instructions below for installing with Anaconda on Windows. If you are familiar
with installing Python modules using `pip` on Linux or MacOS, please use the
instructions for Python and pip on Linux / MacOS.

### Anaconda on Windows

Anaconda is an all-in-one package installer for setting up dependencies needed
to run and view PQViz. This is recommended approach for Windows due to a number
of dependencies that need to be installed in the correct order.

1. Install Anaconda

   - Follow install instructions
     [found here for installation.](https://docs.anaconda.com/anaconda/install/)
   - Opt for the Python 3.9 version
   - The
     [windows install instructions](https://docs.anaconda.com/anaconda/install/windows/)
     are step-by-step and will get everything set up properly for the project.

1. Download the [PQViz project](https://github.com/mitre/PQViz) as a zip file
   using the "Clone or download" button on GitHub.

1. Unzip the PQViz zip file to have access to all of the source files for the
   Jupyter notebook.

1. Open "Anaconda Prompt" from the Windows start menu and run the following
   commands in the prompt window. Answer "Y" for Yes to each of the prompts.
   **Note**: one or more of these steps may take a long time (10 minutes or even
   much more) to complete. The `geopandas` step (#3) in particular can take a
   while. Please be patient and allow each step to complete.

```windows
conda create -n pqviz -c conda-forge us
conda activate pqviz
conda install python=3 geopandas
conda install -c anaconda seaborn
conda install jupyter
python -m ipykernel install --user --name=pqviz
conda install -c conda-forge branca
conda install -c conda-forge ipyleaflet
```

5. Run the Anaconda Navigator that was installed during Step 1 (go to Start >
   Anaconda Navigator). This may take a while to load.

6. Within the browser, navigate to the `PQViz-main` folder you downloaded and
   unzipped in Step 2 (likely found in your `Downloads` folder). Click on
   `PQViz.ipynb` to run the Python notebook.

7. **[Optional step for testing the notebook]** Once the notebook is open, click
   the 'Run' button to step through the various blocks (cells) of the document,
   OR click the 'Cell' dropdown in the menu bar and select 'Run all' to test the
   entire notebook all at once.

### Python and pip on Linux / MacOS

If you are not using Anaconda, specific versions of packages can be found in
`requirements.txt`, and can be installed with `pip install -r requirements.txt`.
It is best to use a
[virtual environment](https://docs.python.org/3/tutorial/venv.html) with a tool
such as the Python built-in `venv` for this project, but this is not required.
With the dependency packages installed, start the notebook from the command
line:

```bash
jupyter notebook
```

This should open a browser window; open `PQViz.ipynb` to start the notebook and
run the cells.

### Troubleshooting: maps not rendering

If the maps in the notebook do not render, it might be possible that you are
using an older version of the Jupyter notebook. See the
[ipyleaflet Installation Notes](https://github.com/jupyter-widgets/ipyleaflet#installation)
for older versions of Jupyter for details on how to enable this extension
manually.

## Sample data and first run testing

By default when you reach Step 6 of the [Simple Install](#simple-install)
instructions above the notebook will use sample data loaded from the `.csv`
files located in the PQViz project directory `sample_data`. The sample data is
the CODI-PQ output of example synthetic dataset created using
[Synthea](https://synthetichealth.github.io/synthea/). The data is North
Carolina pediatric data, and was processed with CODI-PQ for all sexes, for each
sex individually, and for individual ZIP Code Tabulation Areas (ZCTAs).

### Output boxes

When you run all cells (see Step 8 above) `Out[#]:` boxes will appear in the
notebook below the `In[#]:` code cells. This is common to Jupyter notebooks. The
outputs are the result of executing the functioning code blocks on the data. The
"Out" blocks will often be interactive charts and graphs used to explore the
CODI-PQ data. Descriptions of each `Out[#]:` block can be found in the text
sections above the `In[#]:` blocks.

## Additional notes

### Support scripts for growthcleanr

The directory `pq_support` contains R code that may assist in the workflow of
cleaning data with
[growthcleanr](https://github.com/carriedaymont/growthcleanr). These are not
required to use PQViz, but are provided as an example of a workflow
incorporating EHR data cleaning with the use of CODI-PQ.

- `growthcleanr_batching.R` provides example code for processing large sets of
  EHR data in growthcleanr using a batching strategy to improve performance
  (speed)
- `growthcleanr2pq.R` transforms growthcleanr output to prepare it for use with
  CODI-PQ, including selecting and classifying BMI values
- `bmi_selection.R` includes functions for selecting and classifying BMI values,
  and is used by `growthcleanr2pq.R`

See the `pq_support/README.md` file for additional details.

### Reference data

PQViz comes with several files of reference data from the
[U.S. Department of Health and Human Services](https://www.hhs.gov/) and the
[U.S. Census Bureau](https://www.census.gov/). See the file
`reference_data/README.md` for details on procuring and preparing these files.

## Notice

Copyright (c) 2021-2022 The MITRE Corporation.

Approved for Public Release; Distribution Unlimited. Case Number 19-2008
