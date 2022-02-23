#!/usr/bin/env python
# coding: utf-8

# # CODI Prevelance Query (PQ) Results Visualization
# 
# 
# ## Background - PQ algorithm
# 
# [CODI-PQ](https://github.com/NORC-UChicago/CODI-PQ) is a program for weight-status-category prevalence based on BMI, and results can be stratified by age, sex, race and geography. PQViz can support the simple output of both PQ (Youth and Teens) and APQ (Adults). This notebook supports outputs from CODI-PQ run individually with no conditions.
# 
# ## PQViz Purpose
# 
# This tool allows researchers to conduct post-processing and data visualization of CODI-PQ output. It is intended to be used **after** a data set has been processed with CODI-PQ.
# 
# PQViz is a [Jupyter Notebook](https://jupyter.org/). It provides an environment that includes graphical user interfaces as well as interactive software development to explore data. To achieve this, PQViz uses different software languages and packages:
# 
#   * The [Python programming language](https://www.python.org/) is used to import, transform, visualize and analyze the output of growthcleanr. Some of the code for the tool is directly included in this notebook. Other functions have been placed in external files to minimize the amount of code that users see in order to let them focus on the actual data.
#   
#   * Data analysis is performed using [NumPy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/). The output of PQViz will be loaded into a [Pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html). It is expected that users will create views into or copies of the DataFrames built initially by this tool. Adding columns to the DataFrames created by this tool is unlikely to cause problems. Removing columns is likely to break some of the tool's functionality.
#    
#   * Visualization in the tool is provided by [Matplotlib](https://matplotlib.org/) and [Seaborn](http://seaborn.pydata.org/). Users may generate their own charts with these utilities.
#   
#   * Mapping support is provided by [GeoPandas](https://geopandas.org/en/stable/) and [ipyleaflet](https://ipyleaflet.readthedocs.io/en/latest/).

# # Setting Up the Environment
# 
# Jupyter Notebooks have documentation cells, such as this one, and code cells, like the one below. The notebook server runs any code cells and provides results back in the notebook. The following code cell loads the libraries necessary for the tool to work. If you would like to incorporate other Python libraries to assist in data exploration, they can be added here. Removing libraries from this cell will very likely break the tool.

# In[ ]:


from pathlib import Path
import warnings

from ipywidgets import fixed, interact, interactive, interact_manual
import ipywidgets as widgets
from IPython.display import display, HTML
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
import us


# The next two code cells tell the notebook server to automatically reload the externally defined Python functions created to assist in data analysis.

# In[ ]:


get_ipython().magic('load_ext autoreload')


# In[ ]:


get_ipython().magic('autoreload 2')


# This code cell instructs the notebook to automatically display plots inline.

# In[ ]:


get_ipython().magic('matplotlib inline')


# This code cell tells the notebook to output plots for high DPI displays, such as 4K monitors, many smartphones or a retina display on Apple hardware. This cell does not need to be run and can be safely removed. If removed, charts will look more "blocky" or "pixelated" on high DPI displays.

# In[ ]:


get_ipython().magic("config InlineBackend.figure_format = 'retina'")


# The following cell configures the look and feel of PQViz charts and data views for clarity. It also sets the visual palette to use a set of color-blind hues, and includes the District of Columbia in the list of state boundaries for map rendering.

# In[ ]:


warnings.filterwarnings('ignore')
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_rows', 500)
dpi = 300
mpl.rcParams['figure.dpi']= dpi
sns.set_style('white')
sns.set_palette("colorblind")
current_palette = sns.color_palette()
sns.set_context("notebook")
if us.states.DC not in us.STATES:
    us.STATES.append(us.states.DC)


# ## Loading Data
# 
# This code cell imports functions created for the tool to assist in data analysis. Some of the functions generate charts used in this tool. The chart code may be modified to change the appearance of plots without too much risk of breaking things. Other functions transform DataFrames and changing those will very likely cause things to break. If you are unable to tell the difference in the functions by looking at the code, it is probably best to leave them unmodified.

# In[ ]:


from pqviz import check_suppressed
from pqviz import create_dataframes
from pqviz import maps
from pqviz import plots


# The following cell defines the folder location of your CODI-PQ outputs. To organize results, use different folders for each of the different parameters to compare. For example, to compare prevalence values by race, group the different CODI-PQ results files created into its own folder. Then specify that folder here, in the next cell. To look at a different comparison using another parameter, group those results in another folder, then change the cell below to point to that second folder and re-run all the cells below this one.
# 
# By default, PQViz includes sample synthetic data for testing and verification. To review your own data, fill in the path in below with the location of your folder of CODI-PQ results.

# In[ ]:


results_folder = Path("./sample_data/zcta3/")


# ### Specify Data Details
# 
# The cell below sets up options which let you specify details about the CODI-PQ result files in the folder you specified above. When it runs, you should see a set of menus to choose from: 
# 
# * Select the demographic across which you are comparing. The demographic is set to `sex` as the default, but you can choose a different one from the drop down. The options are `sex`, `race`, `state`, `zcta3`, and `age`. 
# 
# * Select the State you are analyzing. 
# 
# * Select whether this is Pediatric or Adult data.

# In[ ]:


# Taken from https://stackoverflow.com/questions/31517194/how-to-hide-one-specific-cell-input-or-output-in-ipython-notebook
tag = HTML('''<script>
code_show=true; 
function code_toggle() {
    if (code_show){
        $('div.cell.code_cell.rendered.selected div.input').hide();
    } else {
        $('div.cell.code_cell.rendered.selected div.input').show();
    }
    code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
To show/hide this cell's raw code input, click <a href="javascript:code_toggle()">here</a>.''')
display(tag)

style = dict(description_width="150px")
demographic_type = "zcta3"
demo_drop_down = widgets.Dropdown(options=["sex", "race", "age", "zcta3"],
                                  value=demographic_type,
                                  description="Demographic Type:",
                                  disabled=False,
                                  style=style)

def dropdown_handler_demo(change):
    global demographic_type
    demographic_type = change.new  
    return demographic_type

demo_drop_down.observe(dropdown_handler_demo, names="value")

selected_state = "NC"
state_options = sorted([(s.name, s.abbr) for s in us.STATES])
state_drop_down = widgets.Dropdown(options=state_options,
                                   value=selected_state,
                                   description="State:",
                                   disabled=False,
                                   style=style)

def dropdown_handler_state(change):
    global selected_state
    selected_state = change.new  
    return selected_state

state_drop_down.observe(dropdown_handler_state,
                  names='value')

population_group = "Pediatric"
pop_group_drop_down = widgets.Dropdown(options=["Pediatric", "Adult"],
                                       description="Population Group:",
                                       disabled=False,
                                       style=style)

def dropdown_handler_pop_group(change):
    global population_group
    population_group = change.new  
    return population_group

pop_group_drop_down.observe(dropdown_handler_pop_group, names="value")

display(demo_drop_down)
display(state_drop_down)
display(pop_group_drop_down)


# The next cell will confirm the demographic options you selected.

# In[ ]:


print(f"Demographic Type: {demographic_type}")
print(f"State: {selected_state}")
print(f"Population Group: {population_group}")


# ### Transforming the data
# 
# The following cells prepare data for analysis based on the data location and options you selected.

# In[ ]:


prev_data = create_dataframes.create_prevalence_df(file_path=results_folder,
                                                   population_group=population_group)


# In[ ]:


pop_data = create_dataframes.create_population_df(results_folder, population_group)


# ## Suppressed Data
# 
# 
# As indicated in the CODI PQ [implementation guide](https://github.com/NORC-UChicago/CODI-PQ) (see section __Section A.9__), the query will automatically suppress data if any of these factors have been met:
# 
# * Sample size is less than 30
# * Absolute confidence interval width greater than or equal to 0.30
# * Absolute confidence interval width is between 0.05 and 0.30 and the relative confidence interval width is more than 130%
# 
# The implementation guide also highlights:
# 
# > "The Presentation Standards also provide guidance for identifying results for statistical review, CODI-PQ does not identify records for statistical review and leave this step for the user."
# 
# It is up to each researcher to decide which results to share and how best to do so. To highlight whether data has been suppressed by CODI-PQ, in this section PQViz provides an overview of any data that has been suppressed. The table below shows all the full count of suppressed data within each weight category. Each section below also details the missing values for that prevalence type. If there are no suppressed values in your dataset, you should see the message _"There are no suppressed values for this demographic level"_.

# In[ ]:


check_suppressed.check_suppressed(prev_data, "state")


# ## Sample and Population

# In this section, we plot the population size of these groups from PQ. 
# 
# The CODI PQ [implementation guide](https://github.com/NORC-UChicago/CODI-PQ) (see __Section F.1__) explains:
# 
# * Population: The weighted (or adjusted) count of the study population. It uses the American Community Survey.
# * Sample: The observed (or unadjusted, or crude) count of youth and teens in the study population. This is reflects the data given to CODI-PQ.
# 
# Below, select demographic type as well as whether or not to look at the population or the sample. A plot of the numbers for each BMI Category should display, and will update whenever different options are selected.

# In[ ]:


demo_dropdown_options = pop_data[demographic_type].unique()
pop_type_drowdown_options = pop_data["Population type"].unique()
style = dict(description_width="100px")
interact(plots.plot_pop,
         sam_type=widgets.Dropdown(options=pop_type_drowdown_options, 
                                   description="Sample Type:"),
         selected_demo=widgets.Dropdown(options=demo_dropdown_options, 
                                        description= "{}:".format(str.capitalize(demographic_type))), 
         demographic_type=fixed(demographic_type),
         population_group=fixed(population_group),
         df=fixed(pop_data));


# ## Plotting Prevalence

# In this section we plot the prevalance values in CODI-PQ results.
# 
# Below, select demographic type as well as whether to look at the population or the sample. A plot of the numbers for each BMI Category should appear, and should update with any further changes to the selected options.
# 
# The CODI PQ [implementation guide](https://github.com/NORC-UChicago/CODI-PQ) (see __Section F.1__) describes each prevalence type as:
# 
# * **Crude Prevalence**: The observed (or unadjusted, or crude) prevalence in the study population.
# * **Weighted Prevalence**: Prevalence based on weighted counts. A sample weight is assigned to each sample patient. It is a measure of the number of youth and teens or adults in the population represented by that sample patient. See implementation guide, Appendix A. Sample Weights for more information.
# * **Age-Adjusted Prevalence**: Prevalence based on weighted, age-adjusted counts. See implementation guide, Appendix A. Age Adjustment for more information.
# 
# The standard error for each prevalence is calculated with the CODI-PQ and is plotted with error bars. 

# In[ ]:


demo_dropdown_options = prev_data[demographic_type].unique()
prev_type_drowdown_options = prev_data["Prevalence type"].unique()
style = dict(description_width="100px")
interact(plots.plot_prevalence, 
         selected_demo=widgets.Dropdown(
             options=demo_dropdown_options,
             description="{}:".format(str.capitalize(demographic_type)),
             style=style), 
         prevalence_type = widgets.Dropdown(
             options=prev_type_drowdown_options, 
             description="Prevalence Type: ",
             style=style),
         demographic_type=fixed(demographic_type),
         population_group=fixed(population_group),
         df=fixed(prev_data));


# ## Crude prevalence measures from CDC PLACES
# 
# The [CDC PLACES](https://www.cdc.gov/places/index.html) data can provide context to analysis of local data such as the output of CODI-PQ. It provides "model-based population-level analysis and community estimates" of many health indicators, including Obesity.
# 
# The [PLACES data set](https://chronicdata.cdc.gov/500-Cities-Places/PLACES-ZCTA-Data-GIS-Friendly-Format-2020-release/bdsk-unrd) provides crude prevalence estimates along with estimated confidence intervals for dozens of indicators, taken from adult (18 years old or older) subjects. Because of this, its value here is for background and developeing a broader picture of the health of the region, rather than direct comparison. This is especially true if you are assessing pediatric data.
# 
# The PLACES data set is bundled with PQViz for convenience. The map below will show crude prevalence measures from PLACES for the state you selected above.

# In[ ]:


measure_options = sorted([n for n, c, d in maps.PLACES_MEASURES])
mdd = widgets.Dropdown(options=measure_options,
                       description="PLACES Measure:",
                       disabled=False,
                       style={"description_width": "165px"})
interact(maps.choropleth_map_places, selected_state=fixed(selected_state), selected_measure=mdd);


# The map should zoom to your state when it loads. Click on any ZCTA shown to see its crude prevalence value, which will appear under the map.

# ## Prevalence by Location
# 
# If you are looking at CODI-PQ results grouped by ZCTA, the map call below should show your data by ZCTA.
# 
# Note that the map below will show values grouped at the ZCTA3 level, rather than the finer-grained ZCTA5 level shown in the CDC PLACES data in the map directly above.
# 
# Areas of the map filled with light grey represent ZCTA3 areas without values present in the data. Areas filled with  dark grey represent ZCTA3 areas with suppressed data.

# In[ ]:


category_options = sorted(prev_data['Weight Category'].unique())
category_dropdown = widgets.Dropdown(options=category_options,
                                     description="Weight Category:",
                                     disabled=False,
                                     style={"description_width": "165px"})
prevalence_type_dropdown = widgets.Dropdown(options=prev_type_drowdown_options,
                                           description="Prevalence Type:",
                                           disabled=False,
                                           style={"description_width": "165px"})
interact(maps.choropleth_map_pq, 
         selected_state=fixed(selected_state), 
         df=fixed(prev_data),
         category=category_dropdown,
         prevalence_type=prevalence_type_dropdown);

