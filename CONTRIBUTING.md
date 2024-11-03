# Contributing to riscv-opcodes

Welcome, and thank you for your interest in contributing to the `riscv-opcodes` repository!

## Table of Contents
- [How to Contribute](#how-to-contribute)
- [Setting Up the Project](#setting-up-the-project)
- [Code Standards](#code-standards)
- [Running Tests](#running-tests)
- [Submitting a Pull Request](#submitting-a-pull-request)

## How to Contribute
- **Report an Issue**: For bugs or improvement suggestions, please open an issue.
- **Submit a Pull Request (PR)**: For fixes, improvements, or new features, submit a PR. It’s recommended to connect your PR with an open issue or prior discussion.

## Setting Up the Project
### Prerequisites
Ensure you have:
- Python 3.9+
- Necessary Python dependencies

### Generating Artifacts
To generate artifacts like `encoding.h` and `inst.rs`, navigate to the project root and run:
```bash
make
```
To generate specific artifacts like `inst.chisel` and `inst.rs`, run:
```bash
make inst.chisel inst.rs
```
To clean up generated files:
```bash
make clean
```
## Code Standards

- **File Naming**: Follow naming conventions provided in the README.
- **Syntax**: Use correct encoding syntax.
- **Comments**: Use `#` for comments, avoiding inline comments.

To format code, run:
```bash
pre-commit run --all-files
```
## Running Tests
Run tests to check encoding files and artifact generation before submitting a PR.

## Submitting a Pull Request

- **Branching**: Create a new branch for each PR.
- **Commits**: Use clear and descriptive commit messages.
- **PR Details**:
  - Reference any related issues.
  - Provide a summary of changes and their purpose.
  - Verify that all tests pass.

Thank you for contributing to the RISC-V community!
