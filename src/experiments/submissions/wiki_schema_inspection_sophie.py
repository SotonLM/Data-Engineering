import json
import os
from collections import defaultdict        

unique_division = set()
unique_source = set()

# check fields and unqiue values of division and source
with open("wikipedia_000000.jsonl", "r", encoding="utf-8") as f:
    first_line = next(f)
    record = json.loads(first_line)
    # check division and source values
    if "division" in record:
        unique_division.add(record["division"])

    if "source" in record:
        unique_source.add(record["source"])
    
    print("=" * 60)
    print("Starting field inspection on the first record:")
    print("Fields:", record.keys())

print("\nUnique division values:")
print(unique_division)

print("\nUnique source values:")
print(unique_source)

print("\n")
print("=" * 60) 


def inspect_jsonl_files(directory):
    # init counters
    total_records = 0
    field_presence = defaultdict(int)
    empty_counts = defaultdict(int)
    token_lengths = defaultdict(list)
    
    # get json files
    jsonl_files = [f for f in os.listdir(directory) if f.endswith(".jsonl")]

    if not jsonl_files:
        print("No .jsonl files found.")
        return

    print(f"Found {len(jsonl_files)} json file(s)")
    print("=" * 60)

    # read each json file
    for filename in jsonl_files:
        file_record_count = 0
        
        path = os.path.join(directory, filename)
        print(f"\nReading {filename}")
        # Open file and read line by line
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                
                if not line:
                    continue

                total_records += 1
                file_record_count += 1
                record = json.loads(line)
            
                for field, value in record.items():
                    field_presence[field] += 1
                    
                    if value in [None, "", [], {}]:
                        empty_counts[field] += 1

                    if isinstance(value, str) and value.strip():
                        tokens = value.split()
                        token_lengths[field].append(len(tokens))   
                        
            print(f"Records in {filename}: {file_record_count}")
    
    print("\n")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total records: {total_records}\n")
    
    print("Fields detected:")
    for field in sorted(field_presence.keys()):
        print(f"- {field} ({field_presence[field]} records)")

    print("\nEmpty field counts:")
    for field in sorted(empty_counts.keys()):
        print(f"- {field}: {empty_counts[field]}")

    print("\nToken statistics (text fields only):")
    for field in sorted(token_lengths.keys()):
        lengths = token_lengths[field]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            print(
                f"- {field}: min={min(lengths)}, "
                f"max={max(lengths)}, "
                f"avg={avg_len:.2f}"
            )


if __name__ == "__main__":
    inspect_jsonl_files(".")

