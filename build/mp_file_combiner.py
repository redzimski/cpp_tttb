#!/usr/bin/env python
# coding: utf-8

# # Script for combining multiple multiplayer result files into a single multiplayer file
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

# In[17]:


import pandas as pd
pd.set_option('display.max_columns', 1000)
import os
import subprocess


# (For documentation on the following sets of code, see the similar set of code within mp_visualizations.ipynb.)

# In[2]:


notebook_exec = False
try:
    get_ipython()
    notebook_exec = True 
except:
    pass

notebook_exec

if notebook_exec == False:
    # The following code was based on
    # https://docs.python.org/3/howto/argparse.html#argparse-tutorial
    # and # https://docs.python.org/3/library/argparse.html .
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("first_verse_id", type = int)
    parser.add_argument("last_verse_id", type = int)
    args = parser.parse_args()
    first_verse_id = args.first_verse_id
    last_verse_id = args.last_verse_id

else: # Update these as needed when running the Jupyter notebook directly
    first_verse_id = 30786
    last_verse_id = 30795

unique_verse_count = last_verse_id - first_verse_id + 1

first_verse_id, last_verse_id, unique_verse_count


# In[3]:


mp_test_result_folder_path = '../Files/MP_Test_Result_Files_To_Combine/'
mp_test_result_files = os.listdir(mp_test_result_folder_path)
mp_test_result_files


# In[10]:


mp_test_result_headers = ['Test_Number', 'Within_Session_Test_Number', 
'Unix_Test_Start_Time', 'Local_Test_Start_Time', 'Unix_Test_End_Time', 
'Local_Test_End_Time', 'Verse_ID', 'Verse_Code', 'Verse', 'Characters', 
'WPM', 'Test_Seconds', 'Error_Rate', 'Error_and_Backspace_Rate', 
'Marathon_Mode', 'Player', 'Mode', 'Tag_1', 'Tag_2', 'Tag_3', 'Notes']


# In[11]:


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
df_combined


# ## Saving this combined file to the Multiplayer test results folder:
# (This filename will consist of a condensed version of the earliest
# timestamp, followed by a 'CMR' string (which stands for 'combined
# multiplayer results), followed by tthe regular '_test_results.csv'
# suffix for test result files.)

# In[19]:


df_combined_file_timestamp = df_combined.iloc[0]['Local_Test_Start_Time'][
0:19].replace('-', '').replace(':','') # This timestamp will also 
# get used as the argument for an upcoming run of the multiplayer 
# visualizations script.
df_combined_filename = df_combined_file_timestamp + '_CMR_test_results.csv'
df_combined_filename


# In[21]:


df_combined_file_timestamp


# In[22]:


df_combined.to_csv('../Files/Multiplayer/'+df_combined_filename,
                  index = False)


# In[26]:


print(f"Finished combining multiplayer files into a single file.\n This \
file is available at ../Files/Multiplayer/{df_combined_filename}.")


# ## Using the regular multiplayer analysis script to process these results:
# 
# The following code is based on the example found at
# https://www.geeksforgeeks.org/python/how-to-run-another-python-script-with-arguments-in-python/ .

# In[23]:


subprocess.run(['python', 'mp_visualizations.py', 
                df_combined_file_timestamp])

