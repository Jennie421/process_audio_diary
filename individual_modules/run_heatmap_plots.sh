#!/bin/bash

# this is one of a set of wrapping bash scripts that allow the python scripts to be called on all patients in a given study
# it is called by the main pipeline (visualization portion), but can also be used in a modular fashion
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

# first check that it is truly an OLID, that has previouly processed audio
if [[ ! -d $p/phone/processed/audio ]]; then
	"No proper file structure, skipping"
	continue
fi
cd "$p"/phone/processed/audio


# Cony & Jennie's organization 
if [[ ! -d transcripts/visualizations/ ]]; then
	mkdir transcripts/visualizations/
fi
# make a heatmaps subfolder if it doesn't already exist
if [[ ! -d transcripts/visualizations/heatmaps/ ]]; then
	mkdir transcripts/visualizations/heatmaps/
fi

# check that there is an audio QC CSV to use, if so run the heatmap generation script (for audio and transcript combined!)
# Now the file also contains NLP features. 
if [[ -n $(shopt -s nullglob; echo *_phoneAudioDiary_allFeatures.csv) ]]; then
	python "$func_root"/phone_diary_qc_heatmaps.py "$study" "$p"
else 
	echo "Combined QC file not found (check if filename/path is correct in run_heatmap_plots.sh)"
fi

# back out of folder before continuing to next patient
cd $study_loc/"$study"
