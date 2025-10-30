#!/usr/bin/env python3
"""
Assignment 2 – Opcode Search
----------------------------
Searches all files under ./extensions/ for instruction mnemonics.

Usage:
    python search_op.py ADD
    python search_op.py add --ignore-case
    python search_op.py "LW|SW" --regex --ignore-case
    python search_op.py lw -i
    python search_op.py "^f.*\.s$" -r -i

Options:
    --ignore-case / -i   : Case-insensitive search
    --regex / -r         : Treat the query as a regular expression

Outputs:
    search.json  → structured search results, later added to .gitignore
"""

import os
import re
import json
import argparse

EXT_DIR = os.path.join(os.getcwd(), "extensions")  # auto-detect path
OUT_FILE = "search.json"

def iter_files(root):
    """Yield full paths for all files under 'root'."""
    for dirpath, _, files in os.walk(root):
        for f in files:
            yield os.path.join(dirpath, f)

def search_opcodes(root_dir, query, ignore_case=False, use_regex=False):
    """Search all opcode files for lines matching the query."""
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(query if use_regex else re.escape(query), flags)

    results = []

    for path in iter_files(root_dir):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, raw in enumerate(f, start=1):
                    line = raw.strip()
                    # skip comments / blanks
                    if not line or line.startswith("#"):
                        continue
                    if pattern.search(line):
                        results.append({
                            "file": os.path.relpath(path, start=os.getcwd()),
                            "line": line_no,
                            "text": line
                        })
        except Exception as e:
            print(f" [WARN] Could not read {path}: {e}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Search for RISC-V opcodes or patterns")
    parser.add_argument("query", help="Mnemonic or regex pattern to search for")
    parser.add_argument("--ignore-case", "-i", action="store_true", help="Case-insensitive match")
    parser.add_argument("--regex", "-r", action="store_true", help="Treat query as regex")
    args = parser.parse_args()

    if not os.path.isdir(EXT_DIR):
        print(f" Extensions directory not found: {EXT_DIR}")
        return

    print(f" Searching in: {EXT_DIR}")
    print(f" Query: {args.query} | ignore-case={args.ignore_case} | regex={args.regex}\n")

    matches = search_opcodes(EXT_DIR, args.query, args.ignore_case, args.regex)

    print(f" Found {len(matches)} matches")

    if matches:
        for m in matches[:10]:
            print(f"{m['file']}:{m['line']} → {m['text']}")
        if len(matches) > 10:
            print(" (Showing first 10 only)")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2)

    print(f" Results saved to {OUT_FILE}")

if __name__ == "__main__":
    main()
