#! /bin/bash

parentdir=$(dirname `pwd`)
if [ ! -e "$parentdir"/"data/factchecked_statements/embedded_false_statements.csv" ]
then
    python 1b_fact_check_insights_embeddings_2_years_claims_only.py
else
    echo "Fact-checks previously embedded"
fi && python 2_convert_input_to_aac.py && python 3a_transcribe_local.py && python 4_transcript_embeddings.py && python 5_embeddings_comparisons.py