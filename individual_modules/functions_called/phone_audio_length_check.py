#!/usr/bin/env python

import os
import sys
import glob
import pandas as pd
import numpy as np

def audio_length_check(study, length_limit):
	try:
		length_limit = float(length_limit) # convert to a valid number
	except:
		print("Problem with length limit argument " + str(length_limit) + ", exiting")
		sys.exit(0) # exit with status fine error code so doesn't prevent later steps of code if invalid limit was supplied

	# get paths of interest for all patients in this study
	try:
		os.chdir("$study_loc/" + study)
	except:
		print("Problem with study argument " + study + ", exiting")
		sys.exit(0) # exit with status fine error code, so doesn't prevent later steps of code (although would likely fail anyway if study argument is wrong here)
	path_to_send = "*/phone/processed/audio/to_send"
	send_folders_list = glob.glob(path_to_send)
	send_paths_list = []
	for folder in send_folders_list:
		send_paths_list.extend(os.listdir(folder))

	# loop through all file to send audio paths, load DPDash audio QC CSV for each patient to count up the total length in minutes
	num_minutes = 0.0
	for filep in send_paths_list:
		# find dpdash path from file path
		try:
			filen = filep.split("/")[-1]
			OLID = filen.split("_")[1]
			# get day number from file name, to assist in lookup of df
			day_num = int(filen.split("day")[1].split(".")[0])
		except:
			print("Problem with filename " + filen + ", continuing")
			continue # skip in case any improperly formatted filenames come around

		try:
			os.chdir("$study_loc/" + study + "/" + OLID + "/phone/processed/audio")
		except:
			print("Problem with processed audio folder for " + OLID + ", continuing")
			continue

		dpdash_name_format = study + "-" + OLID + "-phoneAudioQC-day1to*.csv"
		try:
			dpdash_name = glob.glob(dpdash_name_format)[0] # DPDash script deletes any older days in this subfolder, so should only get 1 match each time
			dpdash_qc = pd.read_csv(dpdash_name) 
			# technically reloading this CSV for each file instead of for each patient, but should be a fast operation because CSV is small
			# also shouldn't be repeated that much in a normal run, as there cannot be more new uploads for a single patient than the number of days since the last run of the pipeline
		except:
			# patient should always have a dpdash CSV if has files in to_send, but to prevent overall crashing skip over patients in case DPDash part does fail
			print("Problem with DPDash CSV for " + OLID + ", continuing")
			continue
	
		try:
			# should always be exactly one matching entry, as only allowing one file into DPDash per day (first submitted)
			cur_row = dpdash_qc[dpdash_qc["day"]==day_num] 
			# then get total time of that particular recording (in minutes)
			cur_count = float(cur_row["length(minutes)"].tolist()[0])
		except:
			# again should never reach the error as should always be a day in the DPDash CSV for a day found here, but just to be safe!
			print(filen + " is missing a record in  the DPDash CSV for " + OLID + ", continuing")
			continue

		# update total count across the entire study
		num_minutes = num_minutes + cur_count

	if num_minutes > length_limit:
		print("Total minutes (" + str(num_minutes) + ") exceeds limit (" + str(length_limit) + "), so auto transcription will be paused")
		sys.exit(1) # exit with error code so bash script knows to not send the files
	else:
		sys.exit(0) # exit with no problem otherwise

if __name__ == '__main__':
	# Map command line arguments to function arguments.
	try:
		study_inp = sys.argv[1]
		length_inp = sys.argv[2]
	except:
		print("Invalid arguments")
		sys.exit(0) # exit with okay status, as won't prevent sending unless explicit length argument was supplied
	audio_length_check(study_inp, length_inp) # need to run without a try/catch so exit 1 will actually work!
