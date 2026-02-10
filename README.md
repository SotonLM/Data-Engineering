# SotonLM Data Team — Project Update & This Week’s Tasks

## Project Status (Read This First)

The full English Wikipedia dump has now been ingested and parsed into **RAW JSONL shards**.

What this means:
- We have successfully processed the Wikipedia XML dump
- Articles are stored as sharded `.jsonl` files (~512MB per shard)
- Content is still **RAW** (wikitext, minimal processing)
- This unblocks cleaning, analysis, and downstream experiments

This ingestion work is complete and does **not** need to be redone.

We are now moving from **“can we ingest data?”** to **“how do we work with it?”**

---

## What This Week Is About

This week is **not** about building production pipelines.

It *is* about:
- understanding the RAW Wikipedia data
- writing small scripts that operate on the shards
- experimenting locally
- validating assumptions before we harden anything

All work this week is **exploratory and low-risk**.

---

## This Week’s Tasks (GitHub Issues)

Three small tasks have been opened as GitHub issues.  
Pick **one** if you want to contribute.

### 1. RAW Schema Inspection & Stats
**Goal:** Understand what’s actually in the Wikipedia shards.

Write a script that:
- reads one or more RAW Wikipedia `.jsonl` shards
- inspects which fields exist
- reports simple stats (e.g. record counts, average token length, empty fields)

No cleaning, no modifications — inspection only.

---

### 2. Simple Cleaning Prototype
**Goal:** Prototype *very basic* text cleaning.

Write a script that:
- reads RAW Wikipedia `.jsonl`
- performs simple transformations (e.g. strip wikitext markers, remove refs)
- writes a **new** JSONL file (do not overwrite raw)

This is **not** production cleaning — just a prototype to explore approaches.

---

### 3. Shard-Level Analysis
**Goal:** Validate sharding and data distribution.

Write a script that:
- scans all shards in a run directory
- reports per-shard stats (file size, record count, min/max/avg length)

This helps confirm sharding choices and randomness.

---

## How To Work

- Run everything **locally**
- Do **not** commit large data files
- Scripts should be standalone
- Filenames must include your name (e.g. `wiki_stats_alex.py`)
- Output can be printed or written to small test files

Scripts can go under:
```
src/experiments/submissions
```
---

## How To Submit

1. Create a branch:
```bash
git checkout -b feature/<your-name>/<task>
```
2.	Add your script
3.	Commit and push:
```bash
git add .
git commit -m "Add <your-name>'s Wikipedia analysis script"
git push
```
4.	Open a Pull Request and briefly explain:

	•	what your script does
	•	which issue it addresses
	•	any notes or limitations

Expectations
	•	Not every script will be merged — that’s fine
	•	The goal is learning and signal, not volume
	•	This week is about momentum and understanding, not perfection

If you have questions, ask on the relevant GitHub issue so answers are visible to everyone.
