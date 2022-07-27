
import os
import pandas as pd
import sys

study_loc = os.environ['study_loc']
audio_qc_loc = os.environ['audio_qc_loc']
transcript_qc_loc = os.environ['transcript_qc_loc']
NLP_loc = os.environ['NLP_loc']

def generate_subject_metadata(study, OLID):
	
	try:
		os.chdir(study_loc + study + "/" + OLID + audio_qc_loc) # NOTE: variable inplace of hardcoded string

	except Exception as e:
		print("Problem with path, or no processed audio for this patient yet") # should never reach this error if calling via bash module
		print(e)
		return


	# MERGE AUDIO QCs
	file_data = pd.read_csv(study + "_" + OLID + "_phoneAudioDiary_fileMetadata_timezoneCorrected.csv") 
	audio_qc = pd.read_csv(study + "_" + OLID + "_phoneAudioDiary_QC.csv")

	# using merge function by setting how='left'
	audioQCmerged = pd.merge(file_data, audio_qc, on=['filename'], how='left')

	# add column "transcript_name"
	audioQCmerged['transcript_name'] = audioQCmerged.apply(lambda row: str(row.filename).split(".")[0] + ".csv", axis=1)

	# MERGE TRANSCRIPT QC
	transcript_QC = pd.read_csv(study_loc + study + "/" + OLID + transcript_qc_loc + study + "_" + OLID + "_phoneAudioDiary_transcript_QC.csv")
	AudioTranscriptQCmerged = pd.merge(audioQCmerged, transcript_QC, on=['transcript_name'], how='left')

	# MERGE NLP SUMMARY
	NLP_summary = pd.read_csv(study_loc + study + "/" + OLID + NLP_loc + study + "_" + OLID + "_phoneAudioDiary_transcript_NLPFeaturesSummary.csv")
	NLP_summary.rename(columns={"filename": "transcript_name"}, inplace=True)
	all_features = pd.merge(AudioTranscriptQCmerged, NLP_summary, on=['transcript_name'], how='left')
	
	# save this file 
	print("saving all features", flush=True)
	all_features.to_csv(study + "_" + OLID + "_phoneAudioDiary_allFeatures.csv")

if __name__ == '__main__':
	## Map command line arguments to function arguments.
	generate_subject_metadata(sys.argv[1], sys.argv[2])