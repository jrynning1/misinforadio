import pandas as pd
import os
from openai import OpenAI
from pathlib import Path
import json
from datetime import datetime, date

print("Starting to gather embeddings... this may take some time")

# add your OpenAI API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

# load Fact-Check Insights JSON, with only claim reviews
fact_check_insights_filepath = Path().cwd().parent.joinpath('data/factchecked_statements/fact_check_insights.json')

with open(fact_check_insights_filepath) as f:
    data = json.load(f)

claim_reviews = data['claimReviews']

fact_check_insights = pd.DataFrame(claim_reviews)

# filter for only false statements
fact_check_insights.insert(5, 'rating', fact_check_insights.reviewRating.str['alternateName'])

fact_check_insights_false = fact_check_insights[(fact_check_insights['rating'] == "false") | 
    (fact_check_insights['rating'] == "pants-fire") | 
    (fact_check_insights['rating'] == "Falso") |
    (fact_check_insights['rating'] == "False") |
    (fact_check_insights['rating'] == "FALSE") |
    (fact_check_insights['rating'] == "Notizia falsa") |
    (fact_check_insights['rating'] == "Fake") |
    (fact_check_insights['rating'] == "Pants on Fire") |
    (fact_check_insights['rating'] == "falso") |
    (fact_check_insights['rating'] == "Falso!")
    ]

fact_check_insights_false = fact_check_insights_false.dropna(subset='claimReviewed')

false_text_df = fact_check_insights_false.drop(columns=['@context', '@type', 'itemReviewed', 'reviewRating'])

false_text_df = false_text_df.rename(columns={'claimReviewed': 'statement'})

# remove entries without publication date
false_text_df = false_text_df[false_text_df['datePublished'] != '']

# remove entries with improperly formatted dates
false_text_df = false_text_df[false_text_df['datePublished'].str.len() == 10]

# remove entries with empty statement value
false_text_df = false_text_df[false_text_df['statement'] != '']

# remove characters from statement value that may be problematic
false_text_df['statement'] = false_text_df['statement'].str.replace('\n', '').replace("'","").replace('"','').replace('“','').replace(',','\,')

# generate todays date to calculate time since publication
todays_date = date.today()

false_text_df.insert(5, 'reformated_date', false_text_df['datePublished'].apply(lambda x: date.fromisoformat(x)))

false_text_df['time_since_publication'] = todays_date - false_text_df['reformated_date']

false_text_df.insert(5, 'days_since_publication', false_text_df['time_since_publication'].apply(lambda x: x.days))

# filter for only items published within the past two years
year_to_date_false_text_df = false_text_df[false_text_df['days_since_publication'] <= 730]

# request embeddings from OpenAI
def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

# add embeddings to DataFrame
year_to_date_false_text_df['statement_embedding'] = year_to_date_false_text_df['statement'].apply(lambda x: get_embedding(x, model='text-embedding-3-small'))

# generate csv
embedded_false_statements_path = Path().cwd().parent.joinpath('data/factchecked_statements/embedded_false_statements.csv')

year_to_date_false_text_df.to_csv(embedded_false_statements_path, index=False)