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
import subprocess


# In[2]:


current_os = platform.system().lower() # Will be used to label certain files
# and folders
if current_os == 'darwin':
    current_os = 'osx' # Will be more intuitive for many users 
    # than 'darwin'
current_os


# In[3]:


release_folder = f'../cpp_tttb_{current_os}_release/' 
# rf = 'release folder'
release_folder


# In[4]:


# For documentation on the following code,
# see build/tttb_py_complement.ipynb.

notebook_exec = False
try:
    get_ipython()
    notebook_exec = True # Script is running within a notebook
except:
    pass

notebook_exec
    


# In[5]:


if notebook_exec == False:
    import argparse
    parser = argparse.ArgumentParser()
    # The items_to_compile argument specifies which source code files,
    # if any, you wish to compile into binaries. Enter 'both'
    # to compile both the tttb.cpp and tttb_py_complement files;
    # 'cpp' to compile only the tttb.cpp file; 'py' to compile
    # only the tttb_py_complement.py file; and 'neither' to 
    # skip all compilation processes (which you might want to select
    # if you've already compiled the latest versions.)
    
    parser.add_argument("files_to_compile", default='neither')
    args = parser.parse_args()
    files_to_compile = args.files_to_compile
else:
    files_to_compile = 'both'

# Determining, based on the argument passed to files_to_compile,
# which source code files to compile:
compile_cpp = False
compile_py = False

if files_to_compile in ['both', 'cpp']:
    compile_cpp = True
if files_to_compile in ['both', 'py']:
    compile_py = True

files_to_compile, compile_cpp, compile_py


# Specifying the names of the Python and C++ binaries:

# In[6]:


if current_os == 'windows':
    python_binary = 'tttb_py_complement.exe'
    cpp_binary = 'tttb.exe'
else:
    python_binary = 'tttb_py_complement'
    cpp_binary = 'tttb'


# In[7]:


python_binary, cpp_binary


# In[8]:


os.getcwd()


# ### Building our C++ and Python files (if requested by the caller):

# Moving into the build subfolder (simply because this is where I'm used to excuting the following commands when running them within a terminal or command prompt):

# In[9]:


os.chdir('build')


# In[10]:


os.getcwd()


# In[11]:


if compile_cpp == True:
    print("Now compiling tttb.cpp.")
    compile_cpp_output_1 = subprocess.run("cmake ..", shell=True, 
                            capture_output = True, check=True)
    print(compile_cpp_output_1)
    compile_cpp_output_2 = subprocess.run("cmake --build .", shell=True,
                            capture_output = True, check=True)
    print(compile_cpp_output_2)
else:
    print("Skipping the compilation process for tttb.cpp.")


# In[12]:


if compile_py == True:
    print("Now compiling tttb_py_complement.py.")
    # The -y argument in the following call will allow any existing
    # material within the output folder to get deleted and replaced.
    compile_py_output = subprocess.run(
        "pyinstaller tttb_py_complement.py -y", shell = True, 
        capture_output = True)
    print(compile_py_output)
    # Copying tttb_py_complement binary and its corresponding
    # _internal folder into the build folder (where the C++ program expects
    # to find it):
    shutil.rmtree('_internal')
    # Based on datainsight's StackOverflow
        # answer at https://stackoverflow.com/a/70075600/13097194 
    shutil.copytree(
        'dist/tttb_py_complement/_internal', '_internal')
    # Note that shutil.copy() will overwrite the existing copy of the file
    # (if any) in the destination folder with the new copy; see
    # https://docs.python.org/3/library/shutil.html#shutil.copy
    # for details
    shutil.copy(
        f'dist/tttb_py_complement/{python_binary}', 
        f'{python_binary}')
else:
    print("Skipping the compilation process for tttb_py_complement.py.")


# Moving back into our main folder:

# In[13]:


os.chdir('..')
os.getcwd()


# In[14]:


if release_folder.replace('../', '').replace('/', '') in os.listdir('../'):
    # NOTE: this will remove the existing folder (which will allow us to
    # more easily recreate a clean copy).
    shutil.rmtree(release_folder)
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

# In[15]:


if list(pd.read_csv(
'Files/word_results_headers_only.csv').columns) != list(
pd.read_csv('Files/word_results.csv').columns):
    raise ValueError ("Columns don't match!")


# In[16]:


if list(pd.read_csv(
    'Files/test_results_headers_only.csv').columns) != list(
pd.read_csv('Files/test_results.csv').columns):
    raise ValueError ("Columns don't match!")


# In[17]:


if list(pd.read_csv(
    'Files/game_config_headers_only.csv').columns) != list(
pd.read_csv('Files/game_config.csv').columns):
    raise ValueError ("Columns don't match!")


# In[18]:


shutil.copy('Files/word_results_headers_only.csv',
            release_folder+'Files/word_results.csv')
shutil.copy('Files/game_config_headers_only.csv',
            release_folder+'Files/game_config.csv')
shutil.copy('Files/test_results_headers_only.csv',
            release_folder+'Files/test_results.csv')
shutil.copy('Catholic_Public_Domain_Bible/CPDB_for_TTTB.csv',
            release_folder+'Files/CPDB_for_TTTB.csv')
shutil.copy('README_download_link.txt',release_folder + 'README_download_link.txt')


# Copying TTTB C++ and Python binaries, along with supporting files for Python binary, to the release folder:

# In[19]:


shutil.copy(f'build/{cpp_binary}',
            release_folder+f'build/{cpp_binary}')
shutil.copy(f'build/{python_binary}',
            release_folder+f'build/{python_binary}')
# For details on shutil.copytree, see 
# https://docs.python.org/3/library/shutil.html
shutil.copytree('build/_internal', release_folder+'build/_internal')


# Copying Markdown and PDF versions of Readme over to release folder:
# 
# (I commented out this option because I decided to share the Readme as a separate file instead. That way, I wouldn't have to create new zip files of release folders, each hundreds of megabytes in size, for distribution on itch.io just because I updated the game's instructions.)

# In[20]:


# shutil.copy('README.md',
#             release_folder+'README.md')
# shutil.copy('README.pdf',
#             release_folder+'README.pdf')


# In[22]:


print(f"Finished running the create_release_folder script. A \
Clean copy of TTTB can now be found at:\n{release_folder}")

