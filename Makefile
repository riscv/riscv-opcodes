EXTENSIONS := "rv*" "unratified/rv*"
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)

default: everything

.PHONY: everything encoding.out.h inst.chisel inst.go latex inst.sverilog inst.rs clean install instr-table.tex priv-instr-table.tex inst.spinalhdl

everything:
	@./parse.py -c -go -chisel -sverilog -rust -latex -spinalhdl $(EXTENSIONS)

encoding.out.h:
	@./parse.py -c rv* unratified/rv_* unratified/rv32* unratified/rv64*

inst.chisel:
	@./parse.py -chisel $(EXTENSIONS)

inst.go:
	@./parse.py -go $(EXTENSIONS)

latex:
	@./parse.py -latex $(EXTENSIONS)

inst.sverilog:
	@./parse.py -sverilog $(EXTENSIONS)

inst.rs:
	@./parse.py -rust $(EXTENSIONS)

clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

install: everything
	set -e; \
	for FILE in $(INSTALL_HEADER_FILES); do \
	    cp -f encoding.out.h $$FILE; \
	done

instr-table.tex: latex

priv-instr-table.tex: latex

inst.spinalhdl:
	@./parse.py -spinalhdl $(EXTENSIONS)
