#!/usr/bin/env python

import os
import pandas as pd
import sys
from viz_helper_functions import transcript_wordcloud

# NOTE: Referencing paths defined in `phone_diary_viz.sh`
study_loc = os.environ['study_loc']
transcripts_loc = os.environ['transcripts_loc']
audio_qc_loc = os.environ['audio_qc_loc']

def transcript_wordclouds(study, OLID):
	# switch to specific patient folder - transcript CSVs
	try:
		os.chdir(study_loc + study + "/" + OLID + transcripts_loc + "csv")
	except:
		print("Problem with input arguments", flush=True) # should never reach this error if calling via bash module
		return

	print("Generating daily transcript wordclouds for " + OLID, flush=True)
	
	metadata = pd.read_csv(f'{study_loc}{study}/{OLID}{audio_qc_loc}{study}_{OLID}_metadataWithWeek.csv')

	for r in range(metadata.shape[0]):  # Iterate through rows 
		transcript_path = metadata['transcript_name'].iloc[r]
		try:
			cur_trans = pd.read_csv(transcript_path)
		except:
			print("Problem loading " + transcript_path, flush=True)
			continue

		week = metadata['week'].iloc[r]
		period = metadata['period'].iloc[r] 
		acad_cal_day = int(float(metadata['acad_cal_day'].iloc[r])) # Cast day to int
		word_count = int(float(metadata['num_words'].iloc[r]))

		plot_outpath = f'../../visualizations/wordclouds/transcript_level_wordclouds/plots/{study}_{OLID}_phoneAudioDiary_transcript_wordCloud_acadday{acad_cal_day}.png'
		table_outpath = f'../../visualizations/wordclouds/transcript_level_wordclouds/tables/{study}_{OLID}_phoneAudioDiary_transcript_wordFrequencies_acadday{acad_cal_day}.csv'

		title = f'{OLID}: Week {week}, {period}, Acad Day {acad_cal_day} (Word Count = {word_count})'

		
		if not os.path.exists(plot_outpath):
			# only create if doesn't already exist for this transcript (as can be a somewhat time intensive process)
			try:
				transcript_wordcloud(cur_trans, plot_outpath, table_outpath, verbose=True, title=title)
				# note that sometimes multiple words with a space between will be considered as one word, seemingly inexplicably
				# this happens infrequently enough that it is not worth the time to troubleshoot currently
				# instead simply color the "word" as blue instead of on the normal red/black/green colorscale
				# (see transcript_wordcloud function for more details)
			except Exception as e:
				print("Function crashed on " + transcript_path)
				print(e)
				continue
	



'''
Takes a list of files in a week and generates a week-level word cloud of the transcripts. 
Notice! This function is called by `agg` method, thus does not have access to global variables. 
'''
def wordcloud_per_week(weekly_files: list):
	concat_result = pd.DataFrame()	# stores concatonated transcripts
	acad_days = []
	total_word_count = 0
	periods = set()

	# looping through files in a week, and parsing out key information 
	for week, period, acad_cal_day, num_words, transcript_name in weekly_files:
		study = transcript_name.split('_')[0] + '_' + transcript_name.split('_')[1]
		subject = transcript_name.split('_')[2] 
		f = pd.read_csv(transcript_name)
		concat_result = pd.concat([concat_result, f], axis=0)  # concat transcripts from the same week 
		acad_days.append(int(float(acad_cal_day)))
		total_word_count += num_words
		periods.add(period)

	num_files = len(weekly_files) # total avaliable transcirpts 
	avg_word_count = round(total_word_count / num_files) # get words per transcript 

	periods.discard("Regular term")
	if len(periods) == 0:
		special_period = "Regular term"
	else:
		special_period = ','.join(periods)

	plot_outpath = f'../../visualizations/wordclouds/week_level_wordclouds/plots/{study}_{subject}_phoneAudioDiary_transcript_wordCloud_week{week}.png'
	table_outpath = f'../../visualizations/wordclouds/week_level_wordclouds/tables/{study}_{subject}_phoneAudioDiary_transcript_wordFrequencies_week{week}.csv'

	title = f'{subject}: Week {week}, {special_period}, Acad Days {acad_days[0]}-{acad_days[-1]} ({num_files} Transcripts Available; Avg Word Count = {avg_word_count})'
	# actually plotting 
	transcript_wordcloud(concat_result, plot_outpath, table_outpath, verbose=True, title=title)


'''
Week-level transcript wordclouds. 
week is defined by days into academic year. 
'''
def weeklevel_transcript_wordclouds(study, OLID):
	# switch to specific patient folder - transcript CSVs
	try:
		os.chdir(study_loc + study + "/" + OLID + transcripts_loc + "csv")
	except:
		print("Problem with input arguments") # should never reach this error if calling via bash module
		return

	print("Generating weekly transcript wordclouds for " + OLID, flush=True)

	metadata = pd.read_csv(f'{study_loc}{study}/{OLID}{audio_qc_loc}{study}_{OLID}_metadataWithWeek.csv')

	# To use `agg` method, gather title info into one column. 
	metadata['plot_title'] = metadata[['week', 'period', 'acad_cal_day', 'num_words', 'transcript_name']].values.tolist()

	metadata[['week', 'plot_title']].groupby('week').agg(wordcloud_per_week)


"""
Pads academic calendar days to a full range. 
Adds week number inforrmation to a given metadata data frame. 
"""
def acad_cal_days_and_weeks(metadata):
	# generating a full academic days and weeks df
	acad_cal_days = []
	week = [1]*5
	# Declare a list that is to be converted into a column
	for i in range (1, 280): 
		acad_cal_days.append(i)

	for j in range (2, 42):
		temp = [j] * 7
		week += temp

	week_info = metadata['subject']
	df1 = pd.DataFrame({"acad_cal_day": acad_cal_days})
	df2 = pd.DataFrame({"week": week})
	week_info = pd.concat([week_info, df1, df2], axis=1)

	return week_info


"""
Create a file called mmetadataWithWeek.csv
"""
def add_week(study, OLID):
	# Get the all_features file 
	all_features_path = study_loc + study + "/" + OLID + audio_qc_loc + study + "_" + OLID + "_phoneAudioDiary_allFeatures.csv"
	metadata = pd.read_csv(all_features_path)

	week_info = acad_cal_days_and_weeks(metadata)  # generating a full academic days and weeks df
	metadata = pd.merge(week_info, metadata, on=['subject', 'acad_cal_day'], how='left')

	metadata.dropna(inplace=True)	# remove days with missing data
	metadata = metadata[metadata.unavailable_diary == 0]	 # drop unavailable diaries  
	metadata.to_csv(f'{study_loc}{study}/{OLID}{audio_qc_loc}{study}_{OLID}_metadataWithWeek.csv')


if __name__ == '__main__':
	## Map command line arguments to function arguments.
	add_week(sys.argv[1], sys.argv[2])
	transcript_wordclouds(sys.argv[1], sys.argv[2])
	weeklevel_transcript_wordclouds(sys.argv[1], sys.argv[2])
