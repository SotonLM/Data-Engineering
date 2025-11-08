# Soton LM Data Engineering
<div align="center">

Building the Foundation for Large Language Models

</div>
🎯 Project Overview

This is the data engineering division of the Soton LM project, tasked with building high-quality training data for large language models from diverse sources. Our mission is to transform raw, unstructured data from the internet into clean, structured datasets ready for model training.
Team Structure

We operate through three specialized divisions:
Division	Focus Area	Data Sources
🔬 Team 1 - Academic	Research & Educational Content	arXiv, research papers, technical documentation, educational materials
🌐 Team 2 - Web	General Knowledge	Wikipedia, news articles, Common Crawl, general web content
💬 Team 3 - Social	Conversational Data	Reddit, Twitter, social media platforms, forum discussions
🚀 Quick Start
Prerequisites

    Python 3.9 or higher

    Git

    Bash (Linux/Mac) or WSL (Windows)

One-Command Setup

We've automated the entire setup process! Run this single command to get started:
bash

# Clone the repository (if you haven't already)
git clone https://github.com/soton-lm/soton-lm-data-engineering.git
cd soton-lm-data-engineering

# Run the setup script
./setup.sh

What the setup script does:

    ✅ Creates the complete project structure

    ✅ Sets up Python virtual environments

    ✅ Installs all required dependencies

    ✅ Configures pre-commit hooks

    ✅ Verifies your installation

    ✅ Provides team-specific setup

Manual Setup (Alternative)

If you prefer manual setup or the script encounters issues:
bash
```

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install base requirements
pip install -r requirements.txt

# Install team-specific requirements (choose your team)
pip install -r src/division_1_academic/requirements.txt  # Team 1
# OR
pip install -r src/division_2_web/requirements.txt       # Team 2  
# OR
pip install -r src/division_3_social/requirements.txt    # Team 3

```

📁 Project Structure
text

soton-lm-data-engineering/
├── data/                 # Data directories (auto-created)
│   ├── raw/             # Raw source data
│   └── clean/           # Processed, clean data
├── src/                 # Source code
│   ├── division_1_academic/     # Team 1: Academic data pipelines
│   ├── division_2_web/          # Team 2: Web data pipelines  
│   ├── division_3_social/       # Team 3: Social data pipelines
│   └── shared/                  # Common utilities
├── docs/                # Documentation
├── .github/             # GitHub workflows
├── requirements.txt     # Core dependencies
└── setup.sh            # Setup script (you are here!)

🛠️ Technology Stack
Core Technologies

    Python - Primary programming language

    Pandas - Data manipulation and analysis

    PySpark - Distributed data processing

    Prefect - Workflow orchestration

    DuckDB - Analytical database

    DVC - Data version control

Team-Specific Tools

    Team 1: PyMuPDF, arXiv API, NLTK, spaCy

    Team 2: Wikipedia API, Newspaper3k, BeautifulSoup, Common Crawl

    Team 3: snscrape, PRAW, Tweepy, textstat

👥 Team Workflow
For New Contributors

    Choose Your Team based on your interests

    Run the Setup Script to configure your environment

    Explore Your Team's Directory in src/division_*

    Check Existing Issues on your team's project board

    Start with a Good First Issue to get familiar with the codebase

Development Workflow
bash

# 1. Activate your environment (if not already active)
source venv/bin/activate

# 2. Start Prefect server for workflow management
prefect server start

# 3. Work on your data pipelines
cd src/division_[your_team_number]

# 4. Test your pipeline
python your_pipeline.py

# 5. Submit a pull request

Team-Specific Quick Commands

Team 1 (Academic):
bash

./setup.sh 1
python src/division_1_academic/arxiv_pipeline.py

Team 2 (Web):
bash

./setup.sh 2  
python src/division_2_web/wikipedia_pipeline.py

Team 3 (Social):
bash

./setup.sh 3
python src/division_3_social/reddit_pipeline.py

📊 Data Standards

All teams must adhere to our data quality standards:
Output Schema

All processed data should follow this structure:
python

{
    'text': str,           # Cleaned text content
    'source': str,         # Data source identifier
    'language': str,       # Language code (e.g., 'en')
    'quality_score': float,# 0-1 quality metric
    'timestamp': datetime, # When data was collected
    'metadata': dict       # Team-specific fields
}

File Formats

    Raw Data: Original format (JSON, HTML, PDF, etc.)

    Processed Data: Parquet files with compression

    Intermediate Files: Temporary processing files

