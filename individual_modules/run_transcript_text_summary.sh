#!/bin/bash

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


# actually start running the main computations

if [[ ! -d $study_loc/topicModeling ]]; then
	mkdir -p $study_loc/topicModeling # create output folder if there isn't already
fi


# Remove old metadata file if exists. Avoid concatonation error. 
if [[ -f $study_loc/topicModeling/FRESH_17_subjectText.csv ]]; then
	rm $study_loc/topicModeling/FRESH_17_subjectText.csv
	echo "removing old metadata"
fi


cd $study_loc/"$study"

for subject in *; do 
	
	cd $subject

	python "$func_root"/subject_level_transcript_text.py "$study" "$subject"

	echo "Completed analysis for $subject"

	cd ../
	
done