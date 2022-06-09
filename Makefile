EXTENSIONS := "rv*" "unratified/rv*"
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)

default: everything

.PHONY : everything
everything:
	@./parse.py -c -go -chisel -sverilog -rust -latex -spinalhdl $(EXTENSIONS)

.PHONY : encoding.out.h
encoding.out.h:
	@./parse.py -c rv* unratified/rv_* unratified/rv32* unratified/rv64*

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

.PHONY : clean
clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

.PHONY : install
install: everything
	set -e; for FILE in $(INSTALL_HEADER_FILES); do cp -f encoding.out.h $$FILE; done

.PHONY: instr-table.tex
instr-table.tex: latex

.PHONY: priv-instr-table.tex
priv-instr-table.tex: latex

.PHONY: inst.spinalhdl
inst.spinalhdl:
	@./parse.py -spinalhdl $(EXTENSIONS)
