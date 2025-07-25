#!/usr/bin/env python
# coding: utf-8

# ## Visualization scripts for single-player Type Through the Bible files
# 
# (Still very much a work in progress--many more analyses to come, including word-level ones and accuracy-focused graphs!)
# 
# By Ken Burchfiel
# 
# Released under the MIT License

# In[1]:


import time
start_time = time.time()
import pandas as pd # Polars could also be used in place of Pandas to 
# speed up some import/analysis processes--but, if there ends up being
# a need for faster data transformation code, I would rather do it in 
# C++ (as a means of building up my practice with that language.)
pd.set_option('display.max_columns', 1000)
import plotly.express as px
import numpy as np
sp_visualizations_folder = '../Visualizations/Single_Player/'


# ## Analyzing test result file:

# In[2]:


df_tr = pd.read_csv('../Files/test_results.csv') # tr = 'test results'

#Converting start/end timestamps to DateTime values:
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

df_tr


# Calculating various timing statistics that will prove useful for endurance-related analyses:

# In[3]:


for time_type in ['Start', 'End']:
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


# ## Determining how many characters the player typed after each *rolling* hour, 30-minute period, 15-minute period, and 10-minute period:
# 
# (This information will be helpful for calculating endurance-based statistics.)

# In[4]:


col_seconds_pair_list = [['Characters Typed in Next Hour', 3600],
                         ['Characters Typed in Next 30 Minutes', 1800],
                         ['Characters Typed in Next 15 Minutes', 900],
                         ['Characters Typed in Next 10 Minutes', 600]]


# Note: the following code will likely take a considerable amount of time to run once users have completed a significant number of tests (e.g. 1000+). Therefore, it would be ideal to eventually replace it with C++-based code *or* a more sophisticated Python-based approach. (I tried out the 'numba' engine setting within the df.apply() function, but it failed to work correctly.)
# 
# In the meantime, I've commented out this code so that it won't cause performance issues going forward.

# In[5]:


# df_tr_condensed = df_tr[['Unix_Test_Start_Time', 
# 'Unix_Test_End_Time', 'Characters', 'Test number']].copy()
# I thought this DataFrame might be more compatible with certain
# alternative engine options, but unfortunately, that wasn't the case.


# In[6]:


# for col_seconds_pair in col_seconds_pair_list:

#     df_tr[col_seconds_pair[0]] = df_tr.apply(
#         lambda x: df_tr[(df_tr[
#             'Unix_Test_Start_Time'] >= x['Unix_Test_Start_Time']) & (
#             df_tr['Unix_Test_End_Time'] 
#         < (x['Unix_Test_Start_Time'] + col_seconds_pair[1]))][
#             'Characters'].sum(), axis = 1)
# df_tr


# Note: I thought the following approach might actually be faster than the above option, as it only requires a single loop through the whole DataFrame. However, I found it to take a bit longer than the previous method.

# In[7]:


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
            


# In[8]:


# df_tr


# ### WPM results by test:

# In[9]:


fig_wpm_by_test = px.line(
    df_tr, x = 'Chronological test number', y = 'WPM',
title = 'WPM by Chronological Test Number',)
fig_wpm_by_test.write_html(f'{sp_visualizations_folder}WPM_by_race.html',
                           include_plotlyjs = 'cdn')


# ### Average WPM by Tag 1 values:

# In[10]:


df_wpm_by_tag_1 = df_tr.pivot_table(index = 'Tag_1', values = 'WPM',
                                 aggfunc = 'mean').reset_index()
df_wpm_by_tag_1


# In[11]:


fig_wpm_by_tag_1 = px.bar(df_wpm_by_tag_1, x = 'Tag_1', y = 'WPM',
                         title = 'Mean WPM by Tag_1 value')
fig_wpm_by_tag_1.write_html(f'{sp_visualizations_folder}/Mean_WPM_\
by_Tag_1.html',
                            include_plotlyjs = 'cdn')


# ## Creating endurance-related charts:

# ## Visualizing *rolling* endurance statistics:
# 
# (I commented out the following visualization code because it relies on a very inefficient set of code that I have also commented out.)

# In[12]:


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


# ## Visualizing clock-based endurance statistics:

# In[13]:


for time_category in ['Hour', '30-Minute Block', '15-Minute Block',
                      '10-Minute Block']:
    # The following code helps confirm that the following query() statement
    # is correctly filtering out tests whose starting and ending 
    # time categories don't match.
    # print(len(df_tr.query(f"`Start {time_category}` == `End {time_category}`")))
    df_endurance = df_tr.query(f"`Start {time_category}` == `End {time_category}`").pivot_table(
        index = f'Unique {time_category}', values = 'Characters', 
    aggfunc = 'sum').reset_index().sort_values(
    'Characters', ascending = False).reset_index(drop=True).head(50)
    df_endurance['Rank'] = (df_endurance.index + 1)
    
    fig_endurance = px.bar(
    df_endurance, x = f'Unique {time_category}', 
    y = 'Characters',
    title = 'Most Characters Typed By ' + time_category,
    hover_data = 'Rank')
    
    fig_endurance.write_html(
    f'{sp_visualizations_folder}Endurance_Top_50_\
Clock_'+time_category.replace(' ', '_')+'.html', 
    include_plotlyjs = 'cdn')


# Graphing keypresses by date (in both chronological and ranked order):

# In[14]:


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
                              title = 'Characters typed by date',
                               hover_data = ['Rank'])
fig_keypresses_by_date.write_html(f'{sp_visualizations_folder}Keypresses\
_Typed_by_Date.html', include_plotlyjs='cdn')


# In[15]:


fig_top_dates_by_keypresses = px.bar(
    df_top_dates_by_keypresses.head(50),
       x = 'Start Date', y = 'Characters',
       title = 'Dates with the most characters typed', 
       hover_data = ['Rank']).update_layout(
    xaxis_type = 'category')
fig_top_dates_by_keypresses.write_html(
    f'{sp_visualizations_folder}/Top_Dates_by_Keypresses.html', 
    include_plotlyjs='cdn')


# In[16]:


## Calculating mean WPMs by test number:


# In[17]:


df_tr.head()


# In[18]:


df_mean_wpm_by_within_session_test_number = df_tr.pivot_table(
    index = 'Within_Session_Test_Number',
                  values = ['WPM', 'Chronological test number'], 
                  aggfunc = {'WPM':'mean', 
                             'Chronological test number':'count'}).reset_index().rename(
    columns = {'Chronological test number':'Number of tests'})
df_mean_wpm_by_within_session_test_number


# In[19]:


fig_mean_wpm_by_within_session_test_number = px.line(
    df_mean_wpm_by_within_session_test_number,
    x = 'Within_Session_Test_Number', y = 'WPM',
    title = 'Mean WPM by Within-Session Test Number',
    hover_data = 'Number of tests').update_layout(
    xaxis_title = 'Within-session test number')
fig_mean_wpm_by_within_session_test_number.write_html(
    f'{sp_visualizations_folder}/Mean_WPM_by_Within_Session_Test_Number.html', 
    include_plotlyjs='cdn')
fig_mean_wpm_by_within_session_test_number


# In[20]:


# Creating a string version of the test number field that will allow it
# to get used as a color value for the following chart:
# (I found that, when this value was passed as an integer, no lines
# appeared within the chart.)
df_tr['Chronological test number as string'] = df_tr[
'Chronological test number'].astype('str')


# In[21]:


df_tr.query(
    "Within_Session_Test_Number.notna()").sort_values(
'Chronological test number').copy()


# In[23]:


df_tr_for_wpm_by_session = df_tr.query(
"Within_Session_Test_Number.notna()").copy()
df_tr_for_wpm_by_session[
'Within_Session_Test_Number'] = df_tr_for_wpm_by_session[
'Within_Session_Test_Number'].astype('int')
df_tr_for_wpm_by_session


# Not sure why lines aren't appearing within the following chart; I'll need to debug this further.

# In[24]:


fig_wpm_by_session_num_comparison = px.line(df_tr_for_wpm_by_session,
        x = 'Within_Session_Test_Number', y = 'WPM',
       color = 'Chronological test number as string').update_traces(
    mode = 'markers+lines').update_layout(showlegend = False)
fig_wpm_by_session_num_comparison.write_html(
    f'{sp_visualizations_folder}/WPM_by_Within_Session_Test_Number.html', 
    include_plotlyjs='cdn')
fig_wpm_by_session_num_comparison


# In[25]:


end_time = time.time()
run_time = end_time - start_time
print(f"Finished calculating and visualizing single-player stats in \
{round(run_time, 3)} seconds.")


# In[ ]:




