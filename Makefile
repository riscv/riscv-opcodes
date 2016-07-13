SHELL := /bin/sh

ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/pk/encoding.h
FESVR_H := ../riscv-fesvr/fesvr/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
GAS_H := ../riscv-gnu-toolchain/binutils/include/opcode/riscv-opc.h
LLVM_TD := ../riscv-llvm/lib/Target/RISCV/RISCVInstrFormatBits.td

ALL_OPCODES := opcodes-pseudo opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom

install: $(ISASIM_H) $(PK_H) $(FESVR_H) $(ENV_H) $(GAS_H) $(LLVM_TD) inst.chisel instr-table.tex priv-instr-table.tex

$(ISASIM_H) $(PK_H) $(FESVR_H) $(ENV_H): $(ALL_OPCODES) parse-opcodes encoding.h
	cp encoding.h $@
	cat opcodes opcodes-rvc-pseudo opcodes-rvc opcodes-custom | ./parse-opcodes -c >> $@

$(GAS_H) $(XCC_H): $(ALL_OPCODES) parse-opcodes
	cat $(ALL_OPCODES) | ./parse-opcodes -c > $@

$(LLVM_TD): $(ALL_OPCODES) parse-opcodes
	cat $(ALL_OPCODES) | ./parse-opcodes -llvm > $@

inst.chisel: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-custom opcodes-pseudo | ./parse-opcodes -chisel > $@

instr-table.tex: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-pseudo | ./parse-opcodes -tex > $@

priv-instr-table.tex: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-pseudo | ./parse-opcodes -privtex > $@

.PHONY : install
