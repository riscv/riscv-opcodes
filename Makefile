ISASIM_H := ../riscv-isa-sim/riscv/opcodes.h
PK_H := ../riscv-pk/pk/riscv-opc.h
GAS_H := ../riscv-gcc/binutils-2.21.1/include/opcode/riscv-opc.h
XCC_H := ../riscv-gcc/gcc-4.6.1/gcc/config/riscv/riscv-opc.h 

install: $(ISASIM_H) $(PK_H) $(GAS_H) $(XCC_H) inst.chisel instr-table.tex

$(ISASIM_H): opcodes parse-opcodes
	./parse-opcodes -isasim < $< > $@
	./parse-opcodes -isasim < opcodes-hwacha-ut > ../riscv-isa-sim/hwacha/opcodes_hwacha_ut_half.h

$(PK_H): opcodes parse-opcodes
	./parse-opcodes -disasm < $< > $@

$(GAS_H): opcodes opcodes-hwacha opcodes-hwacha-ut opcodes-rvc opcodes-custom opcodes-hwacha-pseudo parse-opcodes
	./parse-opcodes -disasm < $< > $@
	./parse-opcodes -disasm < opcodes-hwacha >> $@
	./parse-opcodes -disasm < opcodes-hwacha-pseudo >> $@
	./parse-opcodes -disasm < opcodes-hwacha-ut >> $@
	./parse-opcodes -disasm < opcodes-rvc >> $@
	./parse-opcodes -disasm < opcodes-custom >> $@

$(XCC_H): opcodes parse-opcodes
	./parse-opcodes -disasm < $< > $@

inst.chisel: opcodes parse-opcodes
	./parse-opcodes -chisel < $< > $@
	./parse-opcodes -chisel < opcodes-custom >> $@

instr-table.tex: opcodes parse-opcodes
	./parse-opcodes -tex < $< > $@

.PHONY : install
