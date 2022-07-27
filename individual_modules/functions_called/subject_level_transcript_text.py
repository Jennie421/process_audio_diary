
import os
import pandas as pd
import sys
from viz_helper_functions import transcript_wordcloud


study_loc = os.environ['study_loc']
transcripts_loc = os.environ['transcripts_loc']
audio_qc_loc = os.environ['audio_qc_loc']
daily_text_loc = os.environ['daily_text_loc']


'''
Subject-level transcript wordclouds. 
Already in transcript_level_wordcloud/tables folder. 
'''
def subjectlevel_transcript_wordclouds(study, OLID):
    # switch to specific patient folder - transcript CSVs

    try:
        os.chdir(os.getcwd() + daily_text_loc)
    except Exception as e:
        print(e, flush=True) # should never reach this error if calling via bash module
        return

    print("Generating subject-level transcript text for " + OLID, flush=True)

    cur_daily_text = pd.read_csv(f'{study}_{OLID}_dailyText.csv')

    cur_full_text = "".join(cur_daily_text['text'])

    full_text_df = pd.DataFrame({'doc_id': [OLID], 'text': [cur_full_text]})
    
    study_text_path = f'{study_loc}/topicModeling/{study}_subjectText.csv'

    try:  
        metadata = pd.read_csv(study_text_path)
        metadata = metadata.append(full_text_df, ignore_index = True)
        print("appending data of subject "+ OLID, flush=True)
    except:
        metadata = full_text_df
        print("new data of subject "+ OLID, flush=True)
    
    metadata.to_csv(study_text_path, index=False)


if __name__ == '__main__':
    subjectlevel_transcript_wordclouds(sys.argv[1], sys.argv[2])