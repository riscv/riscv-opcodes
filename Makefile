EXTENSIONS := "rv*" "unratified/rv*"
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)
PSEUDO_FLAG := $(if $(PSEUDO),-pseudo,)

ifeq ($(shell command -v uv 2>/dev/null),)
	RUNNER := PYTHONPATH=src python -m
else
	RUNNER := $(RUNNER)
endif

.PHONY : default
default: everything

.PHONY: everything encoding.out.h inst.chisel inst.go latex inst.sverilog inst.rs clean install instr-table.tex priv-instr-table.tex inst.spinalhdl pseudo test

pseudo:
	@$(MAKE) PSEUDO=1 everything

everything:
	@$(RUNNER) riscv_opcodes $(PSEUDO_FLAG) -c -go -chisel -sverilog -rust -latex -spinalhdl $(EXTENSIONS)

encoding.out.h:
	@$(RUNNER) riscv_opcodes -c $(PSEUDO_FLAG) $(EXTENSIONS)

inst.chisel:
	@$(RUNNER) riscv_opcodes -chisel $(PSEUDO_FLAG) $(EXTENSIONS)

inst.go:
	@$(RUNNER) riscv_opcodes -go $(PSEUDO_FLAG) $(EXTENSIONS)

latex:
	@$(RUNNER) riscv_opcodes -latex $(PSEUDO_FLAG) $(EXTENSIONS)

inst.sverilog:
	@$(RUNNER) riscv_opcodes -sverilog $(PSEUDO_FLAG) $(EXTENSIONS)

inst.rs:
	@$(RUNNER) riscv_opcodes -rust $(PSEUDO_FLAG) $(EXTENSIONS)

clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

install: everything
	set -e; \
	for FILE in $(INSTALL_HEADER_FILES); do \
	    cp -f encoding.out.h $$FILE; \
	done

test:
	@$(RUNNER) -m unittest -b tests/test.py

instr-table.tex: latex

priv-instr-table.tex: latex

inst.spinalhdl:
	@$(RUNNER) riscv_opcodes -spinalhdl $(PSEUDO_FLAG) $(EXTENSIONS)
