# Soton LM Data Engineering

[](https://www.python.org/downloads/)
[](https://dvc.org/)
[](https://duckdb.org/)
[](https://github.com/psf/black)
[](https://github.com/astral-sh/ruff)

## 🎯 Project Overview

This is the data engineering division of the SotonLM project, tasked with building high-quality training data for large language models from diverse sources. Our mission is to transform raw, unstructured data from the internet into clean, structured, and version-controlled datasets ready for model training.

This repository contains all pipeline code, data pointers (DVC), and documentation.

## 🚀 Team Structure

We operate through three specialized divisions, each focused on a different domain of data:

| Division | Focus Area | Key Tools & Sources |
| :--- | :--- | :--- |
| **🔬 Division 1 - Academic** | Research & Technical Content | `arxiv` (API), `PyMuPDF` (PDFs) |
| **🌐 Division 2 - Web** | General Knowledge | `Scrapy`, `datasets` (Wikipedia), `BeautifulSoup4` (HTML) |
| **💬 Division 3 - Social** | Conversational Data | `PRAW` (Reddit), `Scrubadub` (PII Cleaning) |

## ⚙️ Quick Start

This guide will set up your local environment, connect you to the data, and get you ready to contribute.

### Prerequisites

  * Python 3.10 or higher
  * [Git](https://git-scm.com/)
  * [AWS CLI](https://aws.amazon.com/cli/) (for connecting to S3)
  * [DVC (Data Version Control)](https://dvc.org/doc/install)

### Setup Steps

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/SotonLM/Data-Engineering.git
    cd Data-Engineering
    ```

2.  **Create and Activate Virtual Environment:**

    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (Mac/Linux)
    source venv/bin/activate

    # Or (Windows)
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    We use `pyproject.toml` to define dependencies and `pip-tools` to compile `requirements.txt` files.

    ```bash
    # Install the core tools to get started
    pip install pip-tools

    # Compile and install the main dependencies
    pip-compile pyproject.toml -o requirements.txt
    pip install -r requirements.txt

    # Compile and install the development dependencies (like pytest, black, ruff)
    pip-compile pyproject.toml --extras dev -o requirements-dev.txt
    pip install -r requirements-dev.txt
    ```

4.  **Install Git Hooks:**
    This will automatically format and lint your code on every commit.

    ```bash
    pre-commit install
    ```

5.  **Configure AWS & DVC:**
    This connects you to the S3 bucket where the 100GB+ dataset is stored.

    ```bash
    # 1. Configure your AWS credentials (using the keys provided by your co-lead)
    aws configure

    # 2. Pull the data from DVC (this will download the current dataset)
    dvc pull
    ```

You are now fully set up and have the latest version of both the code and the data.

## 📁 Project Structure

```text
soton-lm-data-engineering/
├── .dvc/                 # DVC internal files
├── .github/              # GitHub workflows and PR templates
├── data/
│   ├── raw/              # Raw source data (tracked by DVC)
│   │   ├── division_1_academic/
│   │   ├── division_2_web/
│   │   └── division_3_social/
│   └── clean/            # Processed, clean data (tracked by DVC)
│       └── ...
├── docs/                 # Documentation (e.g., complete_documentation.json)
├── src/                  # Source code for all data pipelines
│   ├── division_1_academic/
│   ├── division_2_web/
│   ├── division_3_social/
│   └── shared/           # Common utilities (e.g., deduplication)
├── .gitignore
├── pyproject.toml        # Project definition and dependencies
├── requirements.txt      # Main locked dependencies (auto-generated)
└── requirements-dev.txt  # Dev locked dependencies (auto-generated)
```

