import pandas as pd
import os
from openai import OpenAI
from pathlib import Path

print("Starting to gather embeddings... this may take some time")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

politifact_filepath = Path().cwd().parent.joinpath('data/factchecked_statements/politifact_factcheck_data.json')

politifact = pd.read_json(politifact_filepath, lines=True)

false_or_mostly_false_path = Path().cwd().parent.joinpath('data/factchecked_statements/politifact_false_or_mostly_false.json')

politifact_false_or_mostly_false = politifact[(politifact['verdict'] == "false") | (politifact['verdict'] == "mostly-false") | (politifact['verdict'] == "pants-fire")]

politifact_false_or_mostly_false.to_json(false_or_mostly_false_path, orient='records')

false_text_df = politifact_false_or_mostly_false.drop(columns=['verdict', 'statement_originator', 'statement_date', 'statement_source', 'factchecker', 'factcheck_date', 'factcheck_analysis_link'])

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   embed = client.embeddings.create(input = [text], model=model).data[0].embedding
   return embed

false_text_df['statement_embedding'] = false_text_df['statement'].apply(lambda x: get_embedding(x, model='text-embedding-3-small'))

embedded_false_statements_path = Path().cwd().parent.joinpath('data/factchecked_statements/embedded_false_statements.csv')

false_text_df.to_csv(embedded_false_statements_path, index=False)