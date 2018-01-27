SHELL := /bin/sh

ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
FESVR_H := ../riscv-fesvr/fesvr/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h

ALL_OPCODES := opcodes-pseudo opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom opcodes-v

install: $(ISASIM_H) $(PK_H) $(FESVR_H) $(ENV_H) $(OPENOCD_H) inst.chisel instr-table.tex priv-instr-table.tex

$(ISASIM_H) $(PK_H) $(FESVR_H) $(ENV_H) $(OPENOCD_H): $(ALL_OPCODES) parse-opcodes encoding.h
	cp encoding.h $@
	cat opcodes opcodes-rvc-pseudo opcodes-rvc opcodes-custom | ./parse-opcodes -c >> $@

inst.chisel: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-custom opcodes-pseudo | ./parse-opcodes -chisel > $@

inst.go: opcodes opcodes-pseudo parse-opcodes
	cat opcodes opcodes-pseudo | ./parse-opcodes -go > $@

instr-table.tex: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-pseudo opcodes-v | ./parse-opcodes -tex > $@

priv-instr-table.tex: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-pseudo | ./parse-opcodes -privtex > $@

.PHONY : install
