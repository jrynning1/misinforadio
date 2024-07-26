# This script compares embedded radio transcripts and fact-checks,
# returning a CSV file of potential misinformation

# ensure libretranslate is running on port 5000 before running this script

import pandas as pd
import os
import numpy as np
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# add your OpenAI API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

transcript_json= Path().cwd().parent.joinpath('data/output_json/transcript.json')

print('Importing transcript json...')

transcript_df = pd.read_json(transcript_json)

print('Organizing data...')

exploded_transcript_df = transcript_df.explode('transcription').reset_index(drop=True)

exploded_transcript_df = exploded_transcript_df[['file_name', 'transcription']]

"""

# NEED TO WORK ON NORMALIZING SEGMENT LENGTH

exploded_transcript_df["transcription_before"] = exploded_transcript_df['transcription'].shift(1, fill_value=' ')

exploded_transcript_df['transcription_after'] = exploded_transcript_df['transcription'].shift(-1, fill_value=' ')

exploded_transcript_df['transcription_with_context'] = exploded_transcript_df['transcription_before'] + " " + exploded_transcript_df['transcription'] + " " + exploded_transcript_df['transcription_after']

exploded_transcript_df['transcription_with_context'] = exploded_transcript_df['transcription_with_context'].apply(lambda x: x.strip())

"""

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

transcription_embeddings_list = []
counter = 0
for segment in exploded_transcript_df['transcription']:
    print_text = f"Embedding segment {counter} of {len(exploded_transcript_df['transcription'])} segments -- {int((counter)/len(exploded_transcript_df['transcription'])*100)}% complete         "
    print("\r", print_text, end="")
    try:
        embedding = get_embedding(segment)
    except:
        embedding = 0
        print(f"Failed to generate embedding for segment {counter} of {len(exploded_transcript_df['transcription'])}")
    transcription_embeddings_list.append(embedding)
    counter += 1

exploded_transcript_df['transcription_embedding'] = transcription_embeddings_list

"""

# ADDITIONAL SEGMENT LENGTH NORMALIZING

transcription_with_context_embeddings_list = []
counter = 0
for segment in exploded_transcript_df['transcription_with_context']:
    print_text = f"Embedding context segment {counter} of {len(exploded_transcript_df['transcription_with_context'])} segments -- {int((counter)/len(exploded_transcript_df['transcription_with_context'])*100)}% complete         "
    print("\r", print_text, end="")
    try:
        embedding = get_embedding(segment)
    except:
        embedding = 0
        print(f"Failed to generate embedding for context segment {counter} of {len(exploded_transcript_df['transcription'])}")
    transcription_with_context_embeddings_list.append(embedding)
    counter += 1

exploded_transcript_df['transcription_with_context_embedding'] = transcription_with_context_embeddings_list
"""

embedded_transcripts_path = embedded_false_statements_path = Path().cwd().parent.joinpath('data/embedded_transcripts/embedded_transcripts.csv')

exploded_transcript_df.to_csv(embedded_transcripts_path)

