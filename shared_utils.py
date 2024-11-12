#!/usr/bin/env python3
import copy
import glob
import logging
import os
import pprint
import re
from itertools import chain
from typing import Dict, Optional, TypedDict

from constants import (
    arg_lut,
    fixed_ranges,
    imported_regex,
    overlapping_extensions,
    overlapping_instructions,
    pseudo_regex,
    single_fixed,
)

LOG_FORMAT = "%(levelname)s:: %(message)s"
LOG_LEVEL = logging.INFO

pretty_printer = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


# Log an error message
def log_and_exit(message: str):
    """Log an error message and exit the program."""
    logging.error(message)
    raise SystemExit(1)


# Initialize encoding to 32-bit '-' values
def initialize_encoding(bits: int = 32) -> "list[str]":
    """Initialize encoding with '-' to represent don't care bits."""
    return ["-"] * bits


# Validate bit range and value
def validate_bit_range(msb: int, lsb: int, entry_value: int, line: str):
    """Validate the bit range and entry value."""
    if msb < lsb:
        log_and_exit(
            f'{line.split(" ")[0]:<10} has position {msb} less than position {lsb} in its encoding'
        )

    if entry_value >= (1 << (msb - lsb + 1)):
        log_and_exit(
            f'{line.split(" ")[0]:<10} has an illegal value {entry_value} assigned as per the bit width {msb - lsb}'
        )


# Split the instruction line into name and remaining part
def parse_instruction_line(line: str) -> "tuple[str, str]":
    """Parse the instruction name and the remaining encoding details."""
    name, remaining = line.split(" ", 1)
    name = name.replace(".", "_")  # Replace dots for compatibility
    remaining = remaining.lstrip()  # Remove leading whitespace
    return name, remaining


# Verify Overlapping Bits
def check_overlapping_bits(encoding: "list[str]", ind: int, line: str):
    """Check for overlapping bits in the encoding."""
    if encoding[31 - ind] != "-":
        log_and_exit(
            f'{line.split(" ")[0]:<10} has {ind} bit overlapping in its opcodes'
        )


# Update encoding for fixed ranges
def update_encoding_for_fixed_range(
    encoding: "list[str]", msb: int, lsb: int, entry_value: int, line: str
):
    """
    Update encoding bits for a given bit range.
    Checks for overlapping bits and assigns the value accordingly.
    """
    for ind in range(lsb, msb + 1):
        check_overlapping_bits(encoding, ind, line)
        bit = str((entry_value >> (ind - lsb)) & 1)
        encoding[31 - ind] = bit


# Process fixed bit patterns
def process_fixed_ranges(remaining: str, encoding: "list[str]", line: str):
    """Process fixed bit ranges in the encoding."""
    for s2, s1, entry in fixed_ranges.findall(remaining):
        msb, lsb, entry_value = int(s2), int(s1), int(entry, 0)

        # Validate bit range and entry value
        validate_bit_range(msb, lsb, entry_value, line)
        update_encoding_for_fixed_range(encoding, msb, lsb, entry_value, line)

    return fixed_ranges.sub(" ", remaining)


# Process single bit assignments
def process_single_fixed(remaining: str, encoding: "list[str]", line: str):
    """Process single fixed assignments in the encoding."""
    for lsb, value, _drop in single_fixed.findall(remaining):
        lsb = int(lsb, 0)
        value = int(value, 0)

        check_overlapping_bits(encoding, lsb, line)
        encoding[31 - lsb] = str(value)


# Main function to check argument look-up table
def check_arg_lut(args: "list[str]", encoding_args: "list[str]", name: str):
    """Check if arguments are present in arg_lut."""
    for arg in args:
        if arg not in arg_lut:
            arg = handle_arg_lut_mapping(arg, name)
        msb, lsb = arg_lut[arg]
        update_encoding_args(encoding_args, arg, msb, lsb)


# Handle missing argument mappings
def handle_arg_lut_mapping(arg: str, name: str):
    """Handle cases where an argument needs to be mapped to an existing one."""
    parts = arg.split("=")
    if len(parts) == 2:
        existing_arg, _new_arg = parts
        if existing_arg in arg_lut:
            arg_lut[arg] = arg_lut[existing_arg]
        else:
            log_and_exit(
                f" Found field {existing_arg} in variable {arg} in instruction {name} "
                f"whose mapping in arg_lut does not exist"
            )
    else:
        log_and_exit(
            f" Found variable {arg} in instruction {name} "
            f"whose mapping in arg_lut does not exist"
        )
    return arg


# Update encoding args with variables
def update_encoding_args(encoding_args: "list[str]", arg: str, msb: int, lsb: int):
    """Update encoding arguments and ensure no overlapping."""
    for ind in range(lsb, msb + 1):
        check_overlapping_bits(encoding_args, ind, arg)
        encoding_args[31 - ind] = arg


# Compute match and mask
def convert_encoding_to_match_mask(encoding: "list[str]") -> "tuple[str, str]":
    """Convert the encoding list to match and mask strings."""
    match = "".join(encoding).replace("-", "0")
    mask = "".join(encoding).replace("0", "1").replace("-", "0")
    return hex(int(match, 2)), hex(int(mask, 2))


class SingleInstr(TypedDict):
    encoding: str
    variable_fields: "list[str]"
    extension: "list[str]"
    match: str
    mask: str


InstrDict = Dict[str, SingleInstr]


# Processing main function for a line in the encoding file
def process_enc_line(line: str, ext: str) -> "tuple[str, SingleInstr]":
    """
    This function processes each line of the encoding files (rv*). As part of
    the processing, the function ensures that the encoding is legal through the
    following checks::
        - there is no over specification (same bits assigned different values)
        - there is no under specification (some bits not assigned values)
        - bit ranges are in the format hi..lo=val where hi > lo
        - value assigned is representable in the bit range
        - also checks that the mapping of arguments of an instruction exists in
          arg_lut.
    If the above checks pass, then the function returns a tuple of the name and
    a dictionary containing basic information of the instruction which includes:
        - variables: list of arguments used by the instruction whose mapping
          exists in the arg_lut dictionary
        - encoding: this contains the 32-bit encoding of the instruction where
          '-' is used to represent position of arguments and 1/0 is used to
          reprsent the static encoding of the bits
        - extension: this field contains the rv* filename from which this
          instruction was included
        - match: hex value representing the bits that need to match to detect
          this instruction
        - mask: hex value representin the bits that need to be masked to extract
          the value required for matching.
    """
    encoding = initialize_encoding()

    # Parse the instruction line
    name, remaining = parse_instruction_line(line)

    # Process fixed ranges
    remaining = process_fixed_ranges(remaining, encoding, line)

    # Process single fixed assignments
    process_single_fixed(remaining, encoding, line)

    # Convert the list of encodings into a match and mask
    match, mask = convert_encoding_to_match_mask(encoding)

    # Check arguments in arg_lut
    args = single_fixed.sub(" ", remaining).split()
    encoding_args = encoding.copy()

    check_arg_lut(args, encoding_args, name)

    # Return single_dict
    return name, {
        "encoding": "".join(encoding),
        "variable_fields": args,
        "extension": [os.path.basename(ext)],
        "match": match,
        "mask": mask,
    }


# Extract ISA Type
def extract_isa_type(ext_name: str) -> str:
    """Extracts the ISA type from the extension name."""
    return ext_name.split("_")[0]


# Verify the types for RV*
def is_rv_variant(type1: str, type2: str) -> bool:
    """Checks if the types are RV variants (rv32/rv64)."""
    return (type2 == "rv" and type1 in {"rv32", "rv64"}) or (
        type1 == "rv" and type2 in {"rv32", "rv64"}
    )


# Check for same base ISA
def has_same_base_isa(type1: str, type2: str) -> bool:
    """Determines if the two ISA types share the same base."""
    return type1 == type2 or is_rv_variant(type1, type2)


# Compare the base ISA type of a given extension name against a list of extension names
def same_base_isa(ext_name: str, ext_name_list: "list[str]") -> bool:
    """Checks if the base ISA type of ext_name matches any in ext_name_list."""
    type1 = extract_isa_type(ext_name)
    return any(has_same_base_isa(type1, extract_isa_type(ext)) for ext in ext_name_list)


# Pad two strings to equal length
def pad_to_equal_length(str1: str, str2: str, pad_char: str = "-") -> "tuple[str, str]":
    """Pads two strings to equal length using the given padding character."""
    max_len = max(len(str1), len(str2))
    return str1.rjust(max_len, pad_char), str2.rjust(max_len, pad_char)


# Check compatibility for two characters
def has_no_conflict(char1: str, char2: str) -> bool:
    """Checks if two characters are compatible (either matching or don't-care)."""
    return char1 == "-" or char2 == "-" or char1 == char2


# Conflict check between two encoded strings
def overlaps(x: str, y: str) -> bool:
    """Checks if two encoded strings overlap without conflict."""
    x, y = pad_to_equal_length(x, y)
    return all(has_no_conflict(x[i], y[i]) for i in range(len(x)))


# Check presence of keys in dictionary.
def is_in_nested_dict(a: "dict[str, set[str]]", key1: str, key2: str) -> bool:
    """Checks if key2 exists in the dictionary under key1."""
    return key1 in a and key2 in a[key1]


# Overlap allowance
def overlap_allowed(a: "dict[str, set[str]]", x: str, y: str) -> bool:
    """Determines if overlap is allowed between x and y based on nested dictionary checks"""
    return is_in_nested_dict(a, x, y) or is_in_nested_dict(a, y, x)


# Check overlap allowance between extensions
def extension_overlap_allowed(x: str, y: str) -> bool:
    """Checks if overlap is allowed between two extensions using the overlapping_extensions dictionary."""
    return overlap_allowed(overlapping_extensions, x, y)


# Check overlap allowance between instructions
def instruction_overlap_allowed(x: str, y: str) -> bool:
    """Checks if overlap is allowed between two instructions using the overlapping_instructions dictionary."""
    return overlap_allowed(overlapping_instructions, x, y)


# Check 'nf' field
def is_segmented_instruction(instruction: SingleInstr) -> bool:
    """Checks if an instruction contains the 'nf' field."""
    return "nf" in instruction["variable_fields"]


# Expand 'nf' fields
def update_with_expanded_instructions(
    updated_dict: InstrDict, key: str, value: SingleInstr
):
    """Expands 'nf' fields in the instruction dictionary and updates it with new instructions."""
    for new_key, new_value in expand_nf_field(key, value):
        updated_dict[new_key] = new_value


# Process instructions, expanding segmented ones and updating the dictionary
def add_segmented_vls_insn(instr_dict: InstrDict) -> InstrDict:
    """Processes instructions, expanding segmented ones and updating the dictionary."""
    # Use dictionary comprehension for efficiency
    return dict(
        chain.from_iterable(
            (
                expand_nf_field(key, value)
                if is_segmented_instruction(value)
                else [(key, value)]
            )
            for key, value in instr_dict.items()
        )
    )


# Expand the 'nf' field in the instruction dictionary
def expand_nf_field(
    name: str, single_dict: SingleInstr
) -> "list[tuple[str, SingleInstr]]":
    """Validate and prepare the instruction dictionary."""
    validate_nf_field(single_dict, name)
    remove_nf_field(single_dict)
    update_mask(single_dict)

    name_expand_index = name.find("e")

    # Pre compute the base match value and encoding prefix
    base_match = int(single_dict["match"], 16)
    encoding_prefix = single_dict["encoding"][3:]

    expanded_instructions = [
        create_expanded_instruction(
            name, single_dict, nf, name_expand_index, base_match, encoding_prefix
        )
        for nf in range(8)  # Range of 0 to 7
    ]

    return expanded_instructions


# Validate the presence of 'nf'
def validate_nf_field(single_dict: SingleInstr, name: str):
    """Validates the presence of 'nf' in variable fields before expansion."""
    if "nf" not in single_dict["variable_fields"]:
        log_and_exit(f"Cannot expand nf field for instruction {name}")


# Remove 'nf' from variable fields
def remove_nf_field(single_dict: SingleInstr):
    """Removes 'nf' from variable fields in the instruction dictionary."""
    single_dict["variable_fields"].remove("nf")


# Update the mask to include the 'nf' field
def update_mask(single_dict: SingleInstr):
    """Updates the mask to include the 'nf' field in the instruction dictionary."""
    single_dict["mask"] = hex(int(single_dict["mask"], 16) | 0b111 << 29)


# Create an expanded instruction
def create_expanded_instruction(
    name: str,
    single_dict: SingleInstr,
    nf: int,
    name_expand_index: int,
    base_match: int,
    encoding_prefix: str,
) -> "tuple[str, SingleInstr]":
    """Creates an expanded instruction based on 'nf' value."""
    new_single_dict = copy.deepcopy(single_dict)

    # Update match value in one step
    new_single_dict["match"] = hex(base_match | (nf << 29))
    new_single_dict["encoding"] = format(nf, "03b") + encoding_prefix

    # Construct new instruction name
    new_name = (
        name
        if nf == 0
        else f"{name[:name_expand_index]}seg{nf + 1}{name[name_expand_index:]}"
    )

    return (new_name, new_single_dict)


# Return a list of relevant lines from the specified file
def read_lines(file: str) -> "list[str]":
    """Reads lines from a file and returns non-blank, non-comment lines."""
    with open(file, encoding="utf-8") as fp:
        lines = (line.rstrip() for line in fp)
        return [line for line in lines if line and not line.startswith("#")]


# Update the instruction dictionary
def process_standard_instructions(
    lines: "list[str]", instr_dict: InstrDict, file_name: str
):
    """Processes standard instructions from the given lines and updates the instruction dictionary."""
    for line in lines:
        if "$import" in line or "$pseudo" in line:
            continue
        logging.debug(f"Processing line: {line}")
        name, single_dict = process_enc_line(line, file_name)
        ext_name = os.path.basename(file_name)

        if name in instr_dict:
            var = instr_dict[name]["extension"]
            if same_base_isa(ext_name, var):
                log_and_exit(
                    f"Instruction {name} from {ext_name} is already added from {var} in same base ISA"
                )
            elif instr_dict[name]["encoding"] != single_dict["encoding"]:
                log_and_exit(
                    f"Instruction {name} from {ext_name} has different encodings in different base ISAs"
                )

            instr_dict[name]["extension"].extend(single_dict["extension"])
        else:
            for key, item in instr_dict.items():
                if (
                    overlaps(item["encoding"], single_dict["encoding"])
                    and not extension_overlap_allowed(ext_name, item["extension"][0])
                    and not instruction_overlap_allowed(name, key)
                    and same_base_isa(ext_name, item["extension"])
                ):
                    log_and_exit(
                        f'Instruction {name} in extension {ext_name} overlaps with {key} in {item["extension"]}'
                    )

            instr_dict[name] = single_dict


# Incorporate pseudo instructions into the instruction dictionary based on given conditions
def process_pseudo_instructions(
    lines: "list[str]",
    instr_dict: InstrDict,
    file_name: str,
    opcodes_dir: str,
    include_pseudo: bool,
    include_pseudo_ops: "list[str]",
):
    """Processes pseudo instructions from the given lines and updates the instruction dictionary."""
    for line in lines:
        if "$pseudo" not in line:
            continue
        logging.debug(f"Processing pseudo line: {line}")
        ext, orig_inst, pseudo_inst, line_content = pseudo_regex.findall(line)[0]
        ext_file = find_extension_file(ext, opcodes_dir)
        # print("ext_file",ext_file)
        validate_instruction_in_extension(orig_inst, ext_file, file_name, pseudo_inst)

        name, single_dict = process_enc_line(f"{pseudo_inst} {line_content}", file_name)
        if (
            orig_inst.replace(".", "_") not in instr_dict
            or include_pseudo
            or name in include_pseudo_ops
        ):
            if name not in instr_dict:
                instr_dict[name] = single_dict
                logging.debug(f"Including pseudo_op: {name}")
            else:
                if single_dict["match"] != instr_dict[name]["match"]:
                    instr_dict[f"{name}_pseudo"] = single_dict
                # TODO: This expression is always false since both sides are list[str].
                elif single_dict["extension"] not in instr_dict[name]["extension"]:  # type: ignore
                    instr_dict[name]["extension"].extend(single_dict["extension"])


# Integrate imported instructions into the instruction dictionary
def process_imported_instructions(
    lines: "list[str]", instr_dict: InstrDict, file_name: str, opcodes_dir: str
):
    """Processes imported instructions from the given lines and updates the instruction dictionary."""
    for line in lines:
        if "$import" not in line:
            continue
        logging.debug(f"Processing imported line: {line}")
        import_ext, reg_instr = imported_regex.findall(line)[0]
        ext_filename = find_extension_file(import_ext, opcodes_dir)

        validate_instruction_in_extension(reg_instr, ext_filename, file_name, line)

        with open(ext_filename, encoding="utf-8") as ext_file:
            for oline in ext_file:
                if re.findall(f"^\\s*{reg_instr}\\s+", oline):
                    name, single_dict = process_enc_line(oline, file_name)
                    if name in instr_dict:
                        if instr_dict[name]["encoding"] != single_dict["encoding"]:
                            log_and_exit(
                                f"Imported instruction {name} from {os.path.basename(file_name)} has different encodings"
                            )
                        instr_dict[name]["extension"].extend(single_dict["extension"])
                    else:
                        instr_dict[name] = single_dict
                    break


# Locate the path of the specified extension file, checking fallback directories
def find_extension_file(ext: str, opcodes_dir: str):
    """Finds the extension file path, considering the unratified directory if necessary."""
    ext_file = f"{opcodes_dir}/{ext}"
    if not os.path.exists(ext_file):
        ext_file = f"{opcodes_dir}/unratified/{ext}"
        if not os.path.exists(ext_file):
            log_and_exit(f"Extension {ext} not found.")
    # print(ext_file)
    return ext_file


# Confirm the presence of an original instruction in the corresponding extension file.
def validate_instruction_in_extension(
    inst: str, ext_filename: str, file_name: str, pseudo_inst: str
):
    """Validates if the original instruction exists in the dependent extension."""
    found = False
    with open(ext_filename, encoding="utf-8") as ext_file:
        for oline in ext_file:
            if re.findall(f"^\\s*{inst}\\s+", oline):
                found = True
                break
    if not found:
        log_and_exit(
            f"Original instruction {inst} required by pseudo_op {pseudo_inst} in {file_name} not found in {ext_file}"
        )


# Construct a dictionary of instructions filtered by specified criteria
def create_inst_dict(
    file_filter: "list[str]",
    include_pseudo: bool = False,
    include_pseudo_ops: "Optional[list[str]]" = None,
) -> InstrDict:
    """
    Creates a dictionary of instructions based on the provided file filters.

    This function return a dictionary containing all instructions associated
    with an extension defined by the file_filter input.
    Allowed input extensions: needs to be rv* file name without the 'rv' prefix i.e. '_i', '32_i', etc.
    Each node of the dictionary will correspond to an instruction which again is
    a dictionary. The dictionary contents of each instruction includes:
        - variables: list of arguments used by the instruction whose mapping
          exists in the arg_lut dictionary
        - encoding: this contains the 32-bit encoding of the instruction where
          '-' is used to represent position of arguments and 1/0 is used to
          reprsent the static encoding of the bits
        - extension: this field contains the rv* filename from which this
          instruction was included
        - match: hex value representing the bits that need to match to detect
          this instruction
        - mask: hex value representin the bits that need to be masked to extract
          the value required for matching.
    In order to build this dictionary, the function does 2 passes over the same
    rv<file_filter> file:
        - First pass: extracts all standard instructions, skipping pseudo ops
          and imported instructions. For each selected line, the `process_enc_line`
          function is called to create the dictionary contents of the instruction.
          Checks are performed to ensure that the same instruction is not added
          twice to the overall dictionary.
        - Second pass: parses only pseudo_ops. For each pseudo_op, the function:
            - Checks if the dependent extension and instruction exist.
            - Adds the pseudo_op to the dictionary if the dependent instruction
              is not already present; otherwise, it is skipped.
    """
    if include_pseudo_ops is None:
        include_pseudo_ops = []

    opcodes_dir = os.path.dirname(os.path.realpath(__file__)) + "/extensions"
    instr_dict: InstrDict = {}

    file_names = [
        file
        for fil in file_filter
        for file in sorted(glob.glob(f"{opcodes_dir}/{fil}"), reverse=True)
    ]

    logging.debug("Collecting standard instructions")
    for file_name in file_names:
        logging.debug(f"Parsing File: {file_name} for standard instructions")
        lines = read_lines(file_name)
        process_standard_instructions(lines, instr_dict, file_name)

    logging.debug("Collecting pseudo instructions")
    for file_name in file_names:
        logging.debug(f"Parsing File: {file_name} for pseudo instructions")
        lines = read_lines(file_name)
        process_pseudo_instructions(
            lines,
            instr_dict,
            file_name,
            opcodes_dir,
            include_pseudo,
            include_pseudo_ops,
        )

    logging.debug("Collecting imported instructions")

    for file_name in file_names:
        logging.debug(f"Parsing File: {file_name} for imported instructions")
        lines = read_lines(file_name)
        process_imported_instructions(lines, instr_dict, file_name, opcodes_dir)

    return instr_dict


# Extracts the extensions used in an instruction dictionary
def instr_dict_2_extensions(instr_dict: InstrDict) -> "list[str]":
    return list({item["extension"][0] for item in instr_dict.values()})


# Returns signed interpretation of a value within a given width
def signed(value: int, width: int) -> int:
    return value if 0 <= value < (1 << (width - 1)) else value - (1 << width)
