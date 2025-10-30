#!/usr/bin/env python3
"""
Assignment 5 – Instruction Frequency by Opcode Value
----------------------------------------------------
Parses all instruction files under:
    ./extensions/
    ./extensions/unratified/

Extracts:
  - mnemonic (first word)
  - opcode (from '6..2=' pattern)

Groups mnemonics by opcode value, prints summary,
and saves detailed mapping + count to 'opcode_frequencies.txt'.
"""

import os
import re
from collections import defaultdict

# Directories
BASE_DIR = os.getcwd()
EXT_DIRS = [
    os.path.join(BASE_DIR, "extensions"),
    os.path.join(BASE_DIR, "extensions", "unratified")
]
OUT_FILE = "opcode_frequencies.txt"

# Regex to extract the base opcode value
RE_OPCODE = re.compile(r"6\.\.2\s*=\s*([\w\.xX]+)")

def extract_opcode_pairs(filepath):
    """Extract (mnemonic, opcode_value) pairs from a single file."""
    pairs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                # Skip blank lines, comments, and pseudo ops
                if not line or line.startswith("#") or line.startswith("$pseudo_op"):
                    continue

                parts = line.split()
                mnemonic = parts[0]
                match = RE_OPCODE.search(line)
                if match:
                    opcode_val = match.group(1).strip()
                    pairs.append((mnemonic, opcode_val))
    except Exception as e:
        print(f" [WARN] Could not read {filepath}: {e}")
    return pairs

def collect_opcode_frequencies(ext_dirs):
    """Aggregate opcode → list of mnemonics."""
    freq = defaultdict(list)

    for directory in ext_dirs:
        if not os.path.isdir(directory):
            print(f" [WARN] Directory not found: {directory}")
            continue

        print(f" Scanning directory: {directory}")
        for fname in sorted(os.listdir(directory)):
            fpath = os.path.join(directory, fname)
            if not os.path.isfile(fpath):
                continue

            for mnemonic, opcode_val in extract_opcode_pairs(fpath):
                if mnemonic not in freq[opcode_val]:
                    freq[opcode_val].append(mnemonic)
    return freq

def save_to_text(mapping, out_file):
    """Write opcode frequencies to a readable text file with counts."""
    with open(out_file, "w", encoding="utf-8") as f:
        for opcode, mnems in sorted(mapping.items()):
            count = len(mnems)
            f.write(f"{opcode} ({count} instructions): {', '.join(sorted(mnems))}\n")

def main():
    print(" Counting instruction frequencies by base opcode...\n")
    freq = collect_opcode_frequencies(EXT_DIRS)

    if not freq:
        print("  No opcodes found.")
        return

    print("\n=== Opcode Frequency Summary ===")
    print(f"{'Opcode':<10} | {'#Instr':>6}")
    print("-" * 22)
    for opcode, mnems in sorted(freq.items()):
        print(f"{opcode:<10} | {len(mnems):>6}")

    save_to_text(freq, OUT_FILE)
    print(f"\n Saved opcode frequencies with counts to: {OUT_FILE}")

if __name__ == "__main__":
    main()
