#!/usr/bin/env python3

import argparse
import json
import logging
import pprint

from c_utils import make_c
from chisel_utils import make_chisel
from constants import emitted_pseudo_ops
from go_utils import make_go
from latex_utils import make_latex_table, make_priv_latex_table
from rust_utils import make_rust
from shared_utils import add_segmented_vls_insn, create_inst_dict
from sverilog_utils import make_sverilog

LOG_FORMAT = "%(levelname)s:: %(message)s"
LOG_LEVEL = logging.INFO

pretty_printer = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


def generate_extensions(
    extensions: list[str],
    include_pseudo: bool,
    c: bool,
    chisel: bool,
    spinalhdl: bool,
    sverilog: bool,
    rust: bool,
    go: bool,
    latex: bool,
):
    instr_dict = create_inst_dict(extensions, include_pseudo)
    instr_dict = dict(sorted(instr_dict.items()))

    with open("instr_dict.json", "w", encoding="utf-8") as outfile:
        json.dump(add_segmented_vls_insn(instr_dict), outfile, indent=2)

    if c:
        instr_dict_c = create_inst_dict(
            extensions, False, include_pseudo_ops=emitted_pseudo_ops
        )
        instr_dict_c = dict(sorted(instr_dict_c.items()))
        make_c(instr_dict_c)
        logging.info("encoding.out.h generated successfully")

    if chisel:
        make_chisel(instr_dict)
        logging.info("inst.chisel generated successfully")

    if spinalhdl:
        make_chisel(instr_dict, True)
        logging.info("inst.spinalhdl generated successfully")

    if sverilog:
        make_sverilog(instr_dict)
        logging.info("inst.sverilog generated successfully")

    if rust:
        make_rust(instr_dict)
        logging.info("inst.rs generated successfully")

    if go:
        make_go(instr_dict)
        logging.info("inst.go generated successfully")

    if latex:
        make_latex_table()
        logging.info("instr-table.tex generated successfully")
        make_priv_latex_table()
        logging.info("priv-instr-table.tex generated successfully")


def main():
    parser = argparse.ArgumentParser(description="Generate RISC-V constants headers")
    parser.add_argument(
        "-pseudo", action="store_true", help="Include pseudo-instructions"
    )
    parser.add_argument("-c", action="store_true", help="Generate output for C")
    parser.add_argument(
        "-chisel", action="store_true", help="Generate output for Chisel"
    )
    parser.add_argument(
        "-spinalhdl", action="store_true", help="Generate output for SpinalHDL"
    )
    parser.add_argument(
        "-sverilog", action="store_true", help="Generate output for SystemVerilog"
    )
    parser.add_argument("-rust", action="store_true", help="Generate output for Rust")
    parser.add_argument("-go", action="store_true", help="Generate output for Go")
    parser.add_argument("-latex", action="store_true", help="Generate output for Latex")
    parser.add_argument(
        "extensions",
        nargs="*",
        help="Extensions to use. This is a glob of the rv_.. files, e.g. 'rv*' will give all extensions.",
    )

    args = parser.parse_args()

    print(f"Extensions selected : {args.extensions}")

    generate_extensions(
        args.extensions,
        args.pseudo,
        args.c,
        args.chisel,
        args.spinalhdl,
        args.sverilog,
        args.rust,
        args.go,
        args.latex,
    )


if __name__ == "__main__":
    main()
