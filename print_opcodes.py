#!/usr/bin/env python3
"""
Assignment 1 – Print All Opcodes  (text-based format)
----------------------------------------------------
Scans:
    Vyoma_RISCV_Cohort_Work/riscv-opcodes/extensions/
Extracts the first word from each instruction line.
Skips lines starting with "$pseudo_op".
Prints sorted mnemonics and writes them to all_opcodes.txt.
"""

import os

# EXT_DIR = r"Vyoma_RISCV_Cohort_Work\riscv-opcodes\extensions"
EXT_DIR = os.path.join(os.getcwd(), "extensions")
OUT_FILE = "all_opcodes.txt"

def collect_opcodes(root_dir): # type: ignore
    opcodes = set() # type: ignore

    for dirpath, _, files in os.walk(root_dir): # type: ignore
        for fname in files: # type: ignore
            #e.g., rv32_i, rv64_m
            path = os.path.join(dirpath, fname) # type: ignore
            try:
                with open(path, "r", encoding="utf-8") as f: # type: ignore
                    for line in f:
                        line = line.strip()
                        # Skip blank lines and comments
                        if not line or line.startswith("#"):
                            continue
                        # Split by whitespace
                        parts = line.split()
                        if not parts:
                            continue
                        first = parts[0]
                        # Ignore pseudo-ops
                        if first.startswith("$pseudo_op"):
                            continue
                        opcodes.add(first) # type: ignore
            except Exception as e:
                print(f" [WARN] Could not read {path}: {e}")

    return sorted(opcodes, key=str.lower) # type: ignore

def main():
    print(f"🔍 Scanning: {EXT_DIR}\n")
    all_ops = collect_opcodes(EXT_DIR) # type: ignore

    if not all_ops:
        print(" No opcodes found. Check path or file content.")
        return

    print("=== All RISC-V Opcodes (Sorted) ===\n")
    for op in all_ops: # type: ignore
        print(op) # type: ignore

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(all_ops) + "\n") # type: ignore

    print(f"\n Total opcodes: {len(all_ops)}") # type: ignore
    print(f" Saved to: {OUT_FILE}")

if __name__ == "__main__":
    main()
