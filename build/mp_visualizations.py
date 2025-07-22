#!/usr/bin/env python
# coding: utf-8

# ## Visualization script for multiplayer Type Through the Bible files
# 
# By Ken Burchfiel
# 
# Released under the MIT license
# 
# Note: this script, though developed as a Jupyter Notebook to make development and testing easier, is meant to be called as a Python file within a terminal/command prompt with a multiplayer test results file as its sole argument. Here's an example of what this function call may look like on Linux when the current directory is TTTB's build/ folder:
# 
#     python mp_visualizations.py 20250706T220148
# 
# Note that only the timestamp component of the multiplayer file(s) is passed to the argument; the function will take care of the rest. (This helps prevent user-submitted strings from getting passed to a system() call, which could potentially cause security issues.
# 
# When players complete multiplayer games within Type Through The Bible, this script will then get called via a system() call. However, it can also be run as a standalone file if needed.

# In[ ]:


import time
start_time = time.time()
import os
import pandas as pd
import numpy as np
import plotly.express as px
pd.set_option('display.max_columns', 1000)

# The following file paths are relative to the build folder.
mp_results_folder = '../Files/Multiplayer/'
mp_visualizations_folder = '../Visualizations/Multiplayer/'


# Checking whether this script is running within a Jupyter notebook: 
# 
# (This will allow us to determine whether to specify our multiplayer filename via argparse (which will only work when the .py version of the file is being rurn) or via a notebook-specific argument.

# In[ ]:


notebook_exec = False
try:
    get_ipython()
    notebook_exec = True # Script is running within a notebook
except:
#     print("get_ipython() failed, so we'll assume that we're running \
# this script within a .py file.")
    pass

# notebook_exec
    


# Adding code that will allow the caller to specify which multiplayer results file to analyze:
# 
# (Note that only the timestamp component of this file should be passed to the argument.)
# 
# If you're running this code within a notebook, update the test_results_timestamp value as needed.

# In[ ]:


if notebook_exec == False:
    # The following code was based on
    # https://docs.python.org/3/howto/argparse.html#argparse-tutorial
    # and # https://docs.python.org/3/library/argparse.html .
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("results_timestamp")
    args = parser.parse_args()
    test_results_timestamp = args.results_timestamp
else:
    test_results_timestamp = '20250722T010046'

test_results_timestamp


# Determining the multiplayer test_results.csv file whose timestamp matches our test_results_timestamp string:
# 
# (There *should* only be one such timestamp, but just in case two or more share this timestamp--which is extremely improbable--only one will be retained.)

# In[ ]:


test_results_file = [file for file in os.listdir(mp_results_folder) if 
 (test_results_timestamp in file) & ('test_results' in file)][0]
# Creating a shortened version of this string that doesn't have
# the 'test_results.csv' component at the end: 
# (This shortened version will serve as the initial component
# of our visualization filenames.)
test_results_name = test_results_file[:-17]
test_results_file, test_results_name


# In[ ]:


df = pd.read_csv(mp_results_folder+test_results_file) 
# Replacing the tag columns with their actual meanings:
df.rename(columns = {'Tag_1':'Round','Tag_2':'Test within round',
                    'Tag_3':'Player test number',
                    'Within_Session_Test_Number':
                    'Game test number'}, inplace = True)
# Making sure that the results are stored in the order that they were
# typed:
df.sort_values('Game test number', inplace = True)

# Calculating cumulative WPM values:
df['Cumulative WPM'] = (df.groupby('Player')['WPM'].transform(
'cumsum')) / df['Player test number']

df['Best_WPM_for_Test'] = df.groupby(
    'Player test number')['WPM'].transform('max')
df['Player had best WPM for this test'] = np.where(
    df['WPM'] == df['Best_WPM_for_Test'], 1, 0)

df.tail()


# Creating a melted verison of this DataFrame that stores both cumulative and test-specific WPM values within the same column:
# 
# (This will make it easier to produce a graph that uses different line dash types to differentiate between cumulative and test-specific WPM values.)

# In[ ]:


df_wpm_type_melt = df.melt(id_vars = ['Player', 'Player test number'],
value_vars = ['WPM', 'Cumulative WPM'],
var_name = 'WPM Type',
value_name = 'Words per minute').rename(
    columns = {'Words per minute':'WPM'}) # This column couldn't be 
# initialized as WPM because a column with that name was already present 
# within df.
df_wpm_type_melt['WPM Type'] = df_wpm_type_melt['WPM Type'].replace(
{'WPM':'Test WPM'})

df_wpm_type_melt


# In[ ]:


fig_wpm_by_player = px.line(df_wpm_type_melt, 
x = 'Player test number', y = 'WPM',
        color = 'Player', line_dash = 'WPM Type',
       title = 'WPM By Player and Test',
        color_discrete_sequence = px.colors.qualitative.Alphabet)
fig_wpm_by_player.write_html(
    f'{mp_visualizations_folder}{test_results_name}_Mean_WPM_By_\
Player_And_Test.html',
    include_plotlyjs = 'cdn')
# Note: 'Alphabet' is used here so that up to 26 distinct colors can be
# shown within the chart (which will prove useful for multiplayer rounds
# with larger player counts).
# fig_wpm_by_player


# Calculating mean WPMs by player and round as well as overall WPMs:

# In[ ]:


df_mean_wpm_by_player_and_round = df.pivot_table(
index = ['Player', 'Round'], values = 'WPM', 
               aggfunc = 'mean').reset_index()

# Adding overall WPMs for each player to the bottom of this DataFrame:

df_mean_wpm_by_player = df.pivot_table(
index = 'Player', values = 'WPM', 
               aggfunc = 'mean').reset_index()
df_mean_wpm_by_player['Round'] = 'Overall'

df_mean_wpm_by_player_and_round = pd.concat([
    df_mean_wpm_by_player_and_round, df_mean_wpm_by_player]).reset_index(
    drop=True)
# Ensuring that all Round values are strings: (I found that, without
# this update, the Overall rows would not appear within the figure
# that we're about to create.)
df_mean_wpm_by_player_and_round['Round'] = (
    df_mean_wpm_by_player_and_round['Round'].astype('str'))
df_mean_wpm_by_player_and_round


# In[ ]:


fig_mean_wpm_by_player_and_round = px.bar(
    df_mean_wpm_by_player_and_round, x = 'Round', 
       y = 'WPM', color = 'Player', barmode = 'group',
    color_discrete_sequence = px.colors.qualitative.Alphabet,
    title = 'Mean WPM by Player and Round',
      text_auto = '.0f')
fig_mean_wpm_by_player_and_round.write_html(
    f'{mp_visualizations_folder}{test_results_name}_Mean_WPM_\
By_Player_And_Round.html',
    include_plotlyjs = 'cdn')
# fig_mean_wpm_by_player_and_round


# In[ ]:


df_wins = df.pivot_table(index = 'Player', values = 'Player had best \
WPM for this test', aggfunc = 'sum').reset_index()
df_wins.sort_values('Player had best WPM for this test', ascending = False,
                   inplace = True)
df_wins


# In[ ]:


fig_wins = px.bar(df_wins, x = 'Player', 
       y = 'Player had best WPM for this test',
      title = 'Number of Tests in Which Each Player \
Had the Highest WPM', text_auto = '.0f',
                 color = 'Player', 
color_discrete_sequence=px.colors.qualitative.Alphabet).update_layout(
yaxis_title = 'Wins')
fig_wins.write_html(f'{mp_visualizations_folder}{test_results_name}_\
wins_by_player.html', include_plotlyjs = 'cdn')
# fig_wins


# In[ ]:


df_highest_wpm = df.pivot_table(index = 'Player', values = 'WPM', 
                                aggfunc = 'max').reset_index()
df_highest_wpm.sort_values('WPM', ascending = False, inplace = True)
df_highest_wpm


# In[ ]:


fig_highest_wpm = px.bar(df_highest_wpm, x = 'Player', 
       y = 'WPM',
      title = 'Highest WPM by Player', text_auto = '.3f',
                 color = 'Player', 
                 color_discrete_sequence = 
px.colors.qualitative.Alphabet)
fig_highest_wpm.write_html(
    f'{mp_visualizations_folder}{test_results_name}_\
highest_wpm_by_player.html', include_plotlyjs = 'cdn')
# fig_highest_wpm


# In[ ]:


end_time = time.time()
run_time = end_time - start_time
print(f"Finished calculating and visualizing multiplayer stats in \
{round(run_time, 3)} seconds.")


# In[ ]:




