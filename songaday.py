import csv
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter1d

sns.set_style('darkgrid') # darkgrid, white grid, dark, white and ticks
plt.rc('axes', titlesize=14)     # fontsize of the axes title
plt.rc('axes', labelsize=10)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=12)    # legend fontsize
plt.rc('font', size=12)          # controls default text sizes

sad = pd.read_csv('~/Documents/Songaday/songaday.csv')
mood_scores = pd.read_csv('~/Documents/Songaday/mood_scores.csv')
mood_sorted = pd.read_csv('~/Documents/Songaday/mood_sorted.csv')
location_grp = pd.read_csv('~/Documents/Songaday/location_grp.csv')

sad2 = pd.DataFrame(sad['length'].str.split(':').tolist(), index= sad.index)
sad['length'] = pd.to_numeric(sad2[0])*60+pd.to_numeric(sad2[1])
sad['YTid'] = sad['videoID'].str.replace(r'^(.*)(/)','').str.replace(r'^(.*)(v\=)','')
sad_ids = ','.join(sad['YTid'])

if __name__ == "__main__":
    results = getYTstats(sad_ids)

ids = list()
views = list()
likes = list()
comments = list()
for i in list(range(len(results))):
    ids.append( results[i]['id'] )
    views.append( results[i]['statistics']['viewCount'] )
    likes.append( results[i]['statistics']['likeCount'] )
    comments.append( results[i]['statistics']['commentCount'] )



sad['tempo'] = pd.to_numeric(sad['tempo'],errors='coerce')
sad['date'] = sad['date'].str.replace('.','/')
sad2 = pd.DataFrame(sad.date.str.split('/').tolist(), index= sad.index)
sad['date'] = pd.to_datetime(dict(year=pd.to_numeric(sad2[2]), month=pd.to_numeric(sad2[0]), day=pd.to_numeric(sad2[1]) ))
sad['yearmonth'] = sad['date'].dt.year.map(str) + "-" + ('0'+sad['date'].dt.month.map(str)).str.strip().str[-2:4]
sad['yearweek'] = sad['date'].dt.strftime('%Y-%U')
sad['datetimemonth'] = pd.to_datetime(sad['yearmonth'], format='%Y-%m')
sad = pd.merge(sad,mood_sorted,on='mood',how='left')
sad = pd.merge(sad,mood_scores,on='mood',how='left')
sad = pd.merge(sad,location_grp,on='location',how='left')
sad['mood score'] = sad['score']

sad.to_csv('~/Documents/Songaday/modified.csv')


#Average out the numeric number on categorical bar chart
def bar_with_categorical_numeric_avg(sad,categorical_x,numeric_param):
  plt.figure(figsize=(16,4), tight_layout=True)
  colors = sns.color_palette('pastel')
  plottable = sad.groupby([categorical_x],as_index=False).agg({'title':'count',numeric_param:'mean'})
  plottable = plottable[plottable['title']>10]
  plt.bar(plottable[categorical_x], plottable[numeric_param], color=colors)
  plt.xlabel(categorical_x.title())
  plt.ylabel('Avg '+numeric_param)
  plt.title(numeric_param.title()+' based on '+categorical_x.title())
  plt.show()

#Bubble graph with two categorical axes and bubble size is occurrence
def bubble_with_categorical_mood(sad,categorical_x):
  plt.figure(figsize=(70,5), tight_layout=True)
  colors = sns.color_palette('Set2')
  plottable = sad.groupby([categorical_x,'mood_sorted','mood'],as_index=False).agg({'title':'count'})
  plottable = plottable[plottable['title']>20]
  plottable = plottable.sort_values(by='mood_sorted')
  plottable['title'] *= 3
  x_axis = categorical_x.title()
  plt.scatter(x=categorical_x, y="mood", s="title", data=plottable, color = colors[2])
  plt.xlabel(categorical_x)
  plt.ylabel('Mood')
  plt.title(x_axis+' vs Mood')
  plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
  plt.show()

#Line graph where y-axis is numeric and x-axis is yearmonth
def line_overtime(sad,numeric_line):
  plt.figure(figsize=(80,7), tight_layout=True)
  colors = sns.color_palette('Set2')
  plottable = sad.groupby(['yearmonth'], as_index=False).mean(numeric_line)
  plottable = plottable[['yearmonth',numeric_line]]
  smoothed = gaussian_filter1d(plottable[numeric_line], sigma=1.5)
  plt.plot(plottable['yearmonth'], smoothed,'ko-',color=colors[0], markersize=4)
  plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
  plt.xticks(rotation=90)
  plt.show()

#Line graph where x-axis is categorical
def line_with_categorical_x(sad,categorical_x,numeric_line):
  plt.figure(figsize=(70,5), tight_layout=True)
  colors = sns.color_palette('Set2')
  plottable = sad.groupby([categorical_x],as_index=False).agg({'title':'count',numeric_line:'mean'})
  plottable = plottable[plottable['title']>50]
  plottable = plottable.sort_values(by=numeric_line)
  smoothed = gaussian_filter1d(plottable[numeric_line], sigma=1.5)
  plt.plot(plottable[categorical_x], smoothed,'ko-',color=colors[1], markersize=4)
  plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
  if numeric_line=='score': y_axis = 'Mood score'
  else: y_axis = numeric_line
  plt.title(y_axis + ' vs ' + categorical_x)
  plt.show()


bar_with_categorical_numeric_avg(sad,'mood','tempo')
bar_with_categorical_numeric_avg(sad,'mood','length')

line_overtime(sad,'tempo')
line_overtime(sad,'length')
line_overtime(sad,'mood score')


#Mood count over time (line)
plot_time_mood = sad.groupby(['yearmonth','mood'], as_index=False)['title'].count()
plot_time_select = plot_time_mood[plot_time_mood['mood'].isin(['Sad','Happy','Angry','Excited'])]

def assignMood(olddf,moodname):
  newdf = olddf[olddf['mood']==moodname]
  newdf = newdf.rename(columns={'title': moodname})
  newdf = newdf.drop('mood', 1)
  return newdf

plot_time_happy = assignMood(plot_time_mood,'Happy')
plot_time_sad = assignMood(plot_time_mood,'Sad')
plot_time_angry = assignMood(plot_time_mood,'Angry')
plot_time_excited = assignMood(plot_time_mood,'Excited')
newdf = pd.merge(plot_time_happy,plot_time_sad,on='yearmonth',how='outer')
newdf = pd.merge(newdf,plot_time_angry,on='yearmonth',how='outer')
newdf = pd.merge(newdf,plot_time_excited,on='yearmonth',how='outer')
newdf = newdf.sort_values(by='yearmonth')
newdf = newdf.fillna(0)
newdf['HappyExcited'] = newdf['Happy']+newdf['Excited']
newdf['SadAngry'] = newdf['Sad']+newdf['Angry']
HE_smoothed = gaussian_filter1d(newdf['HappyExcited'], sigma=1.5)
SA_smoothed = gaussian_filter1d(newdf['SadAngry'], sigma=1.5)

plt.figure(figsize=(80,6), tight_layout=True)
colors = sns.color_palette('pastel')
line0 = plt.plot(newdf['yearmonth'], HE_smoothed,'ko-',label='Happy+Excited', color = colors[2], markersize=4)
line1 = plt.plot(newdf['yearmonth'], SA_smoothed,'ro-',label='Sad+Angry', color = colors[3], markersize=4)
plt.xticks(rotation=90)
plt.xlabel('Month')
plt.ylabel('# of times')
plt.title('Mood per month')
plt.legend(loc="upper left")
plt.show()

#Bubble graph for all
plt.figure(figsize=(80,6), tight_layout=True)
colors = sns.color_palette('Set2')
plot_time_score = sad.groupby(['yearmonth','mood'], as_index=False)['title'].count()
plot_time_score['title'] *= 30
plt.scatter(x="yearmonth", y="mood", s="title", data=plot_time_score, color = colors[0])
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.xticks(rotation=90)
plt.show()

#Moods over categories
bubble_with_categorical_mood(sad,'main instrument')
bubble_with_categorical_mood(sad,'location')

#Bubble graph for select /// NOT SAVED
plt.figure(figsize=(80,5), tight_layout=True)
colors = sns.color_palette('pastel')
plot_time_moodcount = sad.groupby(['yearmonth','mood'], as_index=False)['title'].count()
plot_time_moodcount = plot_time_moodcount[plot_time_moodcount['mood'].isin(['Happy','Excited','Angry','Sad'])]
plot_time_moodcount['title'] *= 40
plt.scatter(x="yearmonth", y="mood", s="title", data=plot_time_moodcount)
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.xticks(rotation=90)
plt.show()

#Mood score over categories
line_with_categorical_x(sad,'location','score')
line_with_categorical_x(sad,'location_grp','score')
line_with_categorical_x(sad,'main instrument','score')
line_with_categorical_x(sad,'main style','score')
line_with_categorical_x(sad,'topic','score')
line_with_categorical_x(sad,'inKey','score')
line_with_categorical_x(sad,'topic','length')
line_with_categorical_x(sad,'main instrument','length')



numeric_line = 'mood score'
plottable = sad.groupby(['yearmonth'], as_index=False).mean('mood score')
plottable = plottable[['yearmonth',numeric_line]]
smoothed1 = gaussian_filter1d(plottable[numeric_line], sigma=1.5)


plottable = sad.groupby(['yearmonth'],as_index=False).agg({'title':'count','mood score':'mean','tempo':'mean'})
smoothed1 = gaussian_filter1d(plottable['mood score'], sigma=1.5)
smoothed2 = gaussian_filter1d(plottable['tempo'], sigma=1.5)

colors = sns.color_palette('Set2')
fig, ax = plt.subplots(figsize=(12,5))
ax2 = ax.twinx()
ax.plot(plottable['yearmonth'], smoothed1,'ko-',color=colors[0], markersize=4)
ax2.plot(plottable['yearmonth'], smoothed2,'ko-',color=colors[1], markersize=4)
plt.show()



plt.xlabel(categorical_x)
plt.ylabel('Mood')
plt.title(x_axis+' vs Mood')
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
