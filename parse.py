#!/usr/bin/env python3
import collections
import logging
import pprint
import sys

import yaml

from c_utils import make_c
from chisel_utils import make_chisel
from constants import *
from go_utils import make_go
from latex_utils import make_latex_table, make_priv_latex_table
from rust_utils import make_rust
from shared_utils import add_segmented_vls_insn, create_inst_dict
from sverilog_utils import make_sverilog

LOG_FORMAT = "%(levelname)s:: %(message)s"
LOG_LEVEL = logging.INFO

pretty_printer = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


def remove_non_extensions(args):
    """
    Removes non-extension flags from the command-line arguments.
    """
    extensions = args[1:]
    flags = ["-c", "-latex", "-chisel", "-sverilog", "-rust", "-go", "-spinalhdl"]
    return [ext for ext in extensions if ext not in flags]


def process_instruction_dict(extensions, include_pseudo):
    """
    Processes the instruction dictionary by creating and adding segmented instructions.
    """
    instr_dict = create_inst_dict(extensions, include_pseudo)
    instr_dict = add_segmented_vls_insn(instr_dict)
    return collections.OrderedDict(sorted(instr_dict.items()))


def write_yaml(instr_dict, filename="instr_dict.yaml"):
    """
    Writes the instruction dictionary to a YAML file.
    """
    with open(filename, "w") as outfile:
        yaml.dump(instr_dict, outfile, default_flow_style=False)


def generate_outputs(instr_dict, extensions):
    """
    Generates output files based on selected extensions and flags.
    """
    # Dictionary to map extensions to their respective functions and logging messages
    extension_map = {
        "-c": {
            "function": lambda: make_c(
                collections.OrderedDict(
                    sorted(
                        create_inst_dict(
                            extensions, False, include_pseudo_ops=emitted_pseudo_ops
                        ).items()
                    )
                )
            ),
            "message": "encoding.out.h generated successfully",
        },
        "-chisel": {
            "function": lambda: make_chisel(instr_dict),
            "message": "inst.chisel generated successfully",
        },
        "-spinalhdl": {
            "function": lambda: make_chisel(instr_dict, spinal_hdl=True),
            "message": "inst.spinalhdl generated successfully",
        },
        "-sverilog": {
            "function": lambda: make_sverilog(instr_dict),
            "message": "inst.sverilog generated successfully",
        },
        "-rust": {
            "function": lambda: make_rust(instr_dict),
            "message": "inst.rs generated successfully",
        },
        "-go": {
            "function": lambda: make_go(instr_dict),
            "message": "inst.go generated successfully",
        },
        "-latex": {
            "function": lambda: (make_latex_table(), make_priv_latex_table()),
            "message": [
                "instr-table.tex generated successfully",
                "priv-instr-table.tex generated successfully",
            ],
        },
    }

    for ext, actions in extension_map.items():
        if ext in extensions:
            try:
                actions["function"]()
                if isinstance(actions["message"], list):
                    for msg in actions["message"]:
                        logging.info(msg)
                else:
                    logging.info(actions["message"])

            except Exception as e:
                logging.error(f"Error generating output for {ext}: {e}")


def main():
    """
    Main function for processing and generation of files based on command-line arguments.
    """
    print(f"Running with args : {sys.argv}")
    extensions = remove_non_extensions(sys.argv)
    print(f"Extensions selected : {extensions}")

    include_pseudo = "-go" in sys.argv[1:]
    instr_dict = process_instruction_dict(extensions, include_pseudo)

    write_yaml(instr_dict)
    generate_outputs(instr_dict, sys.argv[1:])


if __name__ == "__main__":
    main()