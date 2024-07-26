#! /bin/bash

python 2_convert_input_to_aac.py && python 3a_transcribe_local.py && python 4_transcript_embeddings.py && python 5_embeddings_comparisons.py