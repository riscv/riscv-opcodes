#!/usr/bin/env python3
"""
Assignment 4 – List Unique (opcode, funct3, funct7) Combinations
---------------------------------------------------------------
Parses all extension files under:
    ./extensions/
    ./extensions/unratified/

Extracts unique triplets of (opcode, funct3, funct7)
based on patterns found in each instruction line.

Output:
  • combinations.json – JSON mapping:
        { extension: [ {opcode, funct3, funct7}, ... ] }
"""

import os
import re
import json

# Directories
BASE_DIR = os.getcwd()
EXT_DIRS = [
    os.path.join(BASE_DIR, "extensions"),
    os.path.join(BASE_DIR, "extensions", "unratified")
]
OUT_FILE = "combinations.json"

# Regex patterns to match fields
RE_FUNCT7 = re.compile(r"31\.\.25\s*=\s*([\w\.xX]+)")
RE_FUNCT3 = re.compile(r"14\.\.12\s*=\s*([\w\.xX]+)")
RE_OPCODE = re.compile(r"6\.\.2\s*=\s*([\w\.xX]+)")

def extract_fields_from_line(line):
    """Extract (opcode, funct3, funct7) from a single instruction line."""
    funct7 = None
    funct3 = None
    opcode = None

    m7 = RE_FUNCT7.search(line)
    m3 = RE_FUNCT3.search(line)
    m_op = RE_OPCODE.search(line)

    if m7:
        funct7 = m7.group(1).strip()
    if m3:
        funct3 = m3.group(1).strip()
    if m_op:
        opcode = m_op.group(1).strip()

    if opcode or funct3 or funct7:
        return (opcode, funct3, funct7)
    return None

def parse_extension_file(filepath):
    """Parse one extension file and return unique (opcode, funct3, funct7) sets."""
    combos = set()
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("$pseudo_op"):
                    continue
                fields = extract_fields_from_line(line)
                if fields:
                    combos.add(fields)
    except Exception as e:
        print(f"[WARN] Could not read {filepath}: {e}")
    return combos

def collect_combinations(ext_dirs):
    """Collect unique field combinations grouped by extension file name."""
    result = {}

    for d in ext_dirs:
        if not os.path.isdir(d):
            print(f"[WARN] Missing directory: {d}")
            continue

        print(f" Parsing directory: {d}")
        for fname in sorted(os.listdir(d)):
            fpath = os.path.join(d, fname)
            if not os.path.isfile(fpath):
                continue

            ext_name = fname  # filename as extension name
            combos = parse_extension_file(fpath)
            if combos:
                result[ext_name] = [
                    {"opcode": (op or ""), "funct3": (f3 or ""), "funct7": (f7 or "")}
                    for (op, f3, f7) in sorted(combos, key=lambda x: (x[0] or "", x[1] or "", x[2] or ""))
        ]

    return result

def main():
    print("Extracting unique (opcode, funct3, funct7) combinations...\n")
    combos_by_ext = collect_combinations(EXT_DIRS)

    if not combos_by_ext:
        print(" No field combinations found.")
        return

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combos_by_ext, f, indent=2)

    print(f" Extracted combinations for {len(combos_by_ext)} extensions.")
    print(f" Saved results to: {OUT_FILE}")

if __name__ == "__main__":
    main()
