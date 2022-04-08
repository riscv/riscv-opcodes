EXTENSIONS := "rv*" "unratified/rv*"
ISASIM_H := ../riscv-isa-sim/riscv/encoding.h
PK_H := ../riscv-pk/machine/encoding.h
ENV_H := ../riscv-tests/env/encoding.h
OPENOCD_H := ../riscv-openocd/src/target/riscv/encoding.h
INSTALL_HEADER_FILES := $(ISASIM_H) $(PK_H) $(ENV_H) $(OPENOCD_H)

default: everything

.PHONY : everything
everything:
	@./parse.py -c -chisel -sverilog -rust -latex $(EXTENSIONS)

.PHONY : c
c:
	@./parse.py -c $(EXTENSIONS)

.PHONY : chisel
chisel:
	@./parse.py -chisel $(EXTENSIONS)

.PHONY : latex
latex:
	@./parse.py -latex $(EXTENSIONS)

.PHONY : sverilog
sverilog:
	@./parse.py -sverilog $(EXTENSIONS)

.PHONY : rust
rust:
	@./parse.py -rust $(EXTENSIONS)

.PHONY : clean
clean:
	rm -f inst* priv-instr-table.tex encoding.out.h

.PHONY : install
install: c
	set -e; for FILE in $(INSTALL_HEADER_FILES); do cp -f encoding.out.h $$FILE; done

