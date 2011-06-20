ISASIM_H := ../riscv-isa-run/riscv/opcodes.h
PK_H := ../pk/pk/riscv-opc.h
XCC_H := ../xcc/src/include/opcode/mips-riscv-opc.h

install: $(ISASIM_H) $(PK_H) $(XCC_H) inst.v instr-table.tex

$(ISASIM_H): opcodes parse-opcodes
	./parse-opcodes -isasim < $< > $@

$(PK_H): opcodes parse-opcodes
	./parse-opcodes -disasm < $< > $@

$(XCC_H): opcodes parse-opcodes
	./parse-opcodes -disasm < $< > $@

inst.v: opcodes parse-opcodes
	./parse-opcodes -verilog < $< > $@

instr-table.tex: opcodes parse-opcodes
	./parse-opcodes -tex < $< > $@

.PHONY : install
