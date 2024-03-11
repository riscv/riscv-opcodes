EXTENSIONS := "rv*" "unratified/rv*"
SPIKE_EXTENSIONS := "rv*" "unratified/rv_*" "unratified/rv32*" "unratified/rv64*"
SPIKE_PSEUDO_OPS := 'pause' 'prefetch_i' 'prefetch_r' 'prefetch_w' 'rstsa16' 'rstsa32' 'srli32_u' 'slli_rv128' 'slli_rv32' 'srai_rv128' 'srai_rv32' 'srli_rv128' 'srli_rv32' 'umax32'
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)

default: everything

.PHONY : everything
everything:
	@./parse.py -c -go -chisel -sverilog -rust -latex -spinalhdl -include_pseudo -extensions $(EXTENSIONS)

.PHONY : encoding.out.h
encoding.out.h:
	@./parse.py -c -include_pseudo -pseudo_ops $(SPIKE_PSEUDO_OPS) -extensions $(SPIKE_EXTENSIONS)

.PHONY : inst.chisel
inst.chisel:
	@./parse.py -chisel -extensions $(EXTENSIONS)

.PHONY : inst.go
inst.go:
	@./parse.py -go -include_pseudo -extensions $(EXTENSIONS)

.PHONY : latex
latex:
	@./parse.py -latex -extensions $(EXTENSIONS)

.PHONY : inst.sverilog
inst.sverilog:
	@./parse.py -sverilog -extensions $(EXTENSIONS)

.PHONY : inst.rs
inst.rs:
	@./parse.py -rust -extensions $(EXTENSIONS)

.PHONY : clean
clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

.PHONY : install
install: encoding.out.h
	set -e; for FILE in $(INSTALL_HEADER_FILES); do cp -f encoding.out.h $$FILE; done

.PHONY: instr-table.tex
instr-table.tex: latex

.PHONY: priv-instr-table.tex
priv-instr-table.tex: latex

.PHONY: inst.spinalhdl
inst.spinalhdl:
	@./parse.py -spinalhdl $(EXTENSIONS)
