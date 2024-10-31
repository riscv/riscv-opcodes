#!/usr/bin/env python3
import collections
import json
import logging
import pprint
import sys

from c_utils import *
from chisel_utils import *
from constants import *
from go_utils import *
from latex_utils import *
from rust_utils import *
from shared_utils import *
from sverilog_utils import *

LOG_FORMAT = "%(levelname)s:: %(message)s"
LOG_LEVEL = logging.INFO

pretty_printer = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

if __name__ == "__main__":
    print(f"Running with args : {sys.argv}")

    extensions = sys.argv[1:]

    targets = {
        "-c",
        "-chisel",
        "-go",
        "-latex",
        "-pseudo",
        "-rust",
        "-spinalhdl",
        "-sverilog",
    }

    extensions = [ext for ext in extensions if ext not in targets]
    print(f"Extensions selected : {extensions}")

    include_pseudo = "-pseudo" in sys.argv[1:]

    instr_dict = create_inst_dict(extensions, include_pseudo)

    with open("instr_dict.json", "w") as outfile:
        json.dump(add_segmented_vls_insn(instr_dict), outfile, indent=2)
    instr_dict = collections.OrderedDict(sorted(instr_dict.items()))

    if "-c" in sys.argv[1:]:
        instr_dict_c = create_inst_dict(
            extensions, False, include_pseudo_ops=emitted_pseudo_ops
        )
        instr_dict_c = collections.OrderedDict(sorted(instr_dict_c.items()))
        make_c(instr_dict_c)
        logging.info("encoding.out.h generated successfully")

    if "-chisel" in sys.argv[1:]:
        make_chisel(instr_dict)
        logging.info("inst.chisel generated successfully")

    if "-spinalhdl" in sys.argv[1:]:
        make_chisel(instr_dict, True)
        logging.info("inst.spinalhdl generated successfully")

    if "-sverilog" in sys.argv[1:]:
        make_sverilog(instr_dict)
        logging.info("inst.sverilog generated successfully")

    if "-rust" in sys.argv[1:]:
        make_rust(instr_dict)
        logging.info("inst.rs generated successfully")

    if "-go" in sys.argv[1:]:
        make_go(instr_dict)
        logging.info("inst.go generated successfully")

    if "-latex" in sys.argv[1:]:
        make_latex_table()
        logging.info("instr-table.tex generated successfully")
        make_priv_latex_table()
        logging.info("priv-instr-table.tex generated successfully")
