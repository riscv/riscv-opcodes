"""
This allows running as a module, i.e. `python3 -m riscv_opcodes` which
we wouldn't normally need, but the `coverage` tool doesn't work on
installed scripts - you can't do `coverage run riscv_opcodes` because it
looks for a Python file called `riscv_opcodes` in the current directory.
"""

from .parse import main

main()
