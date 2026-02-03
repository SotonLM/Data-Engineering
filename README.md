# SotonLM Data Team — Current Instructions

This week is about **exploring data ingestion** by writing small, standalone scripts.

The aim is **not** to build production pipelines yet.  
The aim is to experiment locally, learn what works, and submit scripts for review.

---

## What You Should Do

### Write a Small Data Collection Script

Create a script that:
- fetches data from a website or set of pages
- crawls through pages, APIs, or paginated content
- extracts text or useful metadata
- runs **locally** on your machine
- only collects a **small amount of data** for testing

Examples:
- crawling a section of Wikipedia
- scraping blog posts or documentation
- pulling articles from a public website
- iterating through a paginated archive

This is exploratory — it does **not** need to be perfect or complete.

---

## Where Your Script Should Go

Place your script in the following directory:
- src/ingest/submissions/

### Script Naming (Important)

Your script filename **must include your name**, for example:
- wiki_scrape_jamie.py
- blog_crawler_mykyta.py
- news_fetch_ricky.py

This makes ownership clear and avoids conflicts.

---

## Simple Rules (Please Follow)

- Run scripts **locally only**
- Do **not** commit large datasets
- Do **not** modify core pipeline code
- Do **not** change schemas or directory structure
- Scripts should be standalone and easy to run

If you generate output files:
- keep them very small
- clearly mark them as sample/test data

---

## How To Submit Your Work

1. Create a new branch:
```bash
git checkout -b feature/<your-name>/<script-name>
```

2.	Add your script
3.	Commit and push:

```bash
git add .
git commit -m "Add <your-name>'s data collection script"
git push
```

4.	Open a Pull Request on GitHub

In the PR description, briefly explain:
	•	what the script does
	•	what site or source it targets
	•	any limitations or notes

That’s all.
