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
for p in *; do # loop over all patients in the specified study folder on PHOENIX
	# first check that it is truly an OLID that has previouly processed audio
	if [[ ! -e ${p}/phone/processed/audio/${study}_${p}_phone_audio_ETFileMap.csv ]]; then
		continue
	fi
	cd "$p"/phone/processed/audio

	# then check that there are some newly decrypted files available to process
	if [[ ! -d decrypted_files ]]; then
		cd $study_loc/"$study" # back out of folder before skipping over patient
		continue
	fi
	if [ -z "$(ls -A decrypted_files)" ]; then
		cd $study_loc/"$study" # back out of folder before skipping over patient
		continue
	fi

	# if good to go, setup relevant folders for the VAD outputs
	# first the temp audio output folder that needs to be created every time
	mkdir decrypted_files/foreground_audio
	# then the permanent output folders in the case that they don't already exist (new patient)
	if [[ ! -d vad_spectrogram_comparisons ]]; then
		mkdir vad_spectrogram_comparisons
	fi
	if [[ ! -d opensmile_features_filtered ]]; then
		mkdir opensmile_features_filtered
	fi
	
	# now finally run script on this patient
	python "$func_root"/phone_audio_vad.py "$study" "$p"

	# back out of folder before continuing to next patient
	cd $study_loc/"$study"

	# foreground_audio will be deleted as part of the main pipeline script, when the decrypted_files folder is deleted
	# when running this module stand alone, will be up to user to deal with decrypted files manually
done