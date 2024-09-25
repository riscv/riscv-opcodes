#!/usr/bin/env python3
import copy
import re
import glob
import os
import pprint
import logging

from constants import *

LOG_FORMAT = '%(levelname)s:: %(message)s'
LOG_LEVEL = logging.INFO

pretty_printer = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


def process_enc_line(line, ext):
    '''
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
    '''
    encoding = initialize_encoding()
    name, remaining = parse_instruction_name(line)

    # Fixed ranges of the form hi..lo=val
    process_fixed_ranges(remaining, encoding, line)

    # Single fixed values of the form <lsb>=<val>
    remaining = process_single_fixed(remaining, encoding, line)

    # Create match and mask strings
    match, mask = create_match_and_mask(encoding)

    # Process instruction arguments
    args = process_arguments(remaining, encoding, name)

    # Create and return the final instruction dictionary
    instruction_dict = create_instruction_dict(encoding, args, ext, match, mask)

    return name, instruction_dict


def initialize_encoding():
    """Initialize a 32-bit encoding with '-' representing 'don't care'."""
    return ['-'] * 32


def parse_instruction_name(line):
    """Extract the instruction name and remaining part of the line."""
    name, remaining = line.split(' ', 1)
    name = name.replace('.', '_').lstrip()
    return name, remaining


def process_fixed_ranges(remaining, encoding, line):
    """Process bit ranges of the form hi..lo=val, checking for errors and updating encoding."""
    for s2, s1, entry in fixed_ranges.findall(remaining):
        msb, lsb = int(s2), int(s1)
        validate_bit_range(msb, lsb, line)
        validate_entry_value(msb, lsb, entry, line)
        update_encoding(msb, lsb, entry, encoding, line)


def validate_bit_range(msb, lsb, line):
    """Ensure that msb > lsb and raise an error if not."""
    if msb < lsb:
        log_and_exit(f"{get_instruction_name(line)} has msb < lsb in its encoding")


def validate_entry_value(msb, lsb, entry, line):
    """Ensure that the value assigned to a bit range is legal for its width."""
    entry_value = int(entry, 0)
    if entry_value >= (1 << (msb - lsb + 1)):
        log_and_exit(f"{get_instruction_name(line)} has an illegal value for the bit width {msb - lsb}")


def update_encoding(msb, lsb, entry, encoding, line):
    """Update the encoding array for a given bit range."""
    entry_value = int(entry, 0)
    for ind in range(lsb, msb + 1):
        if encoding[31 - ind] != '-':
            log_and_exit(f"{get_instruction_name(line)} has overlapping bits in its opcodes")
        encoding[31 - ind] = str((entry_value >> (ind - lsb)) & 1)


def process_single_fixed(remaining, encoding, line):
    """Process single fixed values of the form <lsb>=<val>."""
    for lsb, value, _ in single_fixed.findall(remaining):
        lsb = int(lsb, 0)
        value = int(value, 0)
        if encoding[31 - lsb] != '-':
            log_and_exit(f"{get_instruction_name(line)} has overlapping bits in its opcodes")
        encoding[31 - lsb] = str(value)
    return fixed_ranges.sub(' ', remaining)


def create_match_and_mask(encoding):
    """Generate match and mask strings from the encoding array."""
    match = ''.join(encoding).replace('-', '0')
    mask = ''.join(encoding).replace('0', '1').replace('-', '0')
    return match, mask


def process_arguments(remaining, encoding, name):
    """Process instruction arguments and update the encoding with argument positions."""
    args = single_fixed.sub(' ', remaining).split()
    encoding_args = encoding.copy()
    for arg in args:
        if arg not in arg_lut:
            handle_missing_arg(arg, name)
        msb, lsb = arg_lut[arg]
        update_arg_encoding(msb, lsb, arg, encoding_args, name)
    return args, encoding_args


def handle_missing_arg(arg, name):
    """Handle missing argument mapping in arg_lut."""
    if '=' in arg and (existing_arg := arg.split('=')[0]) in arg_lut:
        arg_lut[arg] = arg_lut[existing_arg]
    else:
        log_and_exit(f"Variable {arg} in instruction {name} not mapped in arg_lut")


def update_arg_encoding(msb, lsb, arg, encoding_args, name):
    """Update the encoding array with the argument positions."""
    for ind in range(lsb, msb + 1):
        if encoding_args[31 - ind] != '-':
            log_and_exit(f"Variable {arg} overlaps in bit {ind} in instruction {name}")
        encoding_args[31 - ind] = arg


def create_instruction_dict(encoding, args, ext, match, mask):
    """Create the final dictionary for the instruction."""
    return {
        'encoding': ''.join(encoding),
        'variable_fields': args,
        'extension': [os.path.basename(ext)],
        'match': hex(int(match, 2)),
        'mask': hex(int(mask, 2)),
    }


def log_and_exit(message):
    """Log an error message and exit the program."""
    logging.error(message)
    raise SystemExit(1)


def get_instruction_name(line):
    """Helper to extract the instruction name from a line."""
    return line.split(' ')[0]

def overlaps(x, y):
    """
    Check if two bit strings overlap without conflicts.
    
    Args:
        x (str): First bit string.
        y (str): Second bit string.
    
    Returns:
        bool: True if the bit strings overlap without conflicts, False otherwise.
        
    In the context of RISC-V opcodes, this function ensures that the bit ranges 
    defined by two different bit strings do not conflict.
    """
    
    # Minimum length of the two strings
    min_len = min(len(x), len(y))
    
    for char_x, char_y in zip(x[:min_len], y[:min_len]):
        if char_x != '-' and char_y != '-' and char_x != char_y:
            return False
    
    return True


def overlap_allowed(a, x, y):
    """
    Check if there is an overlap between keys and values in a dictionary.
    
    Args:
        a (dict): The dictionary where keys are mapped to sets or lists of keys.
        x (str): The first key to check.
        y (str): The second key to check.
    
    Returns:
        bool: True if both (x, y) or (y, x) are present in the dictionary 
              as described, False otherwise.
        
    This function determines if `x` is a key in the dictionary `a` and 
    its corresponding value contains `y`, or if `y` is a key and its 
    corresponding value contains `x`.
    """
    
    return x in a and y in a[x] or \
           y in a and x in a[y]


# Checks if overlap between two extensions is allowed
def extension_overlap_allowed(x, y):
    return overlap_allowed(overlapping_extensions, x, y)


# Checks if overlap between two instructions is allowed
def instruction_overlap_allowed(x, y):
    return overlap_allowed(overlapping_instructions, x, y)


# Checks if ext_name shares the same base ISA with any in ext_name_list
def same_base_isa(ext_name, ext_name_list):
    type1 = ext_name.split("_")[0]
    for ext_name1 in ext_name_list:
        type2 = ext_name1.split("_")[0]
        if type1 == type2 or \
           (type2 == "rv" and type1 in ["rv32", "rv64"]) or \
           (type1 == "rv" and type2 in ["rv32", "rv64"]):
            return True
    return False


# Expands instructions with "nf" field in variable_fields, otherwise returns unchanged
def add_segmented_vls_insn(instr_dict):
    updated_dict = {}
    for k, v in instr_dict.items():
        if "nf" in v['variable_fields']:
            updated_dict.update(expand_nf_field(k, v))
        else:
            updated_dict[k] = v
    return updated_dict


# Expands nf field in instruction name and updates instruction details
def expand_nf_field(name, single_dict):
    if "nf" not in single_dict['variable_fields']:
        logging.error(f"Cannot expand nf field for instruction {name}")
        raise SystemExit(1)

    single_dict['variable_fields'].remove("nf")  # Remove "nf" from variable fields
    single_dict['mask'] = hex(int(single_dict['mask'], 16) | (0b111 << 29))  # Update mask

    name_expand_index = name.find('e')
    expanded_instructions = []
    for nf in range(8):  # Expand nf for values 0 to 7
        new_single_dict = copy.deepcopy(single_dict)
        new_single_dict['match'] = hex(int(single_dict['match'], 16) | (nf << 29))
        new_single_dict['encoding'] = format(nf, '03b') + single_dict['encoding'][3:]
        new_name = name if nf == 0 else f"{name[:name_expand_index]}seg{nf+1}{name[name_expand_index:]}"
        expanded_instructions.append((new_name, new_single_dict))
    return expanded_instructions


# Extracts the extensions used in an instruction dictionary
def instr_dict_2_extensions(instr_dict):
    return list({item['extension'][0] for item in instr_dict.values()})


# Returns signed interpretation of a value within a given width
def signed(value, width):
    return value if 0 <= value < (1 << (width - 1)) else value - (1 << width)


def read_lines(file):
    """Reads lines from a file and returns non-blank, non-comment lines."""
    with open(file) as fp:
        lines = (line.rstrip() for line in fp)
        return [line for line in lines if line and not line.startswith("#")]

def process_standard_instructions(lines, instr_dict, file_name):
    """Processes standard instructions from the given lines and updates the instruction dictionary."""
    for line in lines:
        if '$import' in line or '$pseudo' in line:
            continue
        logging.debug(f'Processing line: {line}')
        name, single_dict = process_enc_line(line, file_name)
        ext_name = os.path.basename(file_name)

        if name in instr_dict:
            var = instr_dict[name]["extension"]
            if same_base_isa(ext_name, var):
                log_and_exit(f'Instruction {name} from {ext_name} is already added from {var} in same base ISA')
            elif instr_dict[name]['encoding'] != single_dict['encoding']:
                log_and_exit(f'Instruction {name} from {ext_name} has different encodings in different base ISAs')

            instr_dict[name]['extension'].extend(single_dict['extension'])
        else:
            for key, item in instr_dict.items():
                if overlaps(item['encoding'], single_dict['encoding']) and \
                   not extension_overlap_allowed(ext_name, item['extension'][0]) and \
                   not instruction_overlap_allowed(name, key) and \
                   same_base_isa(ext_name, item['extension']):
                    log_and_exit(f'Instruction {name} in extension {ext_name} overlaps with {key} in {item["extension"]}')

            instr_dict[name] = single_dict

def process_pseudo_instructions(lines, instr_dict, file_name, opcodes_dir, include_pseudo, include_pseudo_ops):
    """Processes pseudo instructions from the given lines and updates the instruction dictionary."""
    for line in lines:
        if '$pseudo' not in line:
            continue
        logging.debug(f'Processing pseudo line: {line}')
        ext, orig_inst, pseudo_inst, line_content = pseudo_regex.findall(line)[0]
        ext_file = find_extension_file(ext, opcodes_dir)

        validate_instruction_in_extension(orig_inst, ext_file, file_name, pseudo_inst)

        name, single_dict = process_enc_line(f'{pseudo_inst} {line_content}', file_name)
        if orig_inst.replace('.', '_') not in instr_dict or include_pseudo or name in include_pseudo_ops:
            if name not in instr_dict:
                instr_dict[name] = single_dict
                logging.debug(f'Including pseudo_op: {name}')
            else:
                if single_dict['match'] != instr_dict[name]['match']:
                    instr_dict[f'{name}_pseudo'] = single_dict
                elif single_dict['extension'] not in instr_dict[name]['extension']:
                    instr_dict[name]['extension'].extend(single_dict['extension'])

def process_imported_instructions(lines, instr_dict, file_name, opcodes_dir):
    """Processes imported instructions from the given lines and updates the instruction dictionary."""
    for line in lines:
        if '$import' not in line:
            continue
        logging.debug(f'Processing imported line: {line}')
        import_ext, reg_instr = imported_regex.findall(line)[0]
        ext_file = find_extension_file(import_ext, opcodes_dir)

        validate_instruction_in_extension(reg_instr, ext_file, file_name, line)

        for oline in open(ext_file):
            if re.findall(f'^\\s*{reg_instr}\\s+', oline):
                name, single_dict = process_enc_line(oline, file_name)
                if name in instr_dict:
                    if instr_dict[name]['encoding'] != single_dict['encoding']:
                        log_and_exit(f'Imported instruction {name} from {os.path.basename(file_name)} has different encodings')
                    instr_dict[name]['extension'].extend(single_dict['extension'])
                else:
                    instr_dict[name] = single_dict
                break

def find_extension_file(ext, opcodes_dir):
    """Finds the extension file path, considering the unratified directory if necessary."""
    ext_file = f'{opcodes_dir}/{ext}'
    if not os.path.exists(ext_file):
        ext_file = f'{opcodes_dir}/unratified/{ext}'
        if not os.path.exists(ext_file):
            log_and_exit(f'Extension {ext} not found.')
    return ext_file

def validate_instruction_in_extension(inst, ext_file, file_name, pseudo_inst):
    """Validates if the original instruction exists in the dependent extension."""
    found = False
    for oline in open(ext_file):
        if re.findall(f'^\\s*{inst}\\s+', oline):
            found = True
            break
    if not found:
        log_and_exit(f'Original instruction {inst} required by pseudo_op {pseudo_inst} in {file_name} not found in {ext_file}')

def create_inst_dict(file_filter, include_pseudo=False, include_pseudo_ops=[]):
    """Creates a dictionary of instructions based on the provided file filters."""
    
    '''
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
    '''
    opcodes_dir = os.path.dirname(os.path.realpath(__file__))
    instr_dict = {}

    file_names = [file for fil in file_filter for file in sorted(glob.glob(f'{opcodes_dir}/{fil}'), reverse=True)]
    
    logging.debug('Collecting standard instructions')
    for file_name in file_names:
        logging.debug(f'Parsing File: {file_name} for standard instructions')
        lines = read_lines(file_name)
        process_standard_instructions(lines, instr_dict, file_name)

    logging.debug('Collecting pseudo instructions')
    for file_name in file_names:
        logging.debug(f'Parsing File: {file_name} for pseudo instructions')
        lines = read_lines(file_name)
        process_pseudo_instructions(lines, instr_dict, file_name, opcodes_dir, include_pseudo, include_pseudo_ops)

    logging.debug('Collecting imported instructions')
    for file_name in file_names:
        logging.debug(f'Parsing File: {file_name} for imported instructions')
        lines = read_lines(file_name)
        process_imported_instructions(lines, instr_dict, file_name, opcodes_dir)

    return instr_dict