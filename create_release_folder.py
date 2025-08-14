#!/usr/bin/env python
# coding: utf-8

# # Script for creating folders that can store Linux, Windows, and Mac TTTB releases
# 
# Using this script makes it easier to quickly and accurately copy the files needed for a TTTB release into a folder that can then get zipped and uploaded to itch.io.
# 
# By Ken Burchfiel
# 
# Released under the MIT License
# 
# (Note: Before running this code, make sure that the latest copy of your Pyinstaller-based tttb_py_complement executable, along with its '_internal' folder, have been moved from build/dist/tttb_py_complement to build/. You can automate this process using the code in pyinstaller_commands.txt, but these will need to be updated to match your own computer's directory layout (as will this file).

# In[1]:


import os
import shutil
import platform
import pandas as pd


# In[2]:


os.getcwd()


# In[3]:


current_os = platform.system().lower() # Will be used to label certain files
# and folders
current_os


# In[4]:


release_folder = f'../cpp_tttb_{current_os}_release/' 
# rf = 'release folder'
release_folder


# In[5]:


if release_folder.replace('../', '').replace('/', '') in os.listdir('../'):
    # NOTE: this will remove the existing folder (which will allow us to
    # more easily recreate a clean copy).
    shutil.rmtree(release_folder) # Based on datainsight's StackOverflow
    # answer at https://stackoverflow.com/a/70075600/13097194 
os.mkdir(release_folder)

# Creating relevant directories:

os.mkdir(release_folder + 'Files/')
os.mkdir(release_folder + 'build/')
os.mkdir(release_folder + 'Files/Multiplayer/')
os.mkdir(release_folder + 'Files/MP_Test_Result_Files_To_Combine/')
os.mkdir(release_folder + 'Files/MP_Word_Result_Files_To_Combine/')
os.mkdir(release_folder + 'Visualizations/')
os.mkdir(release_folder + 'Visualizations/Multiplayer')
os.mkdir(release_folder + 'Visualizations/Single_Player')


# Making sure that the headers in our 'headers only' file match the ones I've been using in my own gameplay sessions: (sometimes I only update the latter rather than the former.)

# Copying new versions of our word result, test result, and Bible files over to the Files folder:

# In[6]:


if list(pd.read_csv(
'Files/word_results_headers_only.csv').columns) != list(
pd.read_csv('Files/word_results.csv').columns):
    raise ValueError ("Columns don't match!")


# In[7]:


if list(pd.read_csv(
    'Files/test_results_headers_only.csv').columns) != list(
pd.read_csv('Files/test_results.csv').columns):
    raise ValueError ("Columns don't match!")


# In[8]:


if list(pd.read_csv(
    'Files/game_config_headers_only.csv').columns) != list(
pd.read_csv('Files/game_config.csv').columns):
    raise ValueError ("Columns don't match!")


# In[9]:


shutil.copy('Files/word_results_headers_only.csv',
            release_folder+'Files/word_results.csv')
shutil.copy('Files/game_config_headers_only.csv',
            release_folder+'Files/game_config.csv')
shutil.copy('Files/test_results_headers_only.csv',
            release_folder+'Files/test_results.csv')
shutil.copy('Catholic_Public_Domain_Bible/CPDB_for_TTTB.csv',
            release_folder+'Files/CPDB_for_TTTB.csv')


# Copying TTTB C++ and Python binaries, along with supporting files for Python binary, to the release folder:

# In[10]:


shutil.copy('build/tttb',
            release_folder+'build/tttb')
shutil.copy('build/tttb_py_complement',
            release_folder+'build/tttb_py_complement')
# For details on shutil.copytree, see 
# https://docs.python.org/3/library/shutil.html
shutil.copytree('build/_internal', release_folder+'build/_internal')


# In[11]:


print(f"Clean copy of TTTB can now be found at:\n{release_folder}")

