#!/usr/bin/env python
# coding: utf-8

# # Python Complement to Type Through the Bible
# 
# By Ken Burchfiel
# 
# Released under the MIT License
# 
# This script is a compilation of three scripts that were originally separate:
# 
# 1. A single-player results visualization script
# 2. A multiplayer results visualization script
# 3. A script for combining multiple multiplayer files into a single file
# 
# I chose to combine them so that they could all use the same Pyinstaller content directory, thus greatly reducing TTTB's file size.
# 
# This script takes two arguments: (1) a 'category' argument that specifies which of the three sets of code to run, and a 'second_arg' argument that allows the user to customize how two of these scripts will run.

# In[1]:


import time
start_time = time.time()
print("Starting Python script. It may take a little while to run; please \
be patient.")
import os
import subprocess
import platform
import pandas as pd
import numpy as np
import plotly.express as px
pd.set_option('display.max_columns', 1000)

# The following file paths are relative to the build folder.
mp_results_folder = '../Files/Multiplayer/'
mp_visualizations_folder = '../Visualizations/Multiplayer/'
sp_visualizations_folder = '../Visualizations/Single_Player/'


# Checking whether this script is running within a Jupyter notebook: 
# 
# (This will allow us to determine whether to specify our multiplayer filename via argparse (which will only work when the .py version of the file is being rurn) or via a notebook-specific argument).)
# 
# This code is based on Gustavo Bezerra's answer at https://stackoverflow.com/a/39662359/13097194 .

# In[2]:


notebook_exec = False
try:
    get_ipython()
    notebook_exec = True # Script is running within a notebook
except:
#     print("get_ipython() failed, so we'll assume that we're running \
# this script within a .py file.")
    pass

notebook_exec
    


# In[3]:


if notebook_exec == False:
    # The following code was based on
    # https://docs.python.org/3/howto/argparse.html#argparse-tutorial
    # and # https://docs.python.org/3/library/argparse.html .
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("category")
    # This argument can be 'spv' (for single-player visualizations);
    # 'mpv' (for multiplayer visualizations); or 'mpfc' (for the
    # multiplayer result file combiner script).
    # The following argument name will be kept generic
    # because it will have different meanings for
    # different categories.
    parser.add_argument("second_arg")
    args = parser.parse_args()
    category = args.category
    second_arg = args.second_arg
else:
    category = 'spv'
    second_arg = 'y'

category, second_arg


# In[4]:


## Assigning more intuitive names to this second argument for 
# the two categories that will make use of it:

if category == 'mpv':
    test_results_timestamp = second_arg
elif category == 'mpfc':
    verse_ids = second_arg


# ## Running one or two of these three scripts (depending on which category argument was passed)
# 
# (Note: the purpose of adding multiple if statements for each category is to make each script easier to debug as a Jupyter Notebook.)
# 
# (If the multiplayer file combiner script is requested, the multiplayer visualizations script will get run immediately after. In all other cases, only one of these three scripts will get run.)

# ## Multiplayer file combiner script
# 
# (This script makes it easier to allow multiple players to compete in a multiplayer Type Through the Bible Game simultaneously on different computers. Here's how they can do so:
# 
# 1. After individual players finish their tests, either within a one-player multiplayer game or within the main single-player game, they should transfer their results to a central folder.
# 2. Next, one player should copy or move all *test-result files* (e.g. not *word-result files*) into the MP_Test_Result_Files_To_Combine folder, located within the Files/ directory. That player should then run this script in order to combine those files into a single results file that can then be analyzed like any other multiplayer file.
# 
# This file can handle the following input data:
# 
# 1. Multiplayer files with just one player
# 3. Multiplayer files with multiple players (which will be handy if two or more players need to share a laptop)
# 4. Single-player files. (I recommend making the number of tests divisible by 10, since that way, players can simply copy their autosave data into the central folder.)
# 
# In addition, files *with* and *without* headers are compatible with this script.
# 
# This script can also handle cases in which two or more players have the same name, provided that they are not in the same multiplayer file. It will do so by appending a distinct suffix to all but one of these files.
# 
# **Important: if a player has not completed all of the tests specified by the first_verse_id and last_verse_id arguments, he/she will be excluded from the combined file!**

# In[5]:


if category == 'mpfc':    
    print("Combining multiplayer files together.")
    if verse_ids in ['y', 'Y']: # In this case, we'll examine a particular
        # player's results to determine which verse IDs
        # to use.
        detect_verses_from_first_player = True
    else:
        detect_verses_from_first_player = False
        first_verse_id = int(verse_ids.split('_')[0])
        last_verse_id = int(verse_ids.split('_')[1])
        unique_verse_count = last_verse_id - first_verse_id + 1

    mp_test_result_folder_path = '../Files/MP_Test_Result_Files_To_Combine/'
    mp_test_result_files = os.listdir(mp_test_result_folder_path)
    mp_test_result_files.sort()


# In[6]:


if category == 'mpfc':
    mp_test_result_headers = ['Test_Number', 'Session_Number', 
'Within_Session_Test_Number', 
'Unix_Test_Start_Time', 'Local_Test_Start_Time', 'Unix_Test_End_Time', 
'Local_Test_End_Time', 'Verse_ID', 'Verse_Code', 'Verse', 'Characters', 
'WPM', 'Test_Seconds', 'Error_Rate', 'Error_and_Backspace_Rate', 
'Marathon_Mode', 'Player', 'Mode', 'Tag_1', 'Tag_2', 'Tag_3', 'Notes']


# In[7]:


if category == 'mpfc':
    player_count = 1 # This list will help us assign unique initial codes
    # to each player's name, thus helping distinguish multiple players
    # who happen to have the same name (as long as those duplicate names
    # aren't contained in the same source file).
    
    df_result_list = [] # Creating a list of DataFrames, one for each
    # file, that will ultimately get converted into a single DataFrame
    
    # Processing each file within mp_test_result_folder_path:
    for filename in mp_test_result_files:
        # Reading in the first row of the DataFrame in order to check whether
        # this file contains headers or not:
        df_first_row = pd.read_csv(
            mp_test_result_folder_path + filename,
            header = None, nrows = 1)
    # Setting the header parameter to None ensures that the first row of the
    # .csv file, whether it contains headers or data, will get treated as
    # a row of data (thus making it easier to check what values it contains).
        if df_first_row.iloc[0, 0] == 'Test_Number': # This indicates that 
    # the file does contain headers; thus, we should make the 'names' argument
    # for our upcoming read_csv call None so that read_csv() will convert
    # the first row of the .csv file into the DataFrame's header row.
            names_arg = None
        else: # This indicates that the file does not contain headers. 
            # Therefore, we'll need to pass the headers stored in 
            # mp_test_result_headers to the 'header' argument so that they can 
            # be used as header values.
            names_arg = mp_test_result_headers
        
        
        # Now that we know what headers to use within our read_csv call,
        # we can import the entire dataset:
        
        df = pd.read_csv(mp_test_result_folder_path + filename,
                        names = names_arg)
    
        # Seeing which players are present in the file:
        player_list = df['Player'].unique()
        player_list.sort()
    
        if detect_verses_from_first_player == True:
            # In this case, the first and last verses typed by the
            # first player within the first file will be used as 
            # the set of reference verses for all other players.
            # (If this player's verses are incorrect, you can either
            # specify the verses to use within the arguments to this
            # script *or* make another file whose first player (in 
            # alphabetical terms) typed the correct set of verses.)
            print("player_list:",player_list)
            player_verses = df.query(
                f"Player == '{player_list[0]}'").copy()[
            'Verse_ID'].unique()
            player_verses.sort()
            first_verse_id = player_verses[0]
            last_verse_id = player_verses[-1]
            unique_verse_count = last_verse_id - first_verse_id + 1
            print(f"{first_verse_id} and {last_verse_id} will be used as \
the starting and ending verse IDs, respectively. These IDs are based \
on the verses typed by {player_list[0]} within {filename}.")
            detect_verses_from_first_player = False # Now that we've 
            # retrieved the verse IDs we need, we can set this flag to False.
            
        
        # Filtering the DataFrame to only include tests that fall within
        # the first_verse_id and last_verse_id bounds defined earlier:
    
        df.query("Verse_ID >= @first_verse_id & Verse_ID <= @last_verse_id",
                inplace = True)
    
        # Checking whether each player completed the range of tests
        # that starts at first_verse_id and ends at last_verse_id:
        # (Any player that did not complete all of these tests will be 
        # removed from the combined file.)
        for player in df['Player'].unique():
            if len(df.query("Player == @player")['Verse_ID'].unique()
    ) != unique_verse_count:
                print(f"{player} within {filename} did not complete all of \
the tests between {first_verse_id} and {last_verse_id}; thus, this player \
will be excluded from the combined dataset.")
                df.query("Player != @player", inplace = True)
                   
        
        # Making sure the tests are sorted in chronological order:
        # (We'll use Unix time here to prevent time zone differences from
        # affecting this sort.)
        df = df.sort_values(
            'Unix_Test_Start_Time').reset_index(drop=True).copy()
        
    
        # Adding numerical prefixes to each player's name in order to help 
        # differentiate between two players who happen to have the same name:
        for player in player_list:
            df['Player'] = df['Player'].replace(
                {player:str(player_count)+'_'+str(player)}).copy()
            player_count += 1
        
        # Replacing existing Tag_1 and Tag_2 values with 
        # a standardized set of values:
        # (This step is necessary because single-player files will likely have 
        # different tag values than multiplayer ones.)
        # As a reminder, tags 1, 2, and 3 normally refer to rounds,
        # tests within rounds, and player-specific test numbers, respectively.
        
        df['Tag_1'] = 1 # We'll treat this multiplayer game as having just one
        # round (which would be the case for any players who completed these
        # tests on their own)
        
        df['Tag_3'] = df.groupby('Player')['WPM'].transform('cumcount') + 1
        
        # Because this game has only one round, tags 2 and 3 will have the 
        # same value.
        
        df['Tag_2'] = df['Tag_3'].copy()
        # Storing the original filename within the 'Notes' field:
        df['Notes'] = filename
    
        
        df_result_list.append(df)
    
    # Combining all of these results into a single DataFrame:
    df_combined = pd.concat([df for df in df_result_list])
    # Sorting the tests by chronological order so that we can assign
    # accurate Test_Number and Within_Session_Test_Number values:
    
    df_combined = df_combined.sort_values(
        'Unix_Test_Start_Time').reset_index(drop=True).copy()
    # We'll treat all of the races as occurring within the same session.
    for column in ['Test_Number', 'Within_Session_Test_Number']:
        df_combined[column] = df_combined.index + 1
    df_combined['Session_Number'] = 1 # This too will be made uniform 
    # across all races.
    df_combined


# ### Saving this combined file to the Multiplayer test results folder:
# (This filename will consist of a condensed version of the earliest
# timestamp, followed by a 'CMR' string (which stands for 'combined
# multiplayer results), followed by tthe regular '_test_results.csv'
# suffix for test result files.)

# In[8]:


if category == 'mpfc':
    df_combined_file_timestamp = df_combined.iloc[0]['Local_Test_Start_Time'][
    0:19].replace('-', '').replace(':','') # This timestamp will also 
    # get used as the argument for an upcoming run of the multiplayer 
    # visualizations script.
    df_combined_filename = df_combined_file_timestamp + '_CMR_test_results.csv'
    df_combined_filename


# In[9]:


if category == 'mpfc':
    df_combined.to_csv('../Files/Multiplayer/'+df_combined_filename,
                  index = False)


# In[10]:


if category == 'mpfc':
    print(f"Finished combining multiplayer files into a single file.\nThis \
file is available at ../Files/Multiplayer/{df_combined_filename}.")
    # Now that we've created this file, we'll also want to analyze it using
    # the multiplayer visualizations script defined below. The following
    # code changes our category and second argument strings to facilitate this.

    category = 'mpv'
    test_results_timestamp = 'y' # This argument, when applied to the multiplayer
    # visualizations file, will analyze the most recently modified multiplayer
    # data. Since this will almost certainly be the test results file we just created,
    # this argument should work fine for our needs.


# ## Multiplayer visualizations script

# In[11]:


if category == 'mpv':
    print("Analyzing multiplayer data.")
    if (test_results_timestamp in ['y', 'Y']): # In this case, the 
        # most recently modified file (presumably one that was just created, 
        # in fact) will be analyzed.
        mp_file_list = [(file, os.path.getmtime(
        mp_results_folder+file)) for file in os.listdir(
        mp_results_folder) if 'test_results' in file]
        # The following code, which sorts files by their modification date 
        # (in ascending order), is based on an example found at
        # https://docs.python.org/3/howto/sorting.html#key-functions
        mp_file_list = sorted(
            mp_file_list, key = lambda file_pair: file_pair[1]).copy()
        test_results_file = mp_file_list[-1][0]
    else: # In this case, the argument will be interpreted as a timestamp,
        # and the first file in a list of all files that contain this timestamp
        # will be analyzed.
        # Determining the multiplayer test_results.csv file whose timestamp 
        # matches our test_results_timestamp string:
        # (There *should* only be one such timestamp, but just in case two 
        # or more share this timestamp--which is extremely improbable--only 
        # one will be retained. If you do happen to have two or more files 
        # with the same timestamp, temporarily move all but the one you wish 
        # to analyze out of the Files/Multiplayer/ folder.)
        test_results_file = [file for file in os.listdir(mp_results_folder) if 
        (test_results_timestamp in file) & ('test_results' in file)][0]
        
        # Creating a shortened version of this string that doesn't have
        # the 'test_results.csv' component at the end: 
        # (This shortened version will serve as the initial component
        # of our visualization filenames.)
    test_results_name = test_results_file[:-17]
    test_results_file, test_results_name
    print(f"Analyzing results within {test_results_file}.")
    df = pd.read_csv(mp_results_folder+test_results_file)


# In[12]:


if category == 'mpv':
    # Replacing the tag column names with their actual multiplayer-mode
    # meanings:
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


# Creating a melted verison of this DataFrame that stores both cumulative and test-specific WPM values within the same column:
# 
# (This will make it easier to produce a graph that uses different line dash types to differentiate between cumulative and test-specific WPM values.)

# In[13]:


if category == 'mpv':
    df_wpm_type_melt = df.melt(id_vars = ['Player', 'Player test number'],
    value_vars = ['WPM', 'Cumulative WPM'],
    var_name = 'WPM Type',
    value_name = 'Words per minute').rename(
        columns = {'Words per minute':'WPM'}) # This column couldn't be 
    # initialized as WPM because a column with that name was already present 
    # within df.
    df_wpm_type_melt['WPM Type'] = df_wpm_type_melt['WPM Type'].replace(
    {'WPM':'Test WPM'})
    
    print("Creating visualizations.")
    fig_wpm_by_player = px.line(df_wpm_type_melt, 
x = 'Player test number', y = 'WPM',
        color = 'Player', line_dash = 'WPM Type',
       title = 'WPM By Player and Test',
        color_discrete_sequence = px.colors.qualitative.Alphabet)
    fig_wpm_by_player.write_html(
    f'{mp_visualizations_folder}{test_results_name}_mean_WPM_by_\
player_and_test.html',
    include_plotlyjs = 'cdn')
    # Note: 'Alphabet' is used here so that up to 26 distinct colors can be
    # shown within the chart (which will prove useful for multiplayer rounds
    # with larger player counts).
    # fig_wpm_by_player


# Calculating mean WPM by player and round as well as overall WPM:

# In[14]:


if category == 'mpv':
    df_mean_wpm_by_player_and_round = df.pivot_table(
    index = ['Player', 'Round'], values = 'WPM', 
                   aggfunc = 'mean').reset_index()
    
    # Adding overall WPM for each player to the bottom of this DataFrame:
    
    df_mean_wpm_by_player = df.pivot_table(
    index = 'Player', values = 'WPM', 
                   aggfunc = 'mean').reset_index()
    df_mean_wpm_by_player['Round'] = 'Overall'
    
    df_mean_wpm_by_player_and_round = pd.concat([
        df_mean_wpm_by_player_and_round, 
        df_mean_wpm_by_player]).reset_index(
        drop=True)
    # Ensuring that all Round values are strings: (I found that, without
    # this update, the Overall rows would not appear within the figure
    # that we're about to create.)
    df_mean_wpm_by_player_and_round['Round'] = (
        df_mean_wpm_by_player_and_round['Round'].astype('str'))
    df_mean_wpm_by_player_and_round

    # Calculating players' overall ranks:
    df_overall_ranks = df_mean_wpm_by_player_and_round.query(
    "Round == 'Overall'").copy().sort_values(
    'WPM', ascending = False).reset_index(drop=True)
    df_overall_ranks['Overall rank'] = df_overall_ranks.index + 1
    df_overall_ranks

    df_mean_wpm_by_player_and_round = df_mean_wpm_by_player_and_round.merge(
    df_overall_ranks[['Player', 'Overall rank']], 
    on = 'Player', how = 'left')
    df_mean_wpm_by_player_and_round

    fig_mean_wpm_by_player_and_round = px.bar(
        df_mean_wpm_by_player_and_round.sort_values(
    'Overall rank', ascending = True), x = 'Round', 
           y = 'WPM', color = 'Player', barmode = 'group',
        color_discrete_sequence = px.colors.qualitative.Alphabet,
        title = 'Mean WPM by Player and Round',
          text_auto = '.0f', hover_data = 'Overall rank')
    fig_mean_wpm_by_player_and_round.write_html(
        f'{mp_visualizations_folder}{test_results_name}_mean_WPM_\
by_player_and_round.html',
        include_plotlyjs = 'cdn')
    # fig_mean_wpm_by_player_and_round


# In[15]:


if category == 'mpv':
    df_wins = df.pivot_table(index = 'Player', values = 'Player had best \
WPM for this test', aggfunc = 'sum').reset_index()
    df_wins.sort_values('Player had best WPM for this test', ascending = False,
                       inplace = True)
    df_wins

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


# In[16]:


if category == 'mpv':
    df_highest_wpm = df.pivot_table(index = 'Player', values = 'WPM', 
                                aggfunc = 'max').reset_index()
    df_highest_wpm.sort_values('WPM', ascending = False, inplace = True)
    df_highest_wpm

    fig_highest_wpm = px.bar(df_highest_wpm, x = 'Player', 
       y = 'WPM',
      title = 'Highest WPM by Player', text_auto = '.3f',
                 color = 'Player', 
                 color_discrete_sequence = 
    px.colors.qualitative.Alphabet)
    fig_highest_wpm.write_html(
        f'{mp_visualizations_folder}{test_results_name}_\
highest_WPM_by_player.html', include_plotlyjs = 'cdn')
    # fig_highest_wpm


# In[17]:


if category == 'mpv':
    end_time = time.time()
    run_time = end_time - start_time
    print(f"Finished calculating and visualizing multiplayer stats in \
{round(run_time, 3)} seconds.")


# ## Single-player visualization script

# ### Analyzing test result data:

# In[18]:


if category == 'spv': 
    print("Analyzing single-player results.")
    df_tr = pd.read_csv('../Files/test_results.csv') # tr = 'test results'
    
    # Converting start/end timestamps to DateTime values:
    
    for col in ['Local_Test_Start_Time', 'Local_Test_End_Time']:
        df_tr[col] = pd.to_datetime(df_tr[col])
    # Ensuring the tests are being displayed in chronological order:
    # (This may not always be the case, especially if the player imported
    # multiplayer results into his/her single-player file.)
    # (This will help ensure that the 'chronological test number' values 
    # that we're about to create are accurate.)
    
    df_tr = df_tr.sort_values(
        'Local_Test_Start_Time').reset_index(drop=True).copy()
    df_tr['Chronological test number'] = df_tr.index+1
    df_tr['Count'] = 1


# Adding chronological session numbers to DataFrame:
# 
# (The following approach uses a combination of np.where() and cumsum() to create these numbers. I imagine that this approach is faster than is looping through the DataFrame to assign them, but I could be wrong.)
# 
# Note: if any sessions with a test number of 1 have been deleted, this code's classification of session numbers will be incorrect. However, these chronological values should still be 'good enough' for our needs.
# 
# (Note: I commented out this code following an update to the C++ code that allows session numbers to get calculated and stored within the original test_results.csv file. This code could become useful in the future if there's a need to display session numbers in chronological order, but for now, I'll comment it out.)

# In[19]:


# if category == 'spv': 
#     # We can identify new sessions as those whose within-session test 
# number
#     # is 1:
#     df_tr['new_session'] = np.where(
#         df_tr['Within_Session_Test_Number'] == 1, 1, 0)
#     # The following code increments the session number counter by 1 when
#     # a new session has begun and keeps it at its current number 
# otherwise,
#     # thus allowing us to determine how many sessions the player has 
#     # started thus far.)
#     df_tr['Chronological session number'] = df_tr[
# 'new_session'].cumsum()
#     # We won't have any further need for the new_session column, so we can
#     # remove it:
#     df_tr.drop('new_session', axis = 1, inplace = True)
#     df_tr


# Calculating various timing statistics that will prove useful for endurance-related analyses:

# In[20]:


if category == 'spv': 
    for time_type in ['Start', 'End']:
        df_tr[f'{time_type} Year and Month'] = df_tr[
        f'Local_Test_{time_type}_Time'].dt.year.astype('str') + '-' + df_tr[
        f'Local_Test_{time_type}_Time'].dt.month.astype('str').str.zfill(2)
        df_tr[f'{time_type} Date'] = df_tr[
            f'Local_Test_{time_type}_Time'].dt.date
        df_tr[f'{time_type} Hour'] = df_tr[
            f'Local_Test_{time_type}_Time'].dt.hour
        df_tr[f'{time_type} Minute'] = df_tr[
            f'Local_Test_{time_type}_Time'].dt.minute
        df_tr[f'{time_type} 30-Minute Block'] = np.where(
            df_tr[f'{time_type} Minute'] >= 30, 2, 1)
        # Using floor division to determine the 15- and 10-minute blocks
        # into which each test falls:
        df_tr[f'{time_type} 15-Minute Block'] = df_tr[
            f'{time_type} Minute'] // 15 + 1
        df_tr[f'{time_type} 10-Minute Block'] = df_tr[
            f'{time_type} Minute'] // 10 + 1
        
    
    # Creating columns that will store unique starting hours and
    # 30/15/10-minute blocks:
    df_tr['Unique Hour'] = df_tr['Start Date'].astype(
        'str') + '_' + df_tr['Start Hour'].astype('str')
    for block in ['30', '15', '10']:
        df_tr[f'Unique {block}-Minute Block'] = df_tr[
            'Unique Hour'] + '_' + df_tr[
            f'Start {block}-Minute Block'].astype('str')
    
    
    df_tr.head(5)


# ### Determining how many characters the player typed after each *rolling* hour, 30-minute period, 15-minute period, and 10-minute period:
# 
# (This information will be helpful for calculating endurance-based statistics.)

# In[21]:


if category == 'spv': 
    col_seconds_pair_list = [['Characters Typed in Next Hour', 3600],
                             ['Characters Typed in Next 30 Minutes', 1800],
                             ['Characters Typed in Next 15 Minutes', 900],
                             ['Characters Typed in Next 10 Minutes', 600]]


# Note: the following code will likely take a considerable amount of time to run once users have completed a significant number of tests (e.g. 1000+). Therefore, it would be ideal to eventually replace it with C++-based code *or* a more sophisticated Python-based approach. (I tried out the 'numba' engine setting within the df.apply() function, but it failed to work correctly.)
# 
# In the meantime, I've commented out this code so that it won't cause performance issues going forward.

# In[22]:


# df_tr_condensed = df_tr[['Unix_Test_Start_Time', 
# 'Unix_Test_End_Time', 'Characters', 'Test number']].copy()
# I thought this DataFrame might be more compatible with certain
# alternative engine options, but unfortunately, that wasn't the case.


# In[23]:


# for col_seconds_pair in col_seconds_pair_list:

#     df_tr[col_seconds_pair[0]] = df_tr.apply(
#         lambda x: df_tr[(df_tr[
#             'Unix_Test_Start_Time'] >= x['Unix_Test_Start_Time']) & (
#             df_tr['Unix_Test_End_Time'] 
#         < (x['Unix_Test_Start_Time'] + col_seconds_pair[1]))][
#             'Characters'].sum(), axis = 1)
# df_tr


# Note: I thought the following approach might actually be faster than the above option, as it only requires a single loop through the whole DataFrame. However, I found it to take a bit longer than the previous method.

# In[24]:


# for col in ['characters_typed_in_next_hour',
#             'characters_typed_in_next_30_minutes',
#             'characters_typed_in_next_15_minutes',
#             'characters_typed_in_next_10_minutes']:
#     df_tr[col] = 0
# for i in range(len(df_tr)):
#     start_time = df_tr.iloc[i]['Unix_Test_Start_Time'].astype(
#         'int64')
    
#     df_tr.iloc[i, df_tr.columns.get_loc(
#         'characters_typed_in_next_hour')] = df_tr[(
#         df_tr[
#         'Unix_Test_Start_Time'] >= start_time) & (df_tr[
#             'Unix_Test_End_Time'] 
#         < (start_time + 3600))]['Characters'].sum()
    
#     df_tr.iloc[i, df_tr.columns.get_loc(
#         'characters_typed_in_next_30_minutes')] = df_tr[(
#         df_tr[
#         'Unix_Test_Start_Time'] >= start_time) & (df_tr[
#             'Unix_Test_End_Time'] 
#         < (start_time + 1800))]['Characters'].sum()

#     df_tr.iloc[i, df_tr.columns.get_loc(
#             'characters_typed_in_next_15_minutes')] = df_tr[(
#             df_tr[
#             'Unix_Test_Start_Time'] >= start_time) & (df_tr[
#                 'Unix_Test_End_Time'] 
#             < (start_time + 900))]['Characters'].sum()
    
#     df_tr.iloc[i, df_tr.columns.get_loc(
#             'characters_typed_in_next_10_minutes')] = df_tr[(
#             df_tr[
#             'Unix_Test_Start_Time'] >= start_time) & (df_tr[
#                 'Unix_Test_End_Time'] 
#             < (start_time + 600))]['Characters'].sum()
            


# ### WPM results by test:
# 
# Calculating rolling and cumulative means:

# In[25]:


if category == 'spv': 
    print("Analyzing WPM data.")
    for period in [10, 50, 100, 1000]:
        #print(period)
        df_tr[f'Rolling {period}-test mean WPM'] = df_tr[
    'WPM'].rolling(window=period).mean()
    df_tr['Cumulative mean WPM'] = df_tr['WPM'].cumsum(
    ) / df_tr['Count'].cumsum()


# In[26]:


if category == 'spv': 
    fig_wpm_by_test = px.line(
        df_tr, x = 'Chronological test number', y = ['WPM', 
'Rolling 10-test mean WPM', 'Rolling 50-test mean WPM', 
'Rolling 100-test mean WPM', 'Rolling 1000-test mean WPM', 
'Cumulative mean WPM'],
    title = 'WPM by Chronological Test Number').update_layout(
legend_title = 'Metric')
    fig_wpm_by_test.write_html(
        f'{sp_visualizations_folder}WPM_by_race.html',
        include_plotlyjs = 'cdn')


# In[27]:


if category == 'spv': 
    df_fastest_tests = df_tr.sort_values(
        'WPM', ascending = False).iloc[0:100].copy().reset_index(drop=True)
    df_fastest_tests['Rank'] = df_fastest_tests.index + 1
    df_fastest_tests.head()


# In[28]:


if category == 'spv': 
    fig_fastest_tests = px.bar(df_fastest_tests, x = 'Rank', y = 'WPM',
       color = 'Error_and_Backspace_Rate',
       hover_data = ['Test_Number', 'Local_Test_Start_Time',
                     'Verse_ID', 'Verse_Code'],
       text_auto = '.3f', title = '100 Fastest Tests')
    fig_fastest_tests.write_html(
        f'{sp_visualizations_folder}fastest_tests.html',
        include_plotlyjs = 'cdn')


# In[29]:


if category == 'spv': 
    df_characters_and_avg_wpm_by_hour = df_tr.pivot_table(
    index = 'Start Hour', values = ['Characters', 'WPM'], 
    aggfunc = {'Characters':'sum',
    'WPM':'mean'}).reset_index().rename(
    columns = {'Start Hour':'Starting Hour'})
    df_characters_and_avg_wpm_by_hour['Starting Hour'] = (
    df_characters_and_avg_wpm_by_hour['Starting Hour'].astype('str'))
    df_characters_and_avg_wpm_by_hour


# In[30]:


if category == 'spv': 
    fig_chars_by_hour = px.bar(df_characters_and_avg_wpm_by_hour, 
    x = 'Starting Hour', y = 'Characters', text_auto = ',.0f',
    title = 'Characters Typed by Starting Hour')
    fig_chars_by_hour.write_html(
    f'{sp_visualizations_folder}chars_by_hour.html',
    include_plotlyjs = 'cdn')
    fig_chars_by_hour


# In[31]:


if category == 'spv': 
    fig_wpm_by_hour = px.bar(df_characters_and_avg_wpm_by_hour, 
    x = 'Starting Hour', y = 'WPM', text_auto = '.3f',
    title = 'Average WPM by Starting Hour', subtitle = '(Colors reflect the \
total number of characters typed that hour)',
    color = 'Characters')
    fig_wpm_by_hour.write_html(
    f'{sp_visualizations_folder}WPM_by_hour.html',
    include_plotlyjs = 'cdn')
    fig_wpm_by_hour


# ### Average WPM by Tag 1, Tag 2, and Tag 3 values:

# In[32]:


if category == 'spv': 
    for tag in ['Tag_1', 'Tag_2', 'Tag_3']:
        df_wpm_by_tag = df_tr.pivot_table(
            index = tag, values = ['WPM', 'Chronological test number'],
            aggfunc = {'WPM':'mean',
            'Chronological test number':'count'}).reset_index().rename(
            columns = {'Chronological test number':'Tests'})
        if 'WPM' in df_wpm_by_tag: # If there are no Tag_1 values within
            # the DataFrame, this will return False, thus preventing the
            # following line from raising an error.
            fig_wpm_by_tag = px.bar(df_wpm_by_tag, x = tag, y = 'WPM',
                                 title = f'Mean WPM by {tag} value',
                                text_auto = '.3f',
                                   hover_data = 'Tests')
            fig_wpm_by_tag.write_html(f'{sp_visualizations_folder}mean_\
WPM_by_{tag.lower()}.html', include_plotlyjs = 'cdn')


# ### Creating endurance-related charts:

# #### Visualizing *rolling* endurance statistics:
# 
# (I commented out the following visualization code because it relies on a very inefficient set of code that I have also commented out.)

# In[33]:


# for col in [pair[0] for pair in col_seconds_pair_list]:

#     df_endurance = df_tr.sort_values(col, ascending = False).copy(
#     ).reset_index(drop=True).head(50)
#     df_endurance['Rank'] = (df_endurance.index + 1)

#     fig_endurance = px.bar(
#     df_endurance, x = 'Rank', 
#     y = col,
#     title = 'Most ' + col,
#     hover_data = ['Chronological test number', 'Local_Test_Start_Time'])
    
#     fig_endurance.write_html('Single_Player/Endurance_Top_50_rolling_'+col.replace(
#         ' ', '_')+'.html', 
#     include_plotlyjs = 'cdn')


# #### Visualizing clock-based endurance statistics:

# In[34]:


if category == 'spv':
    print("Analyzing endurance data.")
    for time_category in ['Hour', '30-Minute Block', '15-Minute Block',
                          '10-Minute Block']:
        # The following code helps confirm that the following query() statement
        # is correctly filtering out tests whose starting and ending 
        # time categories don't match.
        # print(len(df_tr.query(f"`Start {time_category}` == `End {time_category}`")))
        df_endurance = df_tr.query(
        f"`Start {time_category}` == `End {time_category}`").pivot_table(
            index = f'Unique {time_category}', values = 'Characters', 
        aggfunc = 'sum').reset_index().sort_values(
        'Characters', ascending = False).reset_index(drop=True).head(50)
        df_endurance['Rank'] = (df_endurance.index + 1)
        
        fig_endurance = px.bar(
        df_endurance, x = f'Unique {time_category}', 
        y = 'Characters', text_auto = ',.0f',
        title = 'Most Characters Typed By ' + time_category,
        hover_data = 'Rank')
        
        fig_endurance.write_html(
        f'{sp_visualizations_folder}endurance_top_50_\
clock_'+time_category.replace(' ', '_').lower()+'.html', 
        include_plotlyjs = 'cdn')


# In[35]:


if category == 'spv':
    df_yyyy_mm_stats = df_tr.query(
        "`Start Year and Month` == `End Year and Month`").pivot_table(
        index = 'Start Year and Month', values = ['Characters', 'WPM'], 
        aggfunc = {'Characters':'sum', 'WPM':'mean'}).reset_index()
    df_yyyy_mm_stats


# In[36]:


if category == 'spv':
    fig_yyyy_mm_characters = px.line(
        df_yyyy_mm_stats, x = 'Start Year and Month',
                                    y = 'Characters')
    fig_yyyy_mm_characters.update_layout(xaxis_type = 'category',
    xaxis_title = None,
    title = 'Characters Typed by Starting Year and Month')
    fig_yyyy_mm_characters.write_html(
    f'{sp_visualizations_folder}characters_\
typed_by_year_and_month.html', include_plotlyjs = 'cdn')


# In[37]:


if category == 'spv':
    fig_yyyy_mm_most_characters = px.bar(
    df_yyyy_mm_stats.sort_values('Characters', ascending = False), 
    x = 'Start Year and Month',
    y = 'Characters', text_auto = ',.0f')
    fig_yyyy_mm_most_characters.update_layout(xaxis_type = 'category',
    xaxis_title = None,
    title = 'Months by characters typed')
    fig_yyyy_mm_most_characters.write_html(
    f'{sp_visualizations_folder}most_characters_\
typed_by_year_and_month.html', include_plotlyjs = 'cdn')


# In[38]:


if category == 'spv':
    fig_yyyy_mm_wpm = px.line(
        df_yyyy_mm_stats, x = 'Start Year and Month',
                                    y = 'WPM')
    fig_yyyy_mm_wpm.update_layout(xaxis_type = 'category',
    xaxis_title = None,
    title = 'Mean WPM by Starting Year and Month')
    fig_yyyy_mm_wpm.write_html(f'{sp_visualizations_folder}avg_WPM_by_\
year_and_month.html', include_plotlyjs = 'cdn')


# Graphing keypresses by date (in both chronological and ranked order):

# In[39]:


if category == 'spv':
    df_top_dates_by_keypresses = df_tr.query(
        "`Start Date` == `End Date`").pivot_table(
        index = 'Start Date', values = 'Characters', 
        aggfunc = 'sum').reset_index().sort_values(
        'Characters', ascending = False).reset_index(drop=True)
    df_top_dates_by_keypresses['Rank'] = df_top_dates_by_keypresses.index + 1
    # Plotly will automatically arrange these dates in chronological order 
    # despite our having sorted the source DataFrame by characters.
    fig_keypresses_by_date = px.bar(df_top_dates_by_keypresses,
                                         x = 'Start Date', y = 'Characters',
                                    text_auto = ',.0f',
                                  title = 'Characters typed by date',
                                   hover_data = ['Rank'])
    fig_keypresses_by_date.write_html(f'{sp_visualizations_folder}keypresses\
_typed_by_date.html', include_plotlyjs='cdn')


# In[40]:


if category == 'spv':
    fig_top_dates_by_keypresses = px.bar(
        df_top_dates_by_keypresses.head(50),
           x = 'Start Date', y = 'Characters',
        text_auto = ',.0f',
           title = 'Dates with the most characters typed', 
           hover_data = ['Rank']).update_layout(
        xaxis_type = 'category')
    fig_top_dates_by_keypresses.write_html(
        f'{sp_visualizations_folder}top_dates_by_keypresses.html', 
        include_plotlyjs='cdn')


# ### Calculating mean WPM by within-session test numbers:

# In[41]:


if category == 'spv':
    df_mean_wpm_by_within_session_test_number = df_tr.pivot_table(
        index = 'Within_Session_Test_Number',
                      values = ['WPM', 'Chronological test number'], 
                      aggfunc = {'WPM':'mean', 
                                 'Chronological test number':'count'}
    ).reset_index().rename(
        columns = {'Chronological test number':'Number of tests'})
    df_mean_wpm_by_within_session_test_number


# In[42]:


if category == 'spv':
    fig_mean_wpm_by_within_session_test_number = px.line(
        df_mean_wpm_by_within_session_test_number,
        x = 'Within_Session_Test_Number', y = 'WPM',
        title = 'Mean WPM by Within-Session Test Number',
        hover_data = 'Number of tests').update_layout(
        xaxis_title = 'Within-session test number')
    fig_mean_wpm_by_within_session_test_number.write_html(
        f'{sp_visualizations_folder}mean_WPM_by_within_\
session_test_number.html', 
        include_plotlyjs='cdn')
    #fig_mean_wpm_by_within_session_test_number


# In[43]:


if category == 'spv':
    fig_wpm_by_session_num_comparison = px.line(df_tr.query(
    "Within_Session_Test_Number.notna()"),
            x = 'Within_Session_Test_Number', y = 'WPM',
           color = 'Session_Number', 
            title = "WPM by Session Number and \
Within-Session Test Number").update_traces(
        mode = 'markers+lines').update_layout(showlegend = True,
        xaxis_title = 'Within-session test number')
    fig_wpm_by_session_num_comparison.write_html(
        f'{sp_visualizations_folder}WPM_by_within_session_\
test_number.html', 
        include_plotlyjs='cdn')
    # fig_wpm_by_session_num_comparison


# ### Accuracy analyses:

# In[44]:


if category == 'spv':
    print("Analyzing accuracy data.")
    df_wpm_by_error_rate = df_tr.pivot_table(
        index = 'Error_and_Backspace_Rate', 
        values = 'WPM', aggfunc = 'mean').reset_index()


# #### Assigning results to accuracy bins:
# 
# (The `duplicates = drop` component prevents the code from raising an error if two or more bins have the same group (which can happen, for instance, if error-free races account for a large percentage of your overall races).

# In[45]:


if category == 'spv':
    df_tr['Error/backspace rate bin'] = pd.qcut(
        df_tr['Error_and_Backspace_Rate'], 10, duplicates = 'drop').astype(
    'str')
    df_tr


# Calculating rolling WPM averages for each WPM category:
# 
# (This code is based on yoav_aaa's StackOverflow response at https://stackoverflow.com/a/64150512/13097194 ).
# 
# (Note that using DataFrameGroupBy (https://pandas.pydata.org/docs/dev/reference/api/pandas.core.groupby.DataFrameGroupBy.rolling.html) reorders the dataset and thus won't be an ideal method.)

# In[46]:


if category == 'spv':
    df_tr['10-test rolling WPM for error/backspace \
rate bin'] = df_tr.groupby(
    'Error/backspace rate bin')['WPM'].transform(
    lambda wpm_within_error_bin: wpm_within_error_bin.rolling(10).mean())
    df_tr

    fig_rolling_wpm_by_error_rate = px.line(df_tr, x = 'Chronological test number',
            y = '10-test rolling WPM for error/backspace rate bin', 
    color = 'Error/backspace rate bin',
           title = 'Rolling 10-test WPM by Error + Backspace \
Rate Bin').update_layout(
        yaxis_title = '10-test rolling WPM')
    
    fig_rolling_wpm_by_error_rate.write_html(
    f'{sp_visualizations_folder}mean_rolling_WPM_\
by_accuracy_bin.html', include_plotlyjs = 'cdn')


# In[47]:


if category == 'spv':
    df_mean_wpm_by_accuracy_bin = df_tr.pivot_table(
        index = 'Error/backspace rate bin',
                      values = ['WPM', 'Chronological test number'], 
                      aggfunc = {'WPM':'mean', 
    'Chronological test number':'count'}).reset_index().rename(
    columns = {'Chronological test number':'Number of races'})

    fig_mean_wpm_by_error_rate = px.bar(
    df_mean_wpm_by_accuracy_bin, x = 'Error/backspace rate bin',
           y = 'WPM', hover_data = 'Number of races',
           text_auto = '.2f',
    title = 'Mean WPM by Accuracy Bin')
    fig_mean_wpm_by_error_rate.write_html(
    f'{sp_visualizations_folder}mean_WPM_by_accuracy_bin.html', 
    include_plotlyjs = 'cdn')


# ### Analyzing word-level results:

# In[48]:


if category == 'spv':
    print("Analyzing word-level data.")
    df_wr = pd.read_csv('../Files/word_results.csv')
    df_wr['Count'] = 1


# Creating a table of words typed at least 10 times by average WPM:

# In[49]:


if category == 'spv':
    words_to_remove = ['s'] # This list will contain any 'words', such 
    # as 's', that shouldn't be counted as actual words.
    df_mean_wpm_by_word = df_wr.pivot_table(
    index = 'Word', values = ['WPM', 'Count'],
    aggfunc = {'WPM':'mean', 'Count':'count'}).reset_index()
    
    df_mean_wpm_by_word.query("Count >= 10 & Word not in @words_to_remove",
                             inplace = True)
    df_mean_wpm_by_word.sort_values('WPM', ascending = False, 
                                    inplace = True)
    df_mean_wpm_by_word


# In[50]:


if category == 'spv':
    fig_highest_word_level_wpm = px.bar(df_mean_wpm_by_word.head(50), 
           x = 'Word', y = 'WPM', text_auto = '.2f',
          hover_data = 'Count',
          title = 'Highest word-level mean WPM for words \
typed at least 10 times')
    fig_highest_word_level_wpm.write_html(
    f'{sp_visualizations_folder}words_with_highest_WPM.html', 
    include_plotlyjs = 'cdn')


# In[51]:


if category == 'spv':
    fig_lowest_word_level_wpm = px.bar(df_mean_wpm_by_word.sort_values(
    'WPM').head(50), x = 'Word', y = 'WPM', text_auto = '.2f',
          hover_data = 'Count',
          title = 'Lowest word-level mean WPM for words typed at least 10 \
times')
    fig_lowest_word_level_wpm.write_html(
    f'{sp_visualizations_folder}words_with_lowest_WPM.html', 
    include_plotlyjs = 'cdn')


# Analyzing word-level accuracy data:

# In[52]:


if category == 'spv': 
    df_wr['Typed Correctly'] = np.where(df_wr['Error_and_Backspace_Rate'] == 0, 1, 0)

    df_wr_acc_wpm = df_wr.pivot_table(
    index = 'Word', values = ['Count', 'Typed Correctly', 'WPM'], 
    aggfunc = {'Count':'sum', 'Typed Correctly':'mean',
'WPM':'mean'}).query(
    "Word not in @words_to_remove").reset_index()
    df_wr_acc_wpm['Error-free %'] = df_wr_acc_wpm['Typed Correctly'] * 100


# Sorting words typed at least 10 times by error-free rate and count, then creating a graph of the top 100 words in this list:

# In[53]:


if category == 'spv':
    fig_wr_high_acc = px.bar(df_wr_acc_wpm.query("Count >= 10").sort_values(
    ['Error-free %', 'Count'], ascending = False).iloc[0:100],
    x = 'Word', y = 'Error-free %', color = 'Count',
    title = "Words typed at least 10 times by error-free % (in descending order) and count")
    fig_wr_high_acc.write_html(
    f'{sp_visualizations_folder}high_accuracy_words.html', 
    include_plotlyjs = 'cdn')


# Using a similar process to create a list of frequently-typed words with the *lowest* accuracy ratings:

# In[54]:


if category == 'spv':
    fig_wr_low_acc = px.bar(df_wr_acc_wpm.query("Count >= 10").sort_values(
    ['Error-free %', 'Count'], ascending = [True, False]).iloc[0:100],
    x = 'Word', y = 'Error-free %', color = 'Count',
    title = "Words typed at least 10 times by error-free % (in ascending order) and count")
    fig_wr_low_acc.write_html(
    f'{sp_visualizations_folder}low_accuracy_words.html', 
    include_plotlyjs = 'cdn')


# In[55]:


if category == 'spv':
    fig_wr_acc_wpm = px.scatter(df_wr_acc_wpm.query(
    "Count >= 10"), x = 'Error-free %', y = 'WPM',
              hover_data = ['Word', 'Count'], color = 'Count',
              title = 'WPM by Error-free % for Words Typed at Least 10 Times')
    fig_wr_acc_wpm.write_html(
    f'{sp_visualizations_folder}word_accuracy_WPM_scatter.html', 
    include_plotlyjs = 'cdn')


# In[56]:


if category == 'spv':
    fig_most_frequent_words = px.bar(
    df_wr_acc_wpm.sort_values('Count', ascending = False).iloc[0:200],
    x = 'Word', y = 'Count', color = 'WPM', text_auto = 'Count',
    title = '200 Most Frequently-typed Words')
    fig_most_frequent_words.write_html(
    f'{sp_visualizations_folder}words_typed_most_frequently.html', 
    include_plotlyjs = 'cdn')


# ## Overall progress analyses:

# In[57]:


if category == 'spv':
    print("Analyzing overall progress data.")
    df_Bible = pd.read_csv('../Files/CPDB_for_TTTB.csv')
    df_Bible['Typed'] = np.where(df_Bible['Tests'] >= 1, 1, 0)
    df_Bible.rename(columns = {'Characters':'Total Characters'}, inplace = True)
    df_Bible['Typed Characters'] = df_Bible['Typed'] * df_Bible['Total Characters']
    df_Bible


# In[58]:


if category == 'spv':
    df_progress = df_Bible.pivot_table(
    index = ['Book_Num', 'Book'], values = [
    'Typed Characters', 'Total Characters'], aggfunc = 'sum',
    margins=True, margins_name='Overall').reset_index()
    df_progress['% Typed'] = 100*(df_progress['Typed Characters'] 
                                  / df_progress['Total Characters'])
    # Updating the Book_Num and Book values for the 'Overall' row:
    df_progress.at[len(df_progress)-1, 'Book_Num'] = len(df_progress)
    df_progress.at[len(df_progress)-1, 'Book'] = 'Overall'


# Graphing progress in percentage terms:

# In[59]:


if category == 'spv':
    fig_pct_progress = px.bar(df_progress, x = 'Book', y = '% Typed',
    title = 'Books of the Bible by % of Characters Typed', text_auto = '.1f',
    color = '% Typed', hover_data = [
    'Total Characters', 'Typed Characters'])
    fig_pct_progress.write_html(
    f'{sp_visualizations_folder}progress_percentage.html', 
    include_plotlyjs = 'cdn')


# Graphing progress in nominal (character-based) terms:
# 
# (This chart, unlike the previous one, doesn't include the 'Overall' row, as its presence would make all of the other bars appear very small in comparison.)

# In[60]:


if category == 'spv':
    fig_progress = px.bar(df_progress.query("Book != 'Overall'"), 
    x = 'Book', y = [
        'Total Characters', 'Typed Characters'],
    title = 'Books of the Bible by Total Characters and \
Characters Typed', text_auto = '.0f', barmode = 'overlay',
    hover_data = '% Typed',
    opacity = 1).update_layout(legend_title = 'Metric')
    fig_progress.write_html(
    f'{sp_visualizations_folder}progress_nominal.html', 
    include_plotlyjs = 'cdn')


# In[61]:


if category == 'spv':
    # Creating a 'Column' argument that can be used as the x-axis value
    # for an upcoming chart:
    df_Bible['Column'] = df_Bible['Verse_ID'] % round(
        np.sqrt(len(df_Bible)), 0)
    df_Bible['Count'] = 1 # This will serve as our upcoming chart's
    # Y-axis value.


# Creating a bar chart that shows whether or not each verse has been typed: (Verses can be identified by hovering over them. This chart isn't as practical as the others, but it's still fun to look at. :)

# In[62]:


if category == 'spv':
    fig_typed_verses = px.bar(df_Bible, x = 'Column', y = 'Count', 
    color = 'Typed',
    hover_data = ['Verse_ID', 'Verse_Code'], title = 'Typed verses').update_layout(coloraxis_showscale = False,
    paper_bgcolor = 'black',
    plot_bgcolor = 'black',
    xaxis_visible = False,
    yaxis_visible=False,
    )
    fig_typed_verses.write_html(
    f'{sp_visualizations_folder}Typed_verses.html', 
    include_plotlyjs = 'cdn')


# In[63]:


if category == 'spv':
    end_time = time.time()
    run_time = end_time - start_time
    print(f"Finished calculating and visualizing single-player stats in \
{round(run_time, 3)} seconds.")

