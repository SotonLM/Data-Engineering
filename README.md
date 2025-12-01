# SotonLM Data Engineering

🎯 **Project Overview**

This repository contains the data-engineering code for SotonLM.  
Our goal is simple:

**Turn raw text from multiple domains (academic, web, social) into clean, structured, schema-consistent JSONL ready for LLM training.**

The pipeline is modular and split into three stages per domain:

1. **Ingest** → get raw data  
2. **Clean** → remove noise / normalise  
3. **Output** → validated records following a consistent schema  

This repo currently contains the core pipeline skeleton, tests, schema, and local sample data.  
Contributors will fill in the TODOs under each domain according to issues on GitHub.

---

## ⚙️ Project Structure

```
data/
  raw/
    academic/
    web/
    social/
  clean/
    academic/
    web/
    social/
  intermediate/
  shard/
  mixture/
  scratch/
  metadata/
docs/
  data_schema.md
  CONTRIBUTING.md
src/
  ingest/
  clean/
  dedupe/
  shard/
  mixture/
  pipeline/
  shared/
tests/
pyproject.toml
README.md
requirements.txt
```

---

## 🚀 Getting Started (Contributors)

**Requirements:**  
- Python 3.10+  
- Git  

### 1. Clone the repository

```bash
git clone https://github.com/SotonLM/Data-Engineering.git
cd Data-Engineering
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

**Mac/Linux:**

```bash
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest
```

### 5. Run the tests

```bash
pytest
```

You should see all tests passing.

---

## 🧪 Minimal Example Run (Academic)

### Run ingestion

```bash
python -c "from src.ingest.academic_ingest import run_ingest; run_ingest('data/raw/academic/sample_raw.jsonl')"
```

### Run cleaning

```bash
python -c "from src.clean.academic_clean import run_clean; run_clean('data/raw/academic/sample_raw.jsonl', 'data/clean/academic/sample_clean.jsonl')"
```

After this, you should see output files in:

- `data/raw/academic/`
- `data/clean/academic/`

---

## 🧭 How to Contribute

Before writing any code:

1. Read `docs/CONTRIBUTING.md`  
2. Read `docs/data_schema.md`  
3. Pick an issue assigned to your division  
   Examples:
   - ingest academic  
   - clean web  
   - ingest social  
4. Modify **only** the TODO section in the file listed in the issue.  
   (Anything else will be rejected.)

All cleaned output must validate against the schema.

---

## 📌 Active Work

See the GitHub **Issues** tab for all open tasks.  
Each task is isolated to a single function to avoid breaking the pipeline.

---

## 🧱 Maintainers

This repo is maintained by the SotonLM Data Engineering team.  
For questions: open an Issue or contact a division lead.
