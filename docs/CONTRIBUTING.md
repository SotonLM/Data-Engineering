# Contributing Guide — SotonLM Data Team

This document explains exactly how to contribute to this repository without breaking the pipeline, structure, or schema.

---

# Core Principles

1. **Never modify directory structure**  
   Do NOT rename, delete, or relocate anything under:  
   - data/**  
   - src/shared/**  
   - src/pipeline/**  

2. **Only write code in your assigned TODO sections**  
   You must ONLY modify:  
   - clean_*_record inside src/clean/...  
   - iter_raw_*_source inside src/ingest/...  
   Any changes outside these functions must be approved by maintainers.

3. **Do NOT commit datasets**  
   All real datasets must be saved locally or in cloud storage.  
   GitHub must only contain:  
   - sample raw files  
   - cleaned sample files  
   - metadata  
   - code

4. **Follow the schema exactly**  
   All cleaned records MUST match docs/data_schema.md and the code in src/shared/schema.py  
   Do not add or remove fields without maintainer approval.

---

# What You Are Allowed To Implement

For each division (Academic, Web, Social), you may work inside:  
src/ingest/<domain>_ingest.py  
src/clean/<domain>_clean.py  

You will see functions like:  

def iter_raw_web_source():  
    # TODO: implement raw record generator  

and  

def clean_web_record(raw):  
    # TODO: implement cleaning logic  

These are the ONLY areas where you write code.

---

# What You Are NOT Allowed To Modify

The following areas are maintained by core maintainers only. Do NOT touch these files unless explicitly told to:

- src/shared/schema.py  
- src/shared/io.py  
- src/shared/logging_utils.py  
- all of src/pipeline/**  
- all of src/shard/**  
- all of src/mixture/**  
- tests/test_paths.py  
- tests/test_schema.py  
- any folder inside data/ except your own sample_raw.jsonl files  

Breaking these rules means your PR is immediately rejected.

---

# Running the Tests

Before opening a pull request, run:  

pytest

Your PR will be rejected if tests do not pass.

---

# Branch and PR Rules

1. Create branches using:  
   git checkout -b feature/<your-name>/<task>

   Example:  
   git checkout -b feature/jamie/web-cleaning-v1

2. One task = one branch  
   One branch = one PR  

3. Every PR must include:  
   - summary of changes  
   - which TODOs were completed  
   - confirmation that pytest passes  

4. At least one maintainer must approve before merging.

---

# Sample Workflow

1. Pull latest main:  
   git pull origin main

2. Create your branch:  
   git checkout -b feature/jamie/web-cleaning-v1

3. Implement TODOs inside clean_web_record or iter_raw_*_source.

4. Run:  
   pytest

5. Commit & push:  
   git add .  
   git commit -m "Implement basic web cleaner"  
   git push --set-upstream origin feature/jamie/web-cleaning-v1

6. Open a PR on GitHub.

---

# Summary

- Only clean inside clean_*_record  
- Only ingest inside iter_raw_*_source  
- Follow the schema exactly  
- Never commit real data  
- Never modify core structure  
- Always run tests before PR  

