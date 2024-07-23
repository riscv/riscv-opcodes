# Define a list of all extensions to process
EXTENSIONS := "rv*" "unratified/rv*"

# Define paths to header files for other projects
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h

# Define a list of header files for installation
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)

# Default target builds everything
default: everything

.PHONY : everything
everything:
	@./parse.py -c -go -chisel -sverilog -rust -latex -spinalhdl $(EXTENSIONS)

# Generate a unified encoding header file for all extensions
.PHONY : encoding.out.h
encoding.out.h:
	@./parse.py -c rv* unratified/rv_* unratified/rv32* unratified/rv64*

# Generate instruction definitions in specific languages
.PHONY : inst.chisel
inst.chisel:
	@./parse.py -chisel $(EXTENSIONS)

.PHONY : inst.go
inst.go:
	@./parse.py -go $(EXTENSIONS)

.PHONY : latex
latex:
	@./parse.py -latex $(EXTENSIONS)

.PHONY : inst.sverilog
inst.sverilog:
	@./parse.py -sverilog $(EXTENSIONS)

.PHONY : inst.rs
inst.rs:
	@./parse.py -rust $(EXTENSIONS)

# Clean up generated files
.PHONY : clean
clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

# Install generated encoding header to other projects
.PHONY : install
install: everything
	set -e; for FILE in $(INSTALL_HEADER_FILES); do cp -f encoding.out.h $$FILE; done

# Alias for generating LaTeX table (existing behavior)
.PHONY: instr-table.tex
instr-table.tex: latex

# Alias for generating private instruction table (existing behavior)
.PHONY: priv-instr-table.tex
priv-instr-table.tex: latex

# Generate SpinalHDL definitions
.PHONY: inst.spinalhdl
inst.spinalhdl:
	@./parse.py -spinalhdl $(EXTENSIONS)
