#!/usr/bin/env python3
"""
Assignment 3 – Count Instructions per Extension (File-Based)
------------------------------------------------------------
Counts how many real (non-pseudo) instructions exist
in each extension file under:
    ./extensions/
    ./extensions/unratified/

Output:
  • Prints table of 'extension → count'
  • Saves results to 'extension_counts.csv'
"""

import os
import csv

# Base directories
BASE_DIR = os.getcwd()
EXT_DIRS = [
    os.path.join(BASE_DIR, "extensions"),
    os.path.join(BASE_DIR, "extensions", "unratified")
]
OUT_FILE = "extension_counts.csv"

def count_instructions_in_file(filepath):
    """Count valid instruction lines in a single file."""
    count = 0
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                # Skip comments, blanks, pseudo-ops
                if not line or line.startswith("#") or line.startswith("$pseudo_op"):
                    continue
                count += 1
    except Exception as e:
        print(f" [WARN] Could not read {filepath}: {e}")
    return count

def count_all_extensions(dirs):
    """Go through all specified directories and count each extension file."""
    results = {}

    for d in dirs:
        if not os.path.isdir(d):
            print(f" [WARN] Directory missing: {d}")
            continue

        print(f" Scanning: {d}")
        for fname in sorted(os.listdir(d)):
            fpath = os.path.join(d, fname)
            if not os.path.isfile(fpath):
                continue

            # Use the filename as the extension name (no path)
            ext_name = fname
            instr_count = count_instructions_in_file(fpath)
            if instr_count > 0:
                results[ext_name] = instr_count

    return results

def save_to_csv(results, out_file):
    with open(out_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Extension_File", "Instruction_Count"])
        for ext, count in sorted(results.items()):
            writer.writerow([ext, count])

def main():
    print(" Counting instructions per extension file...\n")
    counts = count_all_extensions(EXT_DIRS)

    if not counts:
        print(" No instructions found.")
        return

    print("\n=== Instruction Counts per Extension File ===")
    print(f"{'Extension File':<25} | {'Count':>6}")
    print("-" * 36)
    for ext, cnt in sorted(counts.items()):
        print(f"{ext:<25} | {cnt:>6}")

    save_to_csv(counts, OUT_FILE)
    print(f"\n Saved results to: {OUT_FILE}")

if __name__ == "__main__":
    main()
