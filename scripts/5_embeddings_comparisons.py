# This script compares embedded radio transcripts and fact-checks,
# returning a CSV file of potential misinformation

# ensure libretranslate is running on port 5000 before running this script

import pandas as pd
import os
import numpy as np
from pathlib import Path
from openai import OpenAI
from libretranslatepy import LibreTranslateAPI

print("Enter LibreTranslate language code -- \"es\" for spanish, \"fr\" for french, etc.")
input_language = input()

number_return_values = 1

# add your OpenAI API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

embedded_transcripts_path= Path().cwd().parent.joinpath('data/embedded_transcripts/embedded_transcripts.csv')


print('Importing embedded transcripts...')

transcript_df = pd.read_csv(embedded_transcripts_path)

# there is something wrong with at least one embedding, and I need to figure out how to either skip it or make it work
# it may be from assigning errors as NaN in the other script; may have to change that to 0 or something
transcription_embedding_list = []
for embedding in transcript_df['transcription_embedding']:
    try:
        transcription_embedding_array = np.array(eval(embedding))
        transcription_embedding_list.append(transcription_embedding_array)
    except:
        transcription_embedding_list.append(0)
transcript_df['transcription_embedding'] = transcription_embedding_list

transcription_embedding_list = []
for embedding in transcript_df['transcription_with_context_embedding']:
    try:
        transcription_embedding_array = np.array(eval(embedding))
        transcription_embedding_list.append(transcription_embedding_array)
    except:
        transcription_embedding_list.append(0)
transcript_df['transcription_with_context_embedding'] = transcription_embedding_list

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

print("Importing false statements with embeddings...")

embedded_false_statements_path = Path().cwd().parent.joinpath('data/factchecked_statements/embedded_false_statements.csv')

false_text_df = pd.read_csv(embedded_false_statements_path)

statement_embedding_list = []
for embedding in false_text_df['statement_embedding']:
    try:
        statement_embedding_array = np.array(eval(embedding))
        statement_embedding_list.append(statement_embedding_array)
    except:
        statement_embedding_list.append(0)

false_text_df['statement_embedding'] = statement_embedding_list


def cosine_similarity(vec1, vec2):
    # Normalize each vector to unit length
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
  
    # Calculate dot product between normalized vectors
    similarity = np.dot(vec1_norm, vec2_norm)
    return similarity


# if the transcript segment is shorter than 150 characters, this will use the context segment instead
def search_false_statements(search_terms,false_text_df=false_text_df, n=1):
    transcription_similarity_list = []
    transcription_embedding = search_terms.transcription_embedding
    transcription_embedding_array = np.array(transcription_embedding)
    context_embedding = search_terms.transcription_with_context_embedding
    context_embedding_array = np.array(context_embedding)
    transcription = search_terms.transcription
    errors = 0
# is receiving embeddings above
    if len(transcription) > 150:
        for embedding in statement_embedding_list:
            try:
                transcription_similarity = cosine_similarity(embedding, transcription_embedding_array)
                transcription_similarity_list.append(transcription_similarity)
            except:
                errors += 1
                transcription_similarity_list.append("failed to generate similarity")
    else:
        for embedding in statement_embedding_list:
            try:
                transcription_similarity = cosine_similarity(embedding, context_embedding_array)
                transcription_similarity_list.append(transcription_similarity)
            except:
                errors += 1
                transcription_similarity_list.append("failed to generate similarity")
    # print(f"Searched false statements with {errors} errors.")
    false_text_df['similarities'] = transcription_similarity_list
    results = (
        false_text_df.sort_values("similarities", ascending=False).head(n)
    )
    return results

top_matches_json = []

def search_all_transcripts():
    errors = 0
    for row in transcript_df.itertuples():
        match_index = row.Index
        try:
            match_index = row.Index
            results = search_false_statements(row)
            top_match = results.statement.values
            similarity = results.similarities
            top_matches = {}
            top_matches["index"] = f"{match_index}"
            top_matches["filename"] = row.file_name
            top_matches["input_statement"] = row.transcription
            top_matches["checked_false_statement"] = f"{top_match}"
            top_matches["similarity"] = f"{similarity}"
            top_matches_json.append(top_matches)
            print_text = f"Finished checking {match_index + 1} of {len(transcript_df)} statements -- {int((match_index + 1)/len(transcript_df)*100)}% complete         "
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

over_50_csv_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_context.csv')

print("Generating csv file...")

over_50.to_csv(f"{over_50_csv_filepath}")

print("Enter LibreTranslate language code -- \"es\" for spanish, \"fr\" for french, etc.")
input_language = input()

print("Adding translation...")

lt = LibreTranslateAPI("http://localhost:5000")

def libretranslate_spanish(input_text):
    return lt.translate(f"{input_text}", "es", "en")

def libretranslate_french(input_text):
    return lt.translate(f"{input_text}", "fr", "en")

def libretranslate_input(input_text, input_language="es"):
    return lt.translate(f"{input_text}", input_language, "en")

errors = 0
translation_list = []

for statement in over_50['input_statement']:
    #try:
        translate_selected = libretranslate_input(statement, input_language=input_language)
        #french = libretranslate_french(statement)
        #spanish = libretranslate_spanish(french)
        translation_list.append(translate_selected)
    #except:
    #    translation_list.append("translation failed")
    #    errors += 1
print(f"Finished translating with {errors} errors.")
over_50['translation'] = translation_list

if errors > (len(over_50['input_statement'])/2):
    print("Over 50 percent of translations failed. Double check your input language.")
else:
    print("Generating csv file...")

    translation_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_translations.csv')
    
    over_50.to_csv(f"{translation_filepath}")
    over_50 = over_50.sort_values('similarity_value', ascending=False)

    over_50 = over_50[['filename', 'input_statement', 'translation', 'checked_false_statement', 'similarity_value', 'factcheck_index']]

    translation_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_translations.csv')

    over_50.to_csv(f"{translation_filepath}")

