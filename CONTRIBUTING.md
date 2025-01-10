# **Contributing to riscv-opcodes**

Thank you for considering contributing to the **riscv-opcodes** project!
This guide will help you understand the repository structure, coding conventions, and contribution workflow.

---

## **Table of Contents**

1. [Getting Started](#getting-started)
2. [File Naming Policy](#file-naming-policy)
3. [Encoding Syntax](#encoding-syntax)
4. [Adding a New Extension](#adding-a-new-extension)
5. [Testing and Validation](#testing-and-validation)
6. [Code of Conduct](#code-of-conduct)

---

## **Getting Started**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/<your-repo-name>/riscv-opcodes.git
   cd riscv-opcodes
   ```

2. **Set Up Dependencies**
   Ensure you have Python installed (version >= 3.7).
   Install dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Understand the Project Structure**
   Familiarize yourself with the files and folders as explained in the [README.md](README.md).

4. **Create a Branch**
   Before starting your work, create a feature branch:
   ```bash
   git checkout -b <your-branch-name>
   ```

---

## **File Naming Policy**

- **`rv_x`**: Instructions common to both 32-bit and 64-bit modes of extension `X`.
- **`rv32_x`**: Instructions specific to `rv32x` (e.g., `brev8`).
- **`rv64_x`**: Instructions specific to `rv64x` (e.g., `addw`).
- **`rv_x_y`**: Instructions valid when both extensions `X` and `Y` are enabled.
  - **Canonical Ordering**: Follow the RISC-V specification for ordering extensions (e.g., `rv_zknh` for `Zkn` + `Zknh`).

- **`unratified/`**: Contains instruction encodings that are not ratified yet, following the same naming policy.

**Note**: If an instruction belongs to multiple extensions, place the encoding in the canonically ordered first extension and use `$import` to share it.

---

## **Encoding Syntax**

### **Keywords**
- `$import`: Used for importing instructions from another extension.
- `$pseudo_op`: Used to define pseudo-instructions.

### **Operators**
- `::`: Defines relationships between extensions and instructions.
- `..`: Defines bit ranges.

### **Comments**
- Use `#` for comments. Inline comments are not supported.

### **Regular Instruction Syntax**
```plaintext
<instruction name> <arguments> <bit-encodings>
```

### **Pseudo-Instruction Syntax**
```plaintext
$pseudo_op <extension>::<base-instruction> <instruction name> <instruction args> <bit-encodings>
```

### **Imported Instruction Syntax**
```plaintext
$import <extension>::<instruction name> <instruction args>
```

---

## **Adding a New Extension**

1. **Create Encoding Files**
   Place your new encoding file in the `extensions/` folder. Use the [File Naming Policy](#file-naming-policy) to name your file appropriately.

2. **Define Instructions**
   Follow the [Encoding Syntax](#encoding-syntax) to add your instructions in the new file.
   Example:
   ```plaintext
   lui rd imm20 6..2=0x0D 1..0=3
   ```

3. **Import Instructions (if needed)**
   If an instruction is shared between extensions, use `$import`.
   Example:
   ```plaintext
   $import rv_zicsr::csrrs
   ```

4. **Update Dependencies**
   If your new extension requires dependencies (e.g., artifacts), update `Makefile` or other relevant scripts.

---

## **Testing and Validation**

1. **Run the Parser**
   After making changes, validate your encodings using:
   ```bash
   python parse.py
   ```

   Fix any errors or warnings reported by the script.

2. **Check Artifacts**
   Ensure that the artifacts generated (e.g., `encoding.h`, LaTeX tables) include your changes:
   ```bash
   make
   ```

3. **Review Your Changes**
   Verify that your changes are aligned with the project’s conventions and do not break existing functionality.

---

## **Code of Conduct**

By contributing to this project, you agree to adhere to the following principles:
- Be respectful and collaborative.
- Provide clear documentation for any new instructions or extensions.
- Report bugs and propose changes in a constructive manner.
- Ensure your contributions comply with the [LICENSE](LICENSE).

---

## **Submitting Your Contribution**

1. **Commit Your Changes**
   Use clear and concise commit messages:
   ```bash
   git add .
   git commit -m "Add <description of change>"
   ```

2. **Push Your Branch**
   Push your branch to your forked repository:
   ```bash
   git push origin <your-branch-name>
   ```

3. **Create a Pull Request**
   Open a pull request from your branch to the `main` branch of this repository.

4. **Address Feedback**
   Be prepared to make revisions based on reviewer feedback.

---

We look forward to your contributions! 😊
