
The following are the instructions for data engineers in division 3 - conversational and social.
This one is also currently under development.


Warning - this document was written based on the instructions for division 1, just because that was 
    the first one I wrote. If there's any mention of academics or technical bs, you have the choice
    to let me know or ignore it.
Additional Warning - this document was written based on the instructions for division 2, which is based
    on division 1. **Same warning as above**.


# **Main Task** - Create an automated pipeline for data collection

The flow of the pipeline should be as follows : 
    Data Fetching -> Raw Data Storage -> Cleaning -> Cleaning Evaluation -> Clean Data Storage

Here, we will explain in detail what you need to do for each section of the pipeline.

# ------------------- Data Fetching ---------------------------

The data source for your division is mostly the very social media apps that you use today. 
We've currently provided you the API for Twitter and Reddit, but obviously, feel free to add to this list.

I expect data sources from here to have the shortest amount of text out of all divisions, but that's fine - the point 
    of this division is to fetch in entire conversations; essentially the tree of comments that branch off a post.
Essentially, you guys want to make the chatbot not sound like a robot


<small>Some trivia - remmember when Elon Musk officially revealed that all posts on X/Twitter is used for their AI training,
and then all of the artists moved on to Bluesky? The fun fact here is that Bluesky isn't actually safe from web 
scraping, especially since it's open source. Now you can feel more educated than these anti AI artists that don't 
know what they are preaching for!

sincerely, by a non-AI artist.</small>

**- If you want to use a new data source - **
1. Make sure sources are relevant to the division; we want to keep data storage as organized as possible.
2. Add any additional libraries you used to fetch data from your preferred source into the requirements.txt.

Usage of fetching apis will be quite straightforward - the main thing you need to account for 
is automated documentation and storage of all fetched data.


One other thing to make sure in general is that the sources are in English. Multi-language support is a VERY long term 
objective, so we shouldnt worry about it now.

# --------------- Documenting Raw Data ----------------------

As emphasised in previous meetings, documentation of data, whether clean or not, is VERY important.
If the LLM breaks in some way, the blame most likely goes to what and how data was fed into it.
Documenting data makes debugging and fixing the breaks SO MUCH EASIER.

Your method of storing data is a bit different from other divisions:
- You first want a JSON file to represent the entire conversation.
- And then another JSON for each comment that is a part of that conversation.
- The two above must be linked together in some way.

Below is a list of metadata to document, along with storing the main content.

**WARNING** - The list of metadata to store may be subject to change. But don't worry, this won't happen too often, if at all.


## For the Raw File of the Entire Conversation:
- Conversation ID. You can generate ID by code, by doing something like {Platform Name} + {Hashed value of OP's Username}.
    If you dont know what hashing is, google it or something - i know for a fact 
        you have your browser open with 1 million tabs, and this shouldnt be a noticable addition.
- Source URL. The exact URL of where the data came from.
- Platform Name
- Convo Title.
- Hashed version of Convo Title.
- Number of Users in Conversation.
- Message Count.
- Max Reply Depth. E.g. Depth is 3 if there is a comment on a comment on the original post.
- Average Quality Score. Out of all Quality scores of all comments.
If you dont know how to calculate data quality, read section 3 of "https://dl.gi.de/server/api/core/bitstreams/89cb2dc4-8a1d-424d-9bce-6569b6e4ae8e/content"
or just ask AI if you dont like human papers.
- Average Toxicity Score. Out of all toxicity scores of all comments.
I'll get into the details of toxicity score later.



## For the Raw File of a single Message:
- Conversation ID. This ID should be the same as the conversation it belongs to.
- Message ID. Also generate by code, 
- Hashed version of the messenger's username.
- User Type. OP? Commenter? Mods?
- Message Content.
- Message Length in words. If this is low (e.g. one word response like lmao), dont even bother saving this message as a file.
- Message Position within the conversation (How many'th message is this in the entire conversation?)
- Quality Score.
- Toxicity Score. How angry were the keyboard warriors?
    Measure by comparing the number of curse words to the length of the message.
- Likes Count. For reddit, this could be the number of upvotes. 
For twitter, this could be the combined value of the number of retweets and likes.




## Generally Required Data
Metadata specified below must be in both the conversation files and the message files:

- Detected Language. Should be EN.
- Language Confidence Score. A ratio of {Main Detected Language}/{All Detected Languages}. This should show how ENGLISH the text is.

## Legal and Ethical Metadata

WE NEED THESE. As much as I want to be an unethical demon, we have to make sure to not break any rules.

- Legal Framework. This depends on the platform: for Reddit, it's the User Content Agreement.
For Discord, it's ToS + Privacy Policy
- Conversation Type. Is this a DM or a public post?

And then there's the booleans to consider like:

- Consent Implied in Legal Framework? True if the framework says something like:
"Making a post in this platform gives explicit consent on the post being used in various ways."
- Commersial use is Allowed? Found from the framework.
- Scraping is Allowed? Also found from the framework.   
- Official API used?
- Contains Personal Data? We don't really want to break GDPR in some way.
- Contains Sensitive Categories?

## Pipeline Metadata

These will be used to manage and debug the pipeline, so that the fetching process is smooth.

- Fetch Job ID. Not to be confused with empl*yment. Identifies the program execution that fetched this data.
*from wikipedia - In computing, a job is a unit of work or unit of execution*

- Text Extraction Method. Slightly different to the previous Fetch Method metadata; this should store what method was used to extract text from the source's original format.
- List of Warnings displayed within the job.





# -------------- Storage of Raw Data ----------------------

Added this section because the storage method of raw and clean data are different.

As mentioned before, the documented stage should have readied two kinds of JSON files:
- Documented JSON of a Conversation.
- Documented JSONs of each message in that conversation.

You will now put these files into the microsoft azure cloud storage.

Random fact drop: we expect in the long term about 5 - 10 TB of data going into the storage.

we have provided a script (src/storefunc.py) which contains a function (store_to_azure) to store a file into the azure blob.

store_to_azure() takes two arguments: the file name and your division's container name.
**The Azure Blob container name for your division is "conversational-social". DO NOT STORE ANYWHERE ELSE, OR ADD IRRELEVENT DATA.**

You can import this function to the pipeline you create like this:

```
    from storefunc import store_to_azure
```

So once documented, store the JSON file onto the blob. Simple as balls.

Quick heads up - storing clean data is a bit more complicated.


# --------------- Data Cleaning -----------------------

This stage determines which text from the raw data should be used to train the LLM.

There are a bunch of things to clean from raw data - the main point is to extract the most relevent parts of text.

The catch here is that not all raw documents can use the same cleaner (e.g. arxiv documents have content begin and end markers, where other sources wont have that). Hence, we want a cleaner script for each sourcing platform.


Below is a list that we've come up with on what needs to be cleaned off, but if you discover anything else that should be on here, feel free to update this list.


## Elements to Remove

- External URLs
- Hashtags
- User Mentions (@your_mom, etc.)
- Channel Mentions Likewise.
- Offensive Language
- Gifs, Image alt texts, file names.


## Elements to Change/Standardize

- Real Names. Should be changed to just [Name]
- Email Addresses. Likewise to above.
- Same Goes for Addresses, Phone Numbers, IP addresses, and other personal information.
They should be changed to just [Address], [Phone Number], etc.
- Discord, Slack Formatting. Standardize formatting.
- Code Blocks. Standardize an indication that ```this is a block of code``` or smth.
- Emoji Unicode. Standardize this as well.
- 2 + whitespaces. if    the      text   is   spaced out   like   this   its    very    annoying


# ----------------- Documenting Clean Data ---------------------

Documentation of clean data has the same benefits of documenting raw data, with the addition of it helping with checking reproducability and cleaner debugging.

Here's another checklist to go through:

**WARNING** this list is incomplete.

## For the Clean File of the Entire Conversation:
- Conversation ID. You can generate ID by code, by doing something like {Platform Name} + {Hashed value of OP's Username}.
    If you dont know what hashing is, google it or something - i know for a fact 
        you have your browser open with 1 million tabs, and this shouldnt be a noticable addition.
- Source URL. The exact URL of where the data came from.
- Platform Name
- Convo Title.
- Hashed version of Convo Title.
- Number of Users in Conversation.
- Message Count.
- Max Reply Depth. E.g. Depth is 3 if there is a comment on a comment on the original post.
- Average Quality Score. Out of all Quality scores of all comments.
If you dont know how to calculate data quality, read section 3 of "https://dl.gi.de/server/api/core/bitstreams/89cb2dc4-8a1d-424d-9bce-6569b6e4ae8e/content"
or just ask AI if you dont like human papers.
- Average Toxicity Score. Out of all toxicity scores of all comments.
I'll get into the details of toxicity score later.



## For the Clean File of a single Message:
- Conversation ID. This ID should be the same as the conversation it belongs to.
- Message ID. Also generate by code, 
- Hashed version of the messenger's username.
- User Type. OP? Commenter? Mods?
- Message Content.
- Message Length in words. If this is low (e.g. one word response like lmao), dont even bother saving this message as a file.
- Message Position within the conversation (How many'th message is this in the entire conversation?)
- Quality Score.
- Toxicity Score. How angry were the keyboard warriors?
    Measure by comparing the number of curse words to the length of the message.
- Likes Count. For reddit, this could be the number of upvotes. 
For twitter, this could be the combined value of the number of retweets and likes.

## Cleaning Quality

- Cleaning Timestamp.
- Cleaner Script Used.
- Math Handling. This is to log whether you kept the latex code for the expression, rewrote the expression in some other way or just straight up deleted it. My recommendation is to just keep the LaTeX as it is, but having it learn other math syntaxes could help.
- Code Handling. I recommend you standardize how you note the beginning and ending of a snippet of code. 
    Since, notations of this can vary.
(in markdown, this can be ``` WHATEVER CODE THERE IS ```, whereas in latex it could be \begin{verbatim} CODE \end{verbatim}).


# -------------------- Storing Clean Data ----------------------------

Storage of clean data is mainly where databases come in play. Since, we like clean data and we want clean data to be stored cleanly.

But since the database file is version controlled, we don't want to store the main cleaned content directly in there.
The solution is as follows:
- store the txt file which contains the cleaned version of the main content into the azure container.
- get the URL of the file thats now inside the azure container. The store_to_azure function will return the URL upon storage, so use that.
- INSERT to the database all of the metadata, and the URL of the clean data file.

The URL in this case acts as a pointer element. Using this URL, we can read from the file in the blob any time, without storing the bulk of the content
into the database.


**BUT WAIT!!!** Storing clean data into the database just because it's clean won't make for a good LLM.
You should only store pointers for clean data above a certain quality score - yes, we want all 10GB of clean data to be high quality.


An example of an azure blob URL is as follows:
"https://sotonlmdeng.blob.core.windows.net/conversational-social/sacrifice.txt"


