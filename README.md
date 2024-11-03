# riscv-opcodes

This repository enumerates standard RISC-V instruction opcodes and control/status registers. It also contains a script to convert them into various formats (C, Scala, LaTeX).

Artifacts like `encoding.h`, `latex-tables`, etc., from this repo are used in tools and projects such as Spike, PK, and the RISC-V Manual.

## Table of Contents

1. [Project Structure](#project-structure)
2. [File Naming Policy](#file-naming-policy)
3. [Encoding Syntax](#encoding-syntax)
4. [Usage](#usage)
5. [Artifact Generation](#artifact-generation)
6. [Adding a New Extension](#adding-a-new-extension)
7. [Debugging](#debugging)
8. [Contributing.md](CONTRIBUTING.md)

---

## Project Structure

```bash
├── constants.py    # contains variables, constants and data-structures used in parse.py
├── encoding.h      # the template encoding.h file
├── LICENSE         # license file
├── Makefile        # makefile to generate artifacts
├── parse.py        # performs checks and generates artifacts
├── README.md       # this file
├── rv*             # instruction opcode files
└── unratified      # contains unratified instruction opcode files
```

---

## File Naming Policy

This project follows a specific file naming convention for instruction encodings:

- **`rv_x`**: Instructions common to both 32-bit and 64-bit modes of extension `X`.
- **`rv32_x`**: Instructions specific to `rv32x` (e.g., `brev8`).
- **`rv64_x`**: Instructions specific to `rv64x` (e.g., `addw`).
- **`rv_x_y`**: Instructions valid when both extensions `X` and `Y` are enabled. Canonical ordering as specified by the RISC-V spec should be followed.
- **`unratified/`**: Contains instruction encodings that are not ratified yet, following the same policy.

For instructions present in multiple extensions where the spec is vague, the encoding should be placed in the canonically ordered first extension and imported into others using `$import`.

---

## Encoding Syntax

Instruction encoding files in this project use the following syntax:

- **Keywords**: `$import` and `$pseudo_op` are keywords used to indicate special operations.
- **Operators**: `::` defines relationships between extensions and instructions; `..` defines bit ranges.
- **Comments**: Use `#` for comments. Inline comments are not supported.

### Instruction Categories

1. **Regular Instructions**: Instructions with unique opcodes.

   - **Syntax**: `<instruction name> <arguments>`
   - **Example**:

     ```plaintext
     lui     rd imm20 6..2=0x0D 1..0=3
     beq     bimm12hi rs1 rs2 bimm12lo 14..12=0 6..2=0x18 1..0=3
     ```

   - **Bit Encoding Types**:
     - _Single Bit Assignment_: `<bit-position>=<value>`
     - _Range Assignment_: `<msb>..<lsb>=<value>`

2. **Pseudo Instructions** (`$pseudo_op`): Aliases for regular instructions with restricted bit encodings.

   - **Syntax**: `$pseudo_op <extension>::<base-instruction> <instruction name> <instruction args> <bit-encodings>`
     - `<extension>`: Specifies the extension which contains the base instruction.
     - `<base-instruction>`: Indicates the name of the instruction this pseudo-instruction is an alias of.
     - The remaining fields are the same as the regular instruction syntax, where all the arguments and the fields of the pseudo instruction are specified.
   - **Example**:

     ```plaintext
     $pseudo_op rv_zicsr::csrrs frflags rd 19..15=0 31..20=0x001 14..12=2 6..2=0x1C 1..0=3
     ```

   - **Recommendation**: If a ratified instruction is a `$pseudo_op` of a regular unratified instruction, it is recommended to maintain this `$pseudo_op` relationship. Define the new instruction as a `$pseudo_op` of the unratified regular instruction to avoid overlapping opcodes for users experimenting with unratified extensions.

3. **Imported Instructions** (`$import`): Instructions borrowed from another extension.
   - These are instructions borrowed from an extension into a new or different extension/sub-extension. Only regular instructions can be imported. Pseudo-ops or already imported instructions cannot be imported.
   - **Syntax**: `$import <extension>::<instruction name> <instruction args>`
   - **Example**:
     ```plaintext
     $import rv32_zkne::aes32esmi
     ```

### Restrictions

- Pseudo-ops or already imported instructions cannot be imported again.
- A base instruction for a pseudo-op cannot be a pseudo-op itself.

---

## Flow for parse.py

The `parse.py` Python file is used to perform checks on the current set of instruction encodings and also generates multiple artifacts: LaTeX tables, `encoding.h` header file, etc. This section provides a brief overview of the flow within the Python file.

1. **Initial Setup**:

   - `parse.py` creates a list of all `rv*` files currently checked into the repo (including those inside the `unratified` directory).
   - It starts parsing each file line by line.

2. **First Pass - Regular Instructions**:

   - Capture only regular instructions and ignore imported or pseudo instructions.
   - **Checks performed**:

     - For range-assignment syntax, the _msb_ (most significant bit) position must be higher than the _lsb_ (least significant bit) position.
     - The value of the range must be representable in the space identified by _msb_ and _lsb_.
     - Values for the same bit positions should not be defined multiple times.
     - All bit positions must be accounted for (either as arguments or constant value fields).

   - **Dictionary Creation**:

     - Create a dictionary for each instruction with the following fields:
       - `encoding`: A 32-bit string defining the encoding of the instruction. `-` is used to represent instruction argument fields.
       - `extension`: String indicating which extension/filename this instruction was picked from.
       - `mask`: A 32-bit hex value indicating the bits of the encodings that must be checked for legality.
       - `match`: A 32-bit hex value indicating the values the encoding must take for the bits which are set as 1 in the mask.
       - `variable_fields`: A list of arguments required by the instruction.

   - Add the dictionary elements to a main `instr_dict` dictionary under the instruction node. This process continues until all regular instructions have been processed.

3. **Second Pass - Pseudo Instructions**:

   - Process `$pseudo_op` instructions.
   - **Checks performed**:
     - Verify if the _base-instruction_ of the pseudo instruction exists in the relevant extension/filename.
     - The remaining part of the syntax undergoes the same checks as above.
     - If the checks pass and the _base-instruction_ is not already added to the main `instr_dict`, then add the pseudo-instruction to the list.

4. **Third Pass - Imported Instructions**:

   - Process imported instructions.

5. **Special Case**:
   - If the _base-instruction_ for a pseudo-instruction is not present in the main `instr_dict` after the first pass, it may be due to processing only a subset of extensions where the _base-instruction_ is not included.

## Artifact Generation and Usage

The `parse.py` script can generate the following artifacts:

- **`instr_dict.json`**: Contains the main dictionary `instr_dict`, formatted as JSON. In this file, dots in instruction names are replaced with underscores. Previously, this file was generated as instr_dict.yaml. Since JSON is a subset of YAML, it can still be read by any YAML parser.
- **`encoding.out.h`**: A header file used by tools such as Spike, PK, etc.
- **`instr-table.tex`**: LaTeX table of instructions for the RISC-V unprivileged specification.
- **`priv-instr-table.tex`**: LaTeX table of instructions for the RISC-V privileged specification.
- **`inst.chisel`**: Chisel code for decoding instructions.
- **`inst.sverilog`**: SystemVerilog code for decoding instructions.
- **`inst.rs`**: Rust code containing mask and match variables for all instructions.
- **`inst.spinalhdl`**: SpinalHDL code for decoding instructions.
- **`inst.go`**: Go code for decoding instructions.

### Prerequisites

Ensure you have the required Python dependencies installed. Run the following commands:

```bash
sudo apt-get install python3-pip
```

### Generating Artifacts

To generate all artifacts for all instructions currently checked in, run make from the root directory. This will produce the following output:

```plaintext
Running with args : ['./parse.py', '-c', '-go', '-chisel', '-sverilog', '-rust', '-latex', '-spinalhdl', 'rv*', 'unratified/rv*']
Extensions selected : ['rv*', 'unratified/rv*']
INFO:: encoding.out.h generated successfully
INFO:: inst.chisel generated successfully
INFO:: inst.spinalhdl generated successfully
INFO:: inst.sverilog generated successfully
INFO:: inst.rs generated successfully
INFO:: inst.go generated successfully
INFO:: instr-table.tex generated successfully
INFO:: priv-instr-table.tex generated successfully

```

### Selecting Specific Extensions

By default, all extensions are enabled. To select a subset of extensions, modify the EXTENSIONS variable in the Makefile to include only the filenames of interest. For example, to include only the I and M extensions:
For example if you want only the I and M extensions you can do the following:

```bash
make EXTENSIONS='rv*_i rv*_m'
```

This will produce the following output:

```plaintext
  Running with args : ['./parse.py', '-c', '-go', '-chisel', '-sverilog', '-rust', '-latex', 'rv32_i', 'rv64_i', 'rv_i', 'rv64_m', 'rv_m']
  Extensions selected : ['rv32_i', 'rv64_i', 'rv_i', 'rv64_m', 'rv_m']
  INFO:: encoding.out.h generated successfully
  INFO:: inst.chisel generated successfully
  INFO:: inst.sverilog generated successfully
  INFO:: inst.rs generated successfully
  INFO:: instr-table.tex generated successfully
  INFO:: priv-instr-table.tex generated successfully
```

### Generating Specific Artifacts

To generate specific artifacts, use one or more of the following targets:

- `inst.c`,`rs`,`chisel`,`sverilog`, `instr-table.tex`

For example, if you want to generate using Chisel and Rust, run the following command:

```bash
  make inst.chisel inst.rs
```

### Cleaning Up

To remove all generated artifacts, use the `clean` target:

```bash
make clean
```

---

## Adding a New Extension

To add a new extension of instructions, follow these steps:

1. **Create the Extension File**:

- Create a new `rv*` file according to the policy defined in the [File Structure](#file-naming-policy).

2. **Run Checks and Generate Artifacts**:

- From the root directory, run the `make` command to ensure that all checks pass and that all artifacts are generated correctly.
- A successful run will produce the following output:

  ```plaintext
  Running with args : ['./parse.py', '-c', '-chisel', '-sverilog', '-rust', '-latex', 'rv*', 'unratified/rv*']
  Extensions selected : ['rv*', 'unratified/rv*']
  INFO:: encoding.out.h generated successfully
  INFO:: inst.chisel generated successfully
  INFO:: inst.sverilog generated successfully
  INFO:: inst.rs generated successfully
  INFO:: instr-table.tex generated successfully
  INFO:: priv-instr-table.tex generated successfully
  ```

3. **Submit for Review**:
   - Create a pull request (PR) to submit your changes for review.

## Ensure you follow these steps carefully to integrate the new extension properly.

## How do I find where an instruction is defined?

You can locate the definition of an instruction using one of the following methods:

1. **Using `grep`**:
   ```bash
   grep "^\s*<instr-name>" rv* unratified/rv*
   ```
2. **Using `make`**:

- Run make to generate the instr_dict.json file.
- Open instr_dict.json and search for the instruction.
- The extension field in the file will indicate which file the instruction was picked from.

---

## Debugging

To enable debug logs in parse.py:

1. Modify the logging level in parse.py:

```python
level=logging.INFO
```

Change it to:

```python
level=logging.DEBUG
```

2. Example debug output:

```bash
DEBUG:: Parsing File: ./rv_i
DEBUG::      Processing line: lui rd imm20 6..2=0x0D 1..0=3
```
