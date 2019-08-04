SHELL := /bin/sh

ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
FESVR_H := ../riscv-isa-sim/fesvr/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h

ALL_OPCODES := opcodes-pseudo opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom opcodes-rvv opcodes-rvv-pseudo

install: $(ISASIM_H) $(PK_H) $(FESVR_H) $(ENV_H) $(OPENOCD_H) inst.chisel instr-table.tex priv-instr-table.tex

$(ISASIM_H) $(PK_H) $(FESVR_H) $(ENV_H) $(OPENOCD_H): $(ALL_OPCODES) parse_opcodes encoding.h
	cp encoding.h $@
	cat opcodes opcodes-rvc-pseudo opcodes-rvc opcodes-custom opcodes-rvv | python ./parse_opcodes -c >> $@

inst.chisel: $(ALL_OPCODES) parse_opcodes
	cat opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom opcodes-rvv opcodes-rvv-pseudo opcodes-pseudo | ./parse_opcodes -chisel > $@

inst.go: opcodes opcodes-pseudo parse_opcodes
	cat opcodes opcodes-pseudo | ./parse_opcodes -go > $@

inst.sverilog: opcodes opcodes-pseudo parse_opcodes
	cat opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom opcodes-pseudo | ./parse_opcodes -sverilog > $@

instr-table.tex: $(ALL_OPCODES) parse_opcodes
	cat opcodes opcodes-pseudo | ./parse_opcodes -tex > $@

priv-instr-table.tex: $(ALL_OPCODES) parse_opcodes
	cat opcodes opcodes-pseudo | ./parse_opcodes -privtex > $@

.PHONY : install
