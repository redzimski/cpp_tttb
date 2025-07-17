#!/usr/bin/env python
# coding: utf-8

# ## Visualization scripts for multiplayer Type Through the Bible files
# 
# By Ken Burchfiel
# 
# Released under the MIT license

# In[1]:


import time
start_time = time.time()
import os
import pandas as pd
import numpy as np
import plotly.express as px
mp_results_folder = '../Files/Multiplayer/'
# os.listdir(mp_results_folder)


# Adding code that will allow the caller to specify which multiplayer results file to analyze:
# 
# (This file *must* end with "test_results.csv" in order for the code to work correctly.)

# In[8]:


# The following code was based on
# https://docs.python.org/3/howto/argparse.html#argparse-tutorial
# and # https://docs.python.org/3/library/argparse.html .
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()
test_results_file = args.filename


# In[13]:


# If you're running this code within a notebook, skip over the previous
# cell and then uncomment and run the following line:
# test_results_file = '20250706T220148_string_test_results.csv'
test_results_name = test_results_file[0:-17] 
# Removes the 'test_results.csv' component from the file so that
# it can be more easily repurposed for chart filenames
test_results_name


# In[3]:


df = pd.read_csv(mp_results_folder+test_results_file)
# Replacing the tag columns with their actual meanings:
df.rename(columns = {'Tag_1':'Round','Tag_2':'Test within round',
                     'Tag_3':'Game test number'}, inplace = True)
# Making sure that the results are stored in the order that they were
# typed:
df.sort_values('Game test number', inplace = True)

# Adding a column that shows round and test combinations for each race:
# (This can be used as an x axis value for our WPM-by-race graph.)
df['Round_Test'] = df['Round'].astype('str') + '_' + df[
'Test within round'].astype('str')
# Adding another column that shows how many tests each player has completed
# so far:
# (cumcount starts at 0, so we'll need to add 1 to this value for it
# to work. Also note that the DataFrame doesn't need to be sorted by 
# player beforehand in order for this code to work correctly.)
df['Player test number'] = df.groupby(
    'Player')['WPM'].transform('cumcount') + 1
# Calculating cumulative WPM values:
df['Cumulative WPM'] = (df.groupby('Player')['WPM'].transform(
'cumsum')) / df['Player test number']

df['Best Round_Test WPM'] = df.groupby(
    'Round_Test')['WPM'].transform('max')
df['Player had best WPM for this test'] = np.where(
    df['WPM'] == df['Best Round_Test WPM'], 1, 0)

df.tail()


# Creating a melted verison of this DataFrame that stores both cumulative and test-specific WPM values within the same column:
# 
# (This will make it easier to produce a graph that uses different line dash types to differentiate between cumulative and test-specific WPM values.)

# In[4]:


df_wpm_type_melt = df.melt(id_vars = ['Player', 'Round_Test', 
'Player test number'],
value_vars = ['WPM', 'Cumulative WPM'],
var_name = 'WPM Type',
value_name = 'Words per minute').rename(
    columns = {'Words per minute':'WPM'}) # This column couldn't be 
# initialized as WPM because a column with that name was already present 
# within df.
df_wpm_type_melt['WPM Type'] = df_wpm_type_melt['WPM Type'].replace(
{'WPM':'Test WPM'})

df_wpm_type_melt


# In[5]:


fig_wpm_by_player = px.line(df_wpm_type_melt, 
x = 'Player test number', y = 'WPM',
        color = 'Player', line_dash = 'WPM Type',
       title = 'WPM By Player and Test',
        color_discrete_sequence = px.colors.qualitative.Alphabet)
fig_wpm_by_player.write_html(
    f'Multiplayer/{test_results_name}_Mean_WPM_By_Player_And_Test.html',
    include_plotlyjs = 'cdn')
# Note: 'Alphabet' is used here so that up to 26 distinct colors can be
# shown within the chart (which will prove useful for multiplayer rounds
# with larger player counts).
# fig_wpm_by_player


# Calculating mean WPMs by player and round as well as overall WPMs:

# In[6]:


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


# In[7]:


fig_mean_wpm_by_player_and_round = px.bar(
    df_mean_wpm_by_player_and_round, x = 'Round', 
       y = 'WPM', color = 'Player', barmode = 'group',
    color_discrete_sequence = px.colors.qualitative.Alphabet,
    title = 'Mean WPM by Player and Round',
      text_auto = '.0f')
fig_mean_wpm_by_player_and_round.write_html(
    f'Multiplayer/{test_results_name}_Mean_WPM_By_Player_And_Round.html',
    include_plotlyjs = 'cdn')
# fig_mean_wpm_by_player_and_round


# In[8]:


df_wins = df.pivot_table(index = 'Player', values = 'Player had best \
WPM for this test', aggfunc = 'sum').reset_index()
df_wins.sort_values('Player had best WPM for this test', ascending = False,
                   inplace = True)
df_wins


# In[9]:


fig_wins = px.bar(df_wins, x = 'Player', 
       y = 'Player had best WPM for this test',
      title = 'Number of Tests in Which Each Player \
Had the Highest WPM', text_auto = '.0f',
                 color = 'Player', 
                 color_discrete_sequence=px.colors.qualitative.Alphabet).update_layout(
yaxis_title = 'Wins')
fig_wins.write_html(f'Multiplayer/{test_results_name}_\
wins_by_player.html', include_plotlyjs = 'cdn')
# fig_wins


# In[10]:


df_highest_wpm = df.pivot_table(index = 'Player', values = 'WPM', 
                                aggfunc = 'max').reset_index()
df_highest_wpm.sort_values('WPM', ascending = False, inplace = True)
df_highest_wpm


# In[11]:


fig_highest_wpm = px.bar(df_highest_wpm, x = 'Player', 
       y = 'WPM',
      title = 'Highest WPM by Player', text_auto = '.3f',
                 color = 'Player', 
                 color_discrete_sequence = 
px.colors.qualitative.Alphabet)
fig_highest_wpm.write_html(
    f'Multiplayer/{test_results_name}_\
highest_wpm_by_player.html', include_plotlyjs = 'cdn')
# fig_highest_wpm


# In[12]:


end_time = time.time()
run_time = end_time - start_time
print(f"Finished calculating and visualizing multiplayer stats in \
{round(run_time, 3)} seconds.")

