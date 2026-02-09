#!/bin/sh
python3 src/shard/wiki_dump_to_jsonl_shards.py --dump /d/SotonLM/data/enwiki-latest-pages-articles.xml.bz2 --out-dir /d/SotonLM/data/raw/web --shard-mib 512 --buffer-size 10000 --seed 42
