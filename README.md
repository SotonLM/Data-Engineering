# Soton LM Data Engineering

\<div align="center"\>

[](https://www.python.org/downloads/)
[](https://dvc.org/)
[](https://duckdb.org/)
[](https://github.com/psf/black)
[](https://github.com/astral-sh/ruff)

\</div\>

## 🎯 Project Overview

[cite\_start]This is the data engineering division of the SotonLM project, tasked with building high-quality training data for large language models from diverse sources[cite: 1082]. Our mission is to transform raw, unstructured data from the internet into clean, structured, and version-controlled datasets ready for model training.

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

## 🛠️ Technology Stack

[cite\_start]Our stack is defined by `pyproject.toml` to ensure consistency and reproducibility[cite: 1082].

### Core Technologies

  * **Python:** Our primary programming language.
  * **DVC (Data Version Control):** For versioning large datasets and connecting to S3.
  * **Pandas:** For core data manipulation.
  * **DuckDB:** For high-performance queries and analysis.
  * **PyArrow:** For efficient Parquet file I/O.

### Division-Specific Tools

  * **Division 1 (Academic):** `PyMuPDF`, `arxiv`.
  * **Division 2 (Web):** `Scrapy`, `Hugging Face datasets`, `BeautifulSoup4`.
  * **Division 3 (Social):** `PRAW` (for Reddit), `Scrubadub` (for PII).
  * **Universal Cleaning:** `datasketch` (for MinHash LSH).

### Development & CI/CD

  * **`pip-tools`:** For compiling `requirements.txt` from `pyproject.toml`.
  * **`pytest`:** For automated testing of our data pipelines.
  * **`black`:** For automated code formatting.
  * **`ruff`:** For high-speed linting.
  * **`pre-commit`:** For running formatters/linters automatically before commits.

## 🔄 Development Workflow

Follow this workflow to contribute new data to the project.

1.  **Get Latest Changes:**

    ```bash
    git checkout main
    git pull
    dvc pull  # Sync the latest data from S3
    ```

2.  **Create a New Branch:**
    Follow the "data quarantine" workflow from our handbook.

    ```bash
    git checkout -b feature/div3/add-reddit-data
    ```

3.  **Write Your Code:**
    Add your scripts to the `src/division_.../` directory.

4.  **Run Pipeline & Version Data:**
    As you generate data, version it with DVC.

    ```bash
    # 1. Run your sourcing script, which outputs to data/raw/
    python src/division_3_social/01_source_reddit.py

    # 2. Version the raw data
    dvc add data/raw/division_3_social/reddit_batch_01.parquet

    # 3. Run your cleaning script, which outputs to data/clean/
    python src/division_3_social/02_clean_reddit.py

    # 4. Version the clean data
    dvc add data/clean/division_3_social/cleaned_reddit_01.parquet
    ```

5.  **Commit Code & Pointers:**

    ```bash
    # Add your scripts and the new .dvc pointer files
    git add src/, data/

    # Commit your changes (pre-commit hooks will run)
    git commit -m "feat(div3): Add and clean new batch of Reddit data"
    ```

6.  **Push Everything:**
    This is a two-step process: data first, then code.

    ```bash
    # 1. Push DATA to S3
    dvc push

    # 2. Push CODE and POINTERS to GitHub
    git push -u origin feature/div3/add-reddit-data
    ```

7.  **Open a Pull Request:**
    Go to GitHub and open a Pull Request. Fill out the `PULL_REQUEST_TEMPLATE.md` and be sure to update the `docs/complete_documentation.json` as required.
