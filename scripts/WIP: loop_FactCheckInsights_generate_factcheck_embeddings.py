import pandas as pd
import os
from openai import OpenAI
from pathlib import Path
import json
from datetime import datetime, date

print("Starting to gather embeddings... this may take some time")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

fact_check_insights_filepath = Path().cwd().parent.joinpath('data/factchecked_statements/fact_check_insights.json')

with open(fact_check_insights_filepath) as f:
    data = json.load(f)

media_reviews = data['mediaReviews']

mr_df = pd.DataFrame(media_reviews)

mr_df.insert(5, 'rating', mr_df.mediaAuthenticityCategory)

claim_reviews = data['claimReviews']

cr_df = pd.DataFrame(claim_reviews)

cr_df.insert(5, 'rating', cr_df.reviewRating.str['alternateName'])

fact_check_insights = pd.concat([cr_df, mr_df])

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

fact_check_insights_false.dropna(subset='claimReviewed', inplace=True)

false_text_df = fact_check_insights_false.drop(columns=['@context', '@type', 'itemReviewed', 'reviewRating', 'mediaAuthenticityCategory', 'originalMediaContextDescription', 'originalMediaLink'])

false_text_df = false_text_df.rename(columns={'claimReviewed': 'statement'})

# remove entries without publication date
false_text_df = false_text_df[false_text_df['datePublished'] != '']

# remove entries with improperly formatted dates
false_text_df = false_text_df[false_text_df['datePublished'].str.len() == 10]

# remove entries with empty statement value
false_text_df = false_text_df[false_text_df['statement'] != '']

false_text_df['statement'] = false_text_df['statement'].str.replace('\n', '').replace("'","").replace('"','').replace('“','').replace(',','\,')

todays_date = date.today()

false_text_df.insert(5, 'reformated_date', false_text_df['datePublished'].apply(lambda x: date.fromisoformat(x)))

false_text_df['time_since_publication'] = todays_date - false_text_df['reformated_date']

false_text_df.insert(5, 'days_since_publication', false_text_df['time_since_publication'].apply(lambda x: x.days))

year_to_date_false_text_df = false_text_df[false_text_df['days_since_publication'] <= 365]

claim_review_list = year_to_date_false_text_df['statement'].to_list()

embeddings_list = []

counter = 0

failed_embeddings = 0

total_rows = len(year_to_date_false_text_df)

for claim in sorted(claim_review_list):
    try:
        result = client.embeddings.create(input = [claim], model="text-embedding-3-small").data[0].embedding
        print_text = f"Embedded statement {counter} of {total_rows}. [{int((counter / total_rows * 100))}%]          "
        print("\r", print_text, end="")
    except:
        result = 'embedding failed'
        failed_embeddings += 1
        error_print_text = f"Embedding failed for statement {counter} of {total_rows}"
        print(error_print_text)
    counter += 1
    embeddings_list.append(result)

year_to_date_false_text_df['statement_embedding'] = embeddings_list

embedded_false_statements_path = Path().cwd().parent.joinpath('data/factchecked_statements/embedded_false_statements.csv')

year_to_date_false_text_df.to_csv(embedded_false_statements_path, index=False)