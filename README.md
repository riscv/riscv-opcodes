# **riscv-opcodes**

This repository enumerates standard RISC-V instruction opcodes and control/status registers. It includes tools to convert these into various formats (e.g., C, Scala, LaTeX) for use in projects like Spike, PK, and the RISC-V Manual.

---

## **Table of Contents**
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Usage](#usage)
4. [Artifact Generation](#artifact-generation)
5. [Resources](#resources)
6. [Contributing](#contributing)
7. [License](#license)

---

## **Introduction**
The **riscv-opcodes** repository serves as the single source of truth for RISC-V instruction encodings and related metadata. Artifacts generated from this repository, such as `encoding.h` and LaTeX tables, are used in various RISC-V software and documentation projects.

---

## **Project Structure**

```bash
├── utils/           # Utility scripts for artifact generation
├── extensions/      # Instruction opcode files, organized by extensions
│   ├── rv*          # Ratified instructions
│   └── unratified/  # Unratified instruction files
├── LICENSE          # Licensing information
├── Makefile         # Build script for generating artifacts
├── parse.py         # Script to parse and validate encodings
└── README.md        # This file
```

For detailed guidelines on contributing, see the [Contributing Guidelines](CONTRIBUTING.md).

---

## **Usage**

### **Generating Artifacts**
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-repo-name>/riscv-opcodes.git
   cd riscv-opcodes
   ```
2. Run the following command to generate artifacts:
   ```bash
   make
   ```

Generated artifacts (e.g., `encoding.h`, LaTeX tables) will appear in the output directory.

---

## **Artifact Generation**

The following artifacts are generated using `parse.py` or `make`:

| Artifact                | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `instr_dict.json`        | Contains the full dictionary of instruction encodings in JSON format.       |
| `encoding.out.h`         | Header file used by tools like Spike and PK.                               |
| `instr-table.tex`        | LaTeX table for the RISC-V unprivileged spec.                              |
| `priv-instr-table.tex`   | LaTeX table for the RISC-V privileged spec.                                 |
| `inst.chisel`            | Chisel code for instruction decoding.                                      |
| `inst.sverilog`          | System Verilog code for instruction decoding.                              |
| `inst.rs`                | Rust code with mask and match variables.                                   |
| `inst.spinalhdl`         | SpinalHDL code for instruction decoding.                                   |
| `inst.go`                | Go code for instruction decoding.                                          |

### **Commands**

- **Generate All Artifacts**:
  ```bash
  make
  ```

- **Generate Specific Artifacts**:
  To generate specific artifacts, modify the `EXTENSIONS` variable in the `Makefile` or use:
  ```bash
  make EXTENSIONS='rv*_i rv*_m'
  ```

- **Generate Using Specific Targets**:
  ```bash
  ./parse.py -c EXTENSIONS='rv*_i rv*_m'
  ```

- **Clean Artifacts**:
  To remove all generated artifacts, run:
  ```bash
  make clean
  ```

---

## **Resources**

- [RISC-V Official Documentation](https://riscv.org/specifications/)
- [Spike RISC-V Simulator](https://github.com/riscv-software-src/riscv-isa-sim)
- [RISC-V Foundation](https://riscv.org/)

---

## **Contributing**

We welcome contributions! Please read the [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

If you're adding a new instruction, extension, or artifact:
- Follow the **File Naming Policy** and **Encoding Syntax** guidelines in the [Contributing Guidelines](CONTRIBUTING.md).
- Run the `parse.py` script to validate your changes.

---

## **License**

This repository is licensed under the [BSD-3-Clause License](LICENSE).
