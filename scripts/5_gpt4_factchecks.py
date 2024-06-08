# This script compares embedded radio transcripts and fact-checks,
# returning a CSV file of potential misinformation

# ensure libretranslate is running on port 5000 before running this script

import pandas as pd
import os
import numpy as np
from pathlib import Path
from ast import literal_eval
from openai import OpenAI
from libretranslatepy import LibreTranslateAPI

number_return_values = 1

# add your OpenAI API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

transcript_json= Path().cwd().parent.joinpath('data/output_json/transcript.json')

print('Importing transcript json...')

transcript_df = pd.read_json(transcript_json)

print('Organizing data...')

exploded_transcript_df = transcript_df.explode('transcription').reset_index(drop=True)

exploded_transcript_df = exploded_transcript_df[['file_name', 'transcription']]

embedded_false_statements_path = Path().cwd().parent.joinpath('data/factchecked_statements/embedded_false_statements.csv')

print("Importing false statements with embeddings...")

false_text_df = pd.read_csv(embedded_false_statements_path)

false_text_df['statement_embedding'] = false_text_df.statement_embedding.apply(eval).apply(np.array)

false_text_df['statement'] = false_text_df['statement'].replace('\'', '').replace('\"', '').replace('\"', '').replace('.','').replace('?','').replace('!','')

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(vec1, vec2):
    # Normalize each vector to unit length
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
  
    # Calculate dot product between normalized vectors
    similarity = np.dot(vec1_norm, vec2_norm)
    return similarity

def search_false_statements(search_terms,false_text_df=false_text_df, n=1):
   embedding = get_embedding(search_terms, model='text-embedding-3-small')
   false_text_df['similarities'] = false_text_df.statement_embedding.apply(lambda x: cosine_similarity(x, embedding))
   results = (
      false_text_df.sort_values("similarities", ascending=False).head(n)
   )
   return results

top_matches_json = []

def search_all_transcripts():
    errors = 0
    for row in exploded_transcript_df.itertuples(name='segment'):
        match_index = row.Index
        try:
            results = search_false_statements(row.transcription)
            top_match = results.statement.values
            similarity = results.similarities
            top_matches = {}
            top_matches["index"] = f"{match_index}"
            top_matches["filename"] = row.file_name
            top_matches["input_statement"] = row.transcription
            top_matches["checked_false_statement"] = f"{top_match}"
            top_matches["similarity"] = f"{similarity}"
            top_matches_json.append(top_matches)
            print_text = f"Finished checking {match_index + 1} of {len(exploded_transcript_df)} statements -- {int((match_index + 1)/len(exploded_transcript_df)*100)}% complete         "
            print("\r", print_text, end="")
        except:
            errors += 1
            print(f"Error checking statement {match_index + 1}")
    print(f"Finished checking all statements with {errors} error(s)")

print("Starting search of all transcripts...")

search_all_transcripts()

print("Creating DataFrame...")

top_matches_df = pd.DataFrame(top_matches_json)

top_matches_df['similarity_value'] = top_matches_df['similarity'].apply(lambda x: x.split()[1]).astype(float)
top_matches_df['factcheck_index'] = top_matches_df['similarity'].apply(lambda x: x.split()[0])

over_50 = top_matches_df.loc[top_matches_df['similarity_value'] >= .5]

over_50 = over_50.sort_values('similarity_value', ascending=False)

over_50 = over_50[['filename', 'input_statement', 'checked_false_statement', 'similarity_value', 'factcheck_index']]

over_50_csv_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation.csv')

print("Generating csv file...")

over_50.to_csv(f"{over_50_csv_filepath}")


print("Adding translation...")

lt = LibreTranslateAPI("http://localhost:5000")

def libretranslate_spanish(input_text):
    return lt.translate(f"{input_text}", "es", "en")

def libretranslate_french(input_text):
    return lt.translate(f"{input_text}", "fr", "en")

try:
    over_50['translation'] = over_50['input_statement'].apply(lambda x: libretranslate_french(x))
    over_50['translation'] = over_50['translation'].apply(lambda x: libretranslate_spanish(x))

    over_50 = over_50.sort_values('similarity_value', ascending=False)

    over_50 = over_50[['filename', 'input_statement', 'translation', 'checked_false_statement', 'similarity_value', 'factcheck_index']]

except:
    print("Failed to add transcription. Check that LibreTranslate is running.")

print("Generating csv file...")

translation_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_translations.csv')

over_50.to_csv(f"{translation_filepath}")