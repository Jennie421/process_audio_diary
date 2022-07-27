#!/bin/bash

# this is one of a set of wrapping bash scripts that allow the python scripts to be called on all patients in a given study
# it is called by the main pipeline, but can also be used in a modular fashion
# if wanting to run the components of the pipeline on a single patient instead, the python scripts can be called directly
# this script could also be modified to run on only a subset of patients by adding additional checks into the loop over patients below

# setup:
# if called by pipeline will have study variable already set, but to allow modular usage prompt for study of interest if variable is unset
if [[ -z "${study}" ]]; then
	echo "Module called stand alone, prompting for necessary settings:"
	echo "Study of interest?"
	echo "(should match PHOENIX study name, validated options are BLS and DPBPD)"
	read study

	# sanity check provided answer, it should at least exist on PHOENIX
	if [[ ! -d $study_loc/$study ]]; then
		echo "invalid study id"
		exit
	fi

	echo ""
	echo "Beginning script for study:"
	echo "$study"
	echo ""
fi
# similarly, need to check for repo path, use it to define expected python script path
if [[ -z "${repo_root}" ]]; then
	# if don't have the variable, repeat similar process to get directory this script is in, which should be under individual_modules subfolder of the repo
	full_path=$(realpath $0)
	repo_root=$(dirname $full_path)
	func_root="$repo_root"/functions_called
else
	func_root="$repo_root"/individual_modules/functions_called
fi

# body:
# actually start running the main computations
cd $study_loc/"$study"

# first check that it is truly an OLID that has previous transcripts
if [[ ! -d $p/$transcripts_loc/csv ]]; then
	continue
fi
cd "$p"/$transcripts_loc
# confirm there are csvs in the folder, not just that it exists
if [ -z "$(ls -A csv)" ]; then
	cd $study_loc/"$study" # back out of folder before skipping over patient
	continue
fi


# setup folder for the individual transcript outputs
# NOTE: path modified according to Cony & Jennie's organization 
if [[ ! -d $study_loc/"$study"/"$p"/phone/processed/audio/transcripts/NLP_features/ ]]; then
	mkdir $study_loc/"$study"/"$p"/phone/processed/audio/transcripts/NLP_features/
fi

csv_with_features_path=$study_loc/"$study"/"$p"/phone/processed/audio/transcripts/NLP_features/csv_with_features
export csv_with_features_path

# setup folder for the individual transcript outputs
if [[ ! -d $csv_with_features_path ]]; then
	mkdir $csv_with_features_path
fi

# check if all CSVs so far have been processed - if so don't actually run!
# (note this means that if new features are added old outputs will need to be cleared and code ran from the start again)
new_files=$(diff <(ls -1a csv) <(ls -1a $csv_with_features_path))
if [[ -z "${new_files}" ]]; then # if diff of file names of these directories is empty
	cd $study_loc/"$study" # back out of folder before skipping over patient
	# continue  # Only meaningful in a loop, no longer needed 
fi

# now run script on this patient
python "$func_root"/phone_transcript_nlp.py "$study" "$p"

# back out of folder for next loop
cd $study_loc/"$study"