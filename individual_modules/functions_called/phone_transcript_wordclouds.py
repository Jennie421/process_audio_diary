#!/usr/bin/env python

import os
import pandas as pd
import sys
from viz_helper_functions import transcript_wordcloud

# NOTE: Modify the paths in `phone_transcript_processes.sh`
study_loc = os.environ['study_loc']
transcripts_loc = os.environ['transcripts_loc']
transcript_qc_loc = os.environ['transcript_qc_loc']

def transcript_wordclouds(study, OLID):
	# switch to specific patient folder - transcript CSVs
	try:
		os.chdir(study_loc + study + "/" + OLID + transcripts_loc + "csv")
	except:
		print("Problem with input arguments") # should never reach this error if calling via bash module
		return

	print("Generating transcript wordclouds for " + OLID)
	transcript_paths = os.listdir(".")
	for transcript_path in transcript_paths:
		try:
			cur_trans = pd.read_csv(transcript_path)
		except:
			print("Problem loading " + transcript_path)
			continue
		out_path = "../../visualizations/wordclouds/" + transcript_path.split(".")[0] + "_wordcloud.png"
		title = OLID + transcript_path.split(".")[0].split('_')[-1]
		
		if not os.path.exists(out_path):
			# only create if doesn't already exist for this transcript (as can be a somewhat time intensive process)
			try:
				transcript_wordcloud(cur_trans, out_path, verbose=True, title=title)
				# note that sometimes multiple words with a space between will be considered as one word, seemingly inexplicably
				# this happens infrequently enough that it is not worth the time to troubleshoot currently
				# instead simply color the "word" as blue instead of on the normal red/black/green colorscale
				# (see transcript_wordcloud function for more details)
			except Exception as e:
				print("Function crashed on " + transcript_path)
				print(e)
				continue
	


# def helper(weekly_trans, weekdays, days):
# 	out_path = "../../visualizations/wordclouds/" + "days " + days[0] + " to " + days[-1] + "_wordcloud_weeklevel.png"
# 	title = OLID + transcript_path.split(".")[0].split('_')[-1]
	
# 	if not os.path.exists(out_path):
# 		# only create if doesn't already exist for this transcript (as can be a somewhat time intensive process)
# 		try:
# 			transcript_wordcloud(cur_trans, out_path, verbose=True, title=title)
# 			# note that sometimes multiple words with a space between will be considered as one word, seemingly inexplicably
# 			# this happens infrequently enough that it is not worth the time to troubleshoot currently
# 			# instead simply color the "word" as blue instead of on the normal red/black/green colorscale
# 			# (see transcript_wordcloud function for more details)
# 		except Exception as e:
# 			print("Function crashed on " + transcript_path)
# 			print(e)
	

'''
Week-level transcript wordclouds. 
week is defined by days into academic year. 
'''
# def weeklevel_transcript_wordclouds(study, OLID):
# 	# switch to specific patient folder - transcript CSVs
# 	try:
# 		os.chdir(study_loc + study + "/" + OLID + transcripts_loc + "csv")
# 	except:
# 		print("Problem with input arguments") # should never reach this error if calling via bash module
# 		return

# 	print("Generating transcript wordclouds for " + OLID)


# 	# Get the combined qc file containing day, filename, and late submission. 
# 	df_info_path = study_loc + study + "/" + OLID + transcript_qc_loc + study + "_" + OLID + "_AudioTranscriptQCmerged.csv"
# 	df_info = pd.read_csv(df_info_path)

# 	weekly_trans = pd.DataFrame
# 	weekdays, days = [], []
# 	last_day = df_info['day'].iloc[-1]

# 	for i in range(len(df_info.index)) :

# 		if df_info['has_na'][i] == 1: # Skip missing data
# 			continue 

# 		cur_trans_name = df_info['transcript_name'][i]
# 		try: 
# 			cur_trans = pd.read_csv(cur_trans_name)
# 		except:
# 			print("Problem loading " + cur_trans_name)
# 			continue

# 		cur_weekday = df_info['weekday_num'][i]
# 		cur_day = df_info['day'][i]
		
# 		# if entered a new week, wrap up previous week and append the new one
# 		if weekdays and cur_weekday <= weekdays[-1]: 
# 			helper(weekly_trans, weekdays, days)
# 			# RESET
# 			weekly_trans = pd.DataFrame
# 			weekdays, days = [], []

# 		weekly_trans = pd.concat([weekly_trans, cur_trans], ignore_index=True, sort=False)
# 		weekdays.append(cur_weekday)
# 		days.append(cur_day)

# 		# if reached last day, or reached the end of a week, wrap up this week 
# 		if df_info['day'][i] == last_day or (cur_weekday >= df_info['weekday_num'][i+1]): # or (df_info['assigned_date'][i+i] - df_info['assigned_date'][i] > 7 )
# 			helper(weekly_trans, weekdays, days)

# 			weekly_trans = pd.DataFrame
# 			weekdays, days = [], []




if __name__ == '__main__':
    ## Map command line arguments to function arguments.
    transcript_wordclouds(sys.argv[1], sys.argv[2])
	# weeklevel_transcript_wordclouds(sys.argv[1], sys.argv[2])
