
# **Main Task** - Create an automated pipeline for data collection

The flow of the pipeline should be as follows : Data Fetching -> Raw Data Storage -> Cleaning -> Clean Data Storage

Here, we will explain in detail what you need to do for each section of the pipeline.

# ------------------- Data Fetching ---------------------------

Your main source platform is probably arXiv, as mentioned in the meetings. 
However, we've added the apis for [semanticscholar](https://www.semanticscholar.org/) 
and [crossref](https://www.crossref.org/) within the requirements.txt.

Usage of these apis will be quite straightforward - the main thing you need to account for 
is automated documentation and storage of all fetched data.

**IF you want to find and source data from another platform of your choice - **
1. Make sure sources are relevant to the division; we want to keep data storage as organized as possible.
2. Add any additional libraries you used to fetch data from your preferred source into the requirements.txt.

One other thing to make sure in general is that the sources are in English. Multi-language support is a VERY long term 
objective, so we shouldnt worry about it now.

# --------------- Documenting Raw Data ----------------------

As emphasised in previous meetings, documentation of data, whether clean or not, is VERY important.
If the LLM breaks in some way, the blame most likely goes to what and how data was fed into it.
Documenting data makes debugging and fixing the breaks SO MUCH EASIER.

For the sake of readability and organization, documented raw data should be stored in the JSON file format.
The 

A lot of the metadata can be extracted from the fetched data, but there will be some that the script will have to generate on its own.
Below will be a list of what you need to document for every data fetched.

**WARNING** - The list of metadata to store may be subject to change. But don't worry, this won't happen too often, if at all.

- Source ID. A unique identifier for fetched data. You have to generate these with code.
One recommendation of forming an ID is by mixing up the source type and url. for example, if the source type is "arxiv" and the url is "https://arxiv.org/abs/2511.11480v1",
you can form the ID to be something like "arxiv:2511.11480v1". 

Note - You might not be able to use the same protocol for every platform, so you might have to come up with a different way to generate IDs for different platforms.

## Actual Content of Data
Theres the main content you want from the data source like:

- Title
- Abstract
- Full Text

You would also want some additional data that accompanies the main content:

- Authors
- Date of Publication
- Categories. Category of article, or relevant keywords
- Word Count
- Character Count


## General Data for Identification

- Source Type. The platform you sourced the data from.
- Source URL. The exact URL of where the data came from.

- Fetch Timestamp. The program should generate a timestamp of exactly when they fetched the data.
- Fetch Method. The program should note down the APIs and Libraries used to fetch this data. 
The fetch method is probably one of the greater causes of errors, so its very, VERY important.

- Hashed Content. A hash of the raw content. The program should produce a hash from data whenever they're fetched. Useful for detecting duplications.
- Original File Format Type of Fetched Data.
- File Size in Bytes.





## Legal Metadata

WE NEED THESE. As much as I want to be an unethical demon, we have to make sure to not break any rules.

- License Type.
- License URL. Mainly for human reading.

You should also have the program to automate a rough analysis of the license. We can summarise the license by storing the following booleans:

- Commercial use of Data is Allowed. Yes, the project will be open source. But it will be a problem if someone uses our project for a commercial one of their own,
and some of the training data doesn't allow commercial use. So this ideally should be **True**.

- Redistribution is Allowed.

- Attribution is Required.


## Pipeline Metadata

These will be used to manage and debug the pipeline, so that the fetching process is smooth.

- Fetch Job ID. Not to be confused with empl*yment. Identifies the program execution that fetched this data.
*from wikipedia - In computing, a job is a unit of work or unit of execution*

- Text Extraction Method. Slightly different to the previous Fetch Method metadata; this should store what method was used to extract text from the source's original format.
- List of Warnings displayed within the job.





# --------------- Data Cleaning -----------------------

This stage determines which text from the raw data should be used to train the LLM.

There are a bunch of things to clean from raw data - the main point is to extract the most relevent parts of text.

The catch here is that not all raw documents can use the same cleaner (e.g. arxiv documents have content begin and end markers, where other sources wont have that). Hence, we want a cleaner script for each sourcing platform.


Below is a list that we've come up with on what needs to be cleaned off, but if you discover anything else that should be on here, feel free to update this list.


## Elements to Remove

- Authors and Date of Publication.
- for arXiv: [file content begin] and [file content end]. Other data sources can have their own metadata like this, so make sure to remove them as well.
- Page Numbers and Page Number Markers
- URLs
- Citation Markers. Stuff like [], [; ], [10, 11, 12, 13]
- Join Hyphenated Words. So words like "anti-gravity" should just be joined into "antigravity", to simplify training data.
- Some phrases like "et al".

## Elements to Change/Standardize

- Figure, Table and Equation Markers. 
One source can describe figures with "Figure 1:", and another may describe it with "FIGURE 1:". We want to standardize this for consistency.
- Section Headers.
- Bibliography.
- Appendix Markers



# ----------------- Documenting Clean Data ---------------------

Clean data will be stored in the parquet file format. This optimizes data reading which is useful for tokenization later.

Documentation of clean data has the same benefits of documenting raw data, with the addition of it helping with checking reproducability and cleaner debugging.


## Actual Contents of Data

- Title
- Cleaned Version of the Full Text
- Cleaned Abstract

We also want these as well:

- Word Count after Cleaning
- Character Count after Cleaning


## General Identification

These should be found from the documented raw data file.

- Source ID of Raw Data used.
- Hash of Raw Data.
- Path of the Raw Data File.
- Fetch Timestamp


## Cleaning Quality

- Cleaning Timestamp.
- Cleaner Script Used.
- Math Handling. A lot of the data, especially ones from this division, will have mathematical expressions written in LaTeX. This is to log whether you kept the latex code for the expression, rewrote the expression in some other way or just straight up deleted it. My recommendation is to just keep the LaTeX as it is, but having it learn other math syntaxes could help.
- Code Handling.


