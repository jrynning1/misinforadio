import streamlit
import subprocess
import pandas as pd
import os
import numpy as np
from pathlib import Path
from openai import OpenAI
from libretranslatepy import LibreTranslateAPI

number_return_values = 1

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

# add your OpenAI API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

print('Input questionable statement inside quotation marks ("").')

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

# there is something wrong with at least one embedding, and I need to figure out how to either skip it or make it work
# it may be from assigning errors as NaN in the other script; may have to change that to 0 or something
transcription = input()

transcription_embedding_list = get_embedding(transcription)

transcription_embedding_array = np.array(eval(transcription_embedding_list))

print(f'transcription embedding array: {transcription_embedding_array}')

def cosine_similarity(vec1, vec2):
    # Normalize each vector to unit length
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
  
    # Calculate dot product between normalized vectors
    similarity = np.dot(vec1_norm, vec2_norm)
    return similarity

# if the transcript segment is shorter than 150 characters, this will use the context segment instead
def search_false_statements(false_text_df=false_text_df, n=10):
    transcription_similarity_list = []
    errors = 0
# is receiving embeddings above
    for embedding in statement_embedding_list:
        try:
            transcription_similarity = cosine_similarity(embedding, transcription_embedding_array)
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

top_matches_df = search_false_statements()


top_matches_df['similarity_value'] = top_matches_df['similarity'].apply(lambda x: x.split()[1]).astype(float)
top_matches_df['factcheck_index'] = top_matches_df['similarity'].apply(lambda x: x.split()[0])

print(top_matches_df)
"""
over_50 = top_matches_df.loc[top_matches_df['similarity_value'] >= .5]

over_50 = over_50.sort_values('similarity_value', ascending=False)

over_50 = over_50[['filename', 'input_statement', 'checked_false_statement', 'similarity_value', 'factcheck_index']]

over_50_csv_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_context.csv')

print("Generating csv file...")

over_50.to_csv(f"{over_50_csv_filepath}")

print("Enter LibreTranslate language code -- \"es\" for spanish, \"fr\" for french, etc.")
input_language = input()

print("Adding translation...")

"""
"""
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

"""