# misinforadio

Welcome to the misinforadio project. This tool is being developed to assist researchers and reporters to analyze misinformation on radio and television broadcasts.

There are currently four steps to in the automated analysis pipeline, each with a dedicated python script (or multiple scripts to support additional options):

Step 1: Generating Ebmeddings of Fact Checked Statements

Step 2: Converting Input Files to Shortened MP3s

Step 3: Transcription

Step 4: Comparing Radio Segments to Fact Checked Statements


# Basic Instructions

Make a copy of this GitHub repository by running the following command on the command line:

```
$ git clone https://github.com/jrynning1/misinforadio.git
```

Navigate into the directory and run the following commands to initialize a python virtual environment:

```
$ pipenv install
$ pipenv shell
```

Save a dataset of fact checked statements in the /data/factchecked_statements folder. Two datasets are currently supported.

- Fact-Check Insights by the Duke Reporters' Lab, available by request at https://www.factcheckinsights.org/ (JSON version)

- PolitiFact fact checks, compiled by Rishabh Misra and available at https://www.kaggle.com/datasets/rmisra/politifact-fact-check-dataset


Run python script 1a, 1b, or 1c, depending on which fact check dataset you are using and whether you prefer the most recent one or two years if using Fact-Check Insights.

Navigate to the data/video_import folder and save a copy of any audio or vido files you want to analyze.

Run python script 2

Run python script 3a, 3b, or 3c; 3a is recommended if Whisper runs well locally on your machine, otherwise 3b works well but requires an API key and greatly increases the cost of running this pipeline.

Run python script 4

The final output file will be generated in data/output_csv.