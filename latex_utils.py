#!/usr/bin/env python3
import logging
import pprint

from constants import *
from shared_utils import create_inst_dict

LOG_FORMAT = "%(levelname)s:: %(message)s"
LOG_LEVEL = logging.INFO

pretty_printer = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


def create_priv_instr_dataset():
    """Create dataset list for privileged instructions."""
    system_instr = ["_h", "_s", "_system", "_svinval", "64_h"]
    return [
        (system_instr, "Trap-Return Instructions", ["sret", "mret"], False),
        (system_instr, "Interrupt-Management Instructions", ["wfi"], False),
        (
            system_instr,
            "Supervisor Memory-Management Instructions",
            ["sfence_vma"],
            False,
        ),
        (
            system_instr,
            "Hypervisor Memory-Management Instructions",
            ["hfence_vvma", "hfence_gvma"],
            False,
        ),
        (
            system_instr,
            "Hypervisor Virtual-Machine Load and Store Instructions",
            [
                "hlv_b",
                "hlv_bu",
                "hlv_h",
                "hlv_hu",
                "hlv_w",
                "hlvx_hu",
                "hlvx_wu",
                "hsv_b",
                "hsv_h",
                "hsv_w",
            ],
            False,
        ),
        (
            system_instr,
            "Hypervisor Virtual-Machine Load and Store Instructions, RV64 only",
            ["hlv_wu", "hlv_d", "hsv_d"],
            False,
        ),
        (
            system_instr,
            "Svinval Memory-Management Instructions",
            [
                "sinval_vma",
                "sfence_w_inval",
                "sfence_inval_ir",
                "hinval_vvma",
                "hinval_gvma",
            ],
            False,
        ),
    ]


def make_priv_latex_table():
    """Generate and write the LaTeX table for privileged instructions."""
    type_list = ["R-type", "I-type"]
    dataset_list = create_priv_instr_dataset()
    caption = "\\caption{RISC-V Privileged Instructions}"

    with open("priv-instr-table.tex", "w") as latex_file:
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)


def make_latex_table():
    """
    - This function is mean to create the instr-table.tex that is meant to be used
    by the riscv-isa-manual.
        1. creates a single latex file of multiple table
        2. Each table limited to a single page
        3. Only the last table is assigned a latex-caption.

    - For each table, we assign a type-list that captures the different instruction types (R, I, B, etc.) required for that table.
        1. Specify the type-list to capture various instruction types (e.g., R-type, I-type, B-type).
        2. Select a list of extensions (e.g., _i, 32_i) whose instructions are necessary to populate the table.
        3. For each extension or collection of extensions, assign a title that appears as a subheading within the table (these are inlined headings, not captions).

    * All of the above information is collected/created and sent to
    make_ext_latex_table function to dump out the latex contents into a file.

    * The last table only has to be given a caption - as per the policy of the
    riscv-isa-manual.
    """
    # File for writing LaTeX content
    with open("instr-table.tex", "w") as latex_file:
        # Prepare table configurations with type list, datasets, word size & caption
        table_configurations = get_table_configurations()

        # Map each configuration from above with variables to pass as argumnet
        for config in table_configurations:
            # Unpack configuration dictionary into arguments for make_ext_latex_table
            type_list = config["type_list"]
            datasets = config["datasets"]
            word_size = config["word_size"]
            caption = config["caption"]

            # LaTeX table generation function
            make_ext_latex_table(type_list, datasets, latex_file, word_size, caption)


def get_table_configurations():
    """
    Returns a list of table configurations, each specifying the type list, datasets,
    word size, and caption for LaTeX table generation.

    Returns:
        list: A list of dictionaries, each representing a table's configuration.
    """
    return [
        create_table_configuration(
            type_list=["R-type", "I-type", "S-type", "B-type", "U-type", "J-type"],
            datasets=[
                create_dataset(["_i", "32_i"], "RV32I Base Instruction Set", [], False),
                create_dataset(["_i"], "", ["fence_tso", "pause"], True),
            ],
            word_size=32,
        ),
        create_table_configuration(
            type_list=["R-type", "I-type", "S-type"],
            datasets=[
                create_dataset(
                    ["64_i"],
                    "RV64I Base Instruction Set (in addition to RV32I)",
                    [],
                    False,
                ),
                create_dataset(
                    ["_zifencei"], "RV32/RV64 Zifencei Standard Extension", [], False
                ),
                create_dataset(
                    ["_zicsr"], "RV32/RV64 Zicsr Standard Extension", [], False
                ),
                create_dataset(["_m", "32_m"], "RV32M Standard Extension", [], False),
                create_dataset(
                    ["64_m"],
                    "RV64M Standard Extension (in addition to RV32M)",
                    [],
                    False,
                ),
            ],
            word_size=32,
        ),
        create_table_configuration(
            type_list=["R-type"],
            datasets=[
                create_dataset(["_a"], "RV32A Standard Extension", [], False),
                create_dataset(
                    ["64_a"],
                    "RV64A Standard Extension (in addition to RV32A)",
                    [],
                    False,
                ),
            ],
            word_size=32,
        ),
        create_table_configuration(
            type_list=["R-type", "R4-type", "I-type", "S-type"],
            datasets=[
                create_dataset(["_f"], "RV32F Standard Extension", [], False),
                create_dataset(
                    ["64_f"],
                    "RV64F Standard Extension (in addition to RV32F)",
                    [],
                    False,
                ),
            ],
            word_size=32,
        ),
        create_table_configuration(
            type_list=["R-type", "R4-type", "I-type", "S-type"],
            datasets=[
                create_dataset(["_d"], "RV32D Standard Extension", [], False),
                create_dataset(
                    ["64_d"],
                    "RV64D Standard Extension (in addition to RV32D)",
                    [],
                    False,
                ),
            ],
            word_size=32,
        ),
        create_table_configuration(
            type_list=["R-type", "R4-type", "I-type", "S-type"],
            datasets=[
                create_dataset(["_q"], "RV32Q Standard Extension", [], False),
                create_dataset(
                    ["64_q"],
                    "RV64Q Standard Extension (in addition to RV32Q)",
                    [],
                    False,
                ),
            ],
            word_size=32,
        ),
        create_table_configuration(
            type_list=["R-type", "R4-type", "I-type", "S-type"],
            datasets=[
                create_dataset(
                    ["_zfh", "_d_zfh", "_q_zfh"],
                    "RV32Zfh Standard Extension",
                    [],
                    False,
                ),
                create_dataset(
                    ["64_zfh"],
                    "RV64Zfh Standard Extension (in addition to RV32Zfh)",
                    [],
                    False,
                ),
            ],
            word_size=32,
            caption="\\caption{Instruction listing for RISC-V}",
        ),
        create_table_configuration(
            type_list=[""],
            datasets=[
                create_dataset(
                    ["_c", "32_c", "32_c_f", "_c_d"],
                    "RV32C Standard Extension",
                    [],
                    False,
                ),
                create_dataset(
                    ["64_c"],
                    "RV64C Standard Extension (in addition to RV32C)",
                    [],
                    False,
                ),
            ],
            word_size=16,
            caption="",
        ),
    ]


def create_table_configuration(type_list, datasets, word_size, caption=""):
    """
    Creates a table configuration dictionary with the provided parameters.

    Parameters:
        type_list (list): List of instruction types to include in the table.
        datasets (list of tuples): Each tuple contains:
            - list_of_extensions (list): List of extension names.
            - title (str): Title to appear as a subsection in the table.
            - list_of_instructions (list): Specific instructions to include.
            - include_pseudo_ops (bool): Whether to include pseudo-operations.
        word_size (int): The word size for the instructions (32 or 16).
        caption (str): The caption to include at the end of the table.

    Returns:
        dict: A dictionary representing the table configuration.
    """
    return {
        "type_list": type_list,
        "datasets": datasets,
        "word_size": word_size,
        "caption": caption,
    }


def create_dataset(extensions, title, instructions, include_pseudo_ops):
    """
    Creates a dataset tuple for table configuration.

    Parameters:
        extensions (list): List of extension names.
        title (str): Title for the dataset.
        instructions (list): List of specific instructions to include.
        include_pseudo_ops (bool): Whether to include pseudo-operations.

    Returns:
        tuple: A tuple representing the dataset configuration.
    """
    return (extensions, title, instructions, include_pseudo_ops)


def make_ext_latex_table(type_list, dataset, latex_file, ilen, caption):
    """
    For a given collection of extensions this function dumps out a complete
    latex table which includes the encodings of the instructions.

    Args:
    - type_list (list of str):
        1. A list of instruction types (R, I, B, etc) that are treated as header for each table.
        2. Each table will have its own requirements and type_list must include all the instruction-types that the table needs.
        3. All elements of this list must be present in the latex_inst_type dictionary defined in constants.py


    - dataset (list of tuples): A list of 3-element tuples where each tuple consists of:
        1. list_of_extensions (list): A list of extensions whose instructions will be populated under the respective title.
        2. title (str): A title associated with the respective table.
        3. list_of_instructions (list): If not empty, only these instructions present in the corresponding extension
          will be included in the table, while others will be ignored.

    - latex_file (file pointer): A file pointer to the LaTeX file where the generated table will be written.

    - ilen (int): The ilen input indicates the length of the instruction for which the table is created.

    - caption (str): The caption for the LaTeX table.

    Returns:
    - None: The function writes the generated LaTeX table directly to the provided `latex_file`.

    Process:
    1. Creates table headers based on the instruction types in `type_list` using the `latex_inst_type` dictionary
       from constants.py.

    2. Iterates through each entry in the dataset to:
       - Generate an exhaustive list of instructions for each dataset using `create_inst_dict`.
       - Apply any instruction filters based on `list_of_instructions` to select only relevant instructions.

    3. For each instruction, generates LaTeX table entries.
       - Uses `arg_lut` from constants.py to determine the position of arguments in the encoding, and creates multicolumn
         LaTeX entries for these arguments.
       - Handles hardcoded bits (e.g., strings of 1s and 0s) similarly, creating multicolumn entries for continuous
         strings of bits.

    4. Writes the LaTeX table to `latex_file` with a specific format suitable for instructions of size `ilen`.
    """

    column_size = get_column_size(ilen)
    type_entries = generate_type_entries(ilen)
    type_dict = get_type_dict(type_list)

    # Build the table entry with each instruction types
    for inst_type, fields in type_dict.items():
        type_entries += build_instruction_type_entry(inst_type, fields, ilen)

    # Create a table for each dataset entry
    content = generate_dataset_content(dataset, ilen)

    header = generate_table_header(column_size, ilen, type_entries)
    endtable = generate_table_footer(caption)

    # Dump the contents to the latex file
    latex_file.write(header + content + endtable)


def get_column_size(ilen):
    """Generate the column size string based on instruction length (ilen)."""
    return "".join(["p{0.002in}"] * (ilen + 1))


def generate_type_entries(ilen):
    """Generate the type entries section of the LaTeX table."""
    if ilen == 32:
        return """
            \\multicolumn{3}{l}{31} &
            \\multicolumn{2}{r}{27} &
            \\multicolumn{1}{c}{26} &
            \\multicolumn{1}{r}{25} &
            \\multicolumn{3}{l}{24} &
            \\multicolumn{2}{r}{20} &
            \\multicolumn{3}{l}{19} &
            \\multicolumn{2}{r}{15} &
            \\multicolumn{2}{l}{14} &
            \\multicolumn{1}{r}{12} &
            \\multicolumn{4}{l}{11} &
            \\multicolumn{1}{r}{7} &
            \\multicolumn{6}{l}{6} &
            \\multicolumn{1}{r}{0} \\\\
            \\cline{2-33}\n&\n\n"""
    else:
        return """
            \\multicolumn{1}{c}{15} &
            \\multicolumn{1}{c}{14} &
            \\multicolumn{1}{c}{13} &
            \\multicolumn{1}{c}{12} &
            \\multicolumn{1}{c}{11} &
            \\multicolumn{1}{c}{10} &
            \\multicolumn{1}{c}{9} &
            \\multicolumn{1}{c}{8} &
            \\multicolumn{1}{c}{7} &
            \\multicolumn{1}{c}{6} &
            \\multicolumn{1}{c}{5} &
            \\multicolumn{1}{c}{4} &
            \\multicolumn{1}{c}{3} &
            \\multicolumn{1}{c}{2} &
            \\multicolumn{1}{c}{1} &
            \\multicolumn{1}{c}{0} \\\\
            \\cline{2-17}\n&\n\n"""


def get_type_dict(type_list):
    """Create a subset dictionary of latex_inst_type for the given type_list."""
    return {key: value for key, value in latex_inst_type.items() if key in type_list}


def build_instruction_type_entry(inst_type, fields, ilen):
    """Build a LaTeX table entry for each instruction type."""
    entries = []
    for field in fields["variable_fields"]:
        (msb, lsb) = arg_lut[field]
        name = latex_mapping.get(field, field)
        entries.append((msb, lsb, name))

    return format_table_entry(entries, inst_type, ilen)


def format_table_entry(fields, entry_type, ilen):
    """Generate formatted LaTeX table entry."""
    fields.sort(key=lambda f: f[0], reverse=True)
    entry = ""
    for i, (msb, lsb, name) in enumerate(fields):
        col_size = msb - lsb + 1
        if i == len(fields) - 1:
            entry += (
                f"\\multicolumn{{{col_size}}}{{|c|}}{{{name}}} & {entry_type} \\\\\n"
            )
        elif i == 0:
            entry += f"\\multicolumn{{{col_size}}}{{|c|}}{{{name}}} &\n"
        else:
            entry += f"\\multicolumn{{{col_size}}}{{c|}}{{{name}}} &\n"
    return entry + f"\\cline{{2-{ilen+1}}}\n&\n\n"


def generate_dataset_content(dataset, ilen):
    """Generate LaTeX content for each dataset entry."""
    content = ""
    for ext_list, title, filter_list, include_pseudo in dataset:
        instr_dict = get_instruction_dict(ext_list, include_pseudo)
        filtered_list = filter_list if filter_list else list(instr_dict.keys())
        instr_entries = generate_instruction_entries(instr_dict, filtered_list, ilen)

        if title:
            content += generate_dataset_title(title, ilen) + instr_entries
        else:
            content += instr_entries
    return content


def get_instruction_dict(ext_list, include_pseudo):
    """Create a dictionary of instructions for given extensions."""
    instr_dict = {}
    for ext in ext_list:
        instr_dict.update(create_inst_dict([f"rv{ext}"], include_pseudo))
    return instr_dict


def generate_instruction_entries(instr_dict, inst_list, ilen):
    """Generate LaTeX entries for each instruction in the list."""
    instr_entries = ""
    for inst in inst_list:
        if inst not in instr_dict:
            logging.error(f"Instruction {inst} not found in instr_dict")
            raise SystemExit(1)

        fields = parse_instruction_fields(instr_dict[inst], ilen)
        instr_entries += format_table_entry(
            fields, inst.upper().replace("_", "."), ilen
        )

    return instr_entries


def parse_instruction_fields(inst_data, ilen):
    """Parse and extract fields from instruction data."""
    fields = []
    encoding = inst_data["encoding"][16:] if ilen == 16 else inst_data["encoding"]
    msb = ilen - 1
    y = ""

    for i in range(ilen):
        x = encoding[i]
        if x == "-":
            if y:
                fields.append((msb, ilen - i, y))
                y = ""
            msb -= 1
        else:
            y += str(x)

        if i == ilen - 1 and y:
            fields.append((msb, 0, y))

    fields.sort(key=lambda f: f[0], reverse=True)
    return fields


def generate_dataset_title(title, ilen):
    """Generate LaTeX dataset title."""
    return f"""
\\multicolumn{{{ilen}}}{{c}}{{}} & \\\\
\\multicolumn{{{ilen}}}{{c}}{{\\bf {title} }} & \\\\
\\cline{{2-{ilen + 1}}}
"""


def generate_table_header(column_size, ilen, type_entries):
    """Generate LaTeX table header."""
    return f"""
\\newpage

\\begin{{table}}[p]
\\begin{{small}}
\\begin{{center}}
    \\begin{{tabular}} {{{column_size}l}}
    {" ".join(['&'] * ilen)} \\\\

            &
{type_entries}
"""


def generate_table_footer(caption):
    """Generate LaTeX table footer."""
    return f"""

\\end{{tabular}}
\\end{{center}}
\\end{{small}}
{caption}
\\end{{table}}
"""
