EXTENSIONS := "rv*" "unratified/rv*"
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)
PSEUDO_FLAG := $(if $(PSEUDO),-pseudo,)


.PHONY : default
default: everything

.PHONY: everything encoding.out.h inst.chisel inst.go latex inst.sverilog inst.rs clean install instr-table.tex priv-instr-table.tex inst.spinalhdl pseudo test

pseudo:
	@$(MAKE) PSEUDO=1 everything

everything:
	@uv run riscv_opcodes $(PSEUDO_FLAG) -c -go -chisel -sverilog -rust -latex -spinalhdl $(EXTENSIONS)

encoding.out.h:
	@uv run riscv_opcodes -c $(PSEUDO_FLAG) $(EXTENSIONS)

inst.chisel:
	@uv run riscv_opcodes -chisel $(PSEUDO_FLAG) $(EXTENSIONS)

inst.go:
	@uv run riscv_opcodes -go $(PSEUDO_FLAG) $(EXTENSIONS)

latex:
	@uv run riscv_opcodes -latex $(PSEUDO_FLAG) $(EXTENSIONS)

inst.sverilog:
	@uv run riscv_opcodes -sverilog $(PSEUDO_FLAG) $(EXTENSIONS)

inst.rs:
	@uv run riscv_opcodes -rust $(PSEUDO_FLAG) $(EXTENSIONS)

clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

install: everything
	set -e; \
	for FILE in $(INSTALL_HEADER_FILES); do \
	    cp -f encoding.out.h $$FILE; \
	done

test:
	@uv run -m unittest -b tests/test.py

instr-table.tex: latex

priv-instr-table.tex: latex

inst.spinalhdl:
	@uv run riscv_opcodes -spinalhdl $(PSEUDO_FLAG) $(EXTENSIONS)
