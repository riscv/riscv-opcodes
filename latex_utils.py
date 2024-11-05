import logging
import pprint
from typing import TextIO

from constants import latex_fixed_fields, latex_inst_type, latex_mapping
from shared_utils import InstrDict, arg_lut, create_inst_dict

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")


def make_priv_latex_table():
    type_list = ["R-type", "I-type"]
    system_instr = ["_h", "_s", "_system", "_svinval", "64_h", "_svinval_h"]
    dataset_list = [(system_instr, "Trap-Return Instructions", ["sret", "mret"], False)]
    dataset_list.append(
        (system_instr, "Interrupt-Management Instructions", ["wfi"], False)
    )
    dataset_list.append(
        (
            system_instr,
            "Supervisor Memory-Management Instructions",
            ["sfence_vma"],
            False,
        )
    )
    dataset_list.append(
        (
            system_instr,
            "Hypervisor Memory-Management Instructions",
            ["hfence_vvma", "hfence_gvma"],
            False,
        )
    )
    dataset_list.append(
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
        )
    )
    dataset_list.append(
        (
            system_instr,
            "Hypervisor Virtual-Machine Load and Store Instructions, RV64 only",
            ["hlv_wu", "hlv_d", "hsv_d"],
            False,
        )
    )
    dataset_list.append(
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
        )
    )
    caption = "\\caption{RISC-V Privileged Instructions}"
    with open("priv-instr-table.tex", "w", encoding="utf-8") as latex_file:
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)


def make_latex_table():
    """
    This function is mean to create the instr-table.tex that is meant to be used
    by the riscv-isa-manual. This function basically creates a single latext
    file of multiple tables with each table limited to a single page. Only the
    last table is assigned a latex-caption.

    For each table we assign a type-list which capture the different instruction
    types (R, I, B, etc) that will be required for the table. Then we select the
    list of extensions ('_i, '32_i', etc) whose instructions are required to
    populate the table. For each extension or collection of extension we can
    assign Title, such that in the end they appear as subheadings within
    the table (note these are inlined headings and not captions of the table).

    All of the above information is collected/created and sent to
    make_ext_latex_table function to dump out the latex contents into a file.

    The last table only has to be given a caption - as per the policy of the
    riscv-isa-manual.
    """
    # open the file and use it as a pointer for all further dumps
    with open("instr-table.tex", "w", encoding="utf-8") as latex_file:

        # create the rv32i table first. Here we set the caption to empty. We use the
        # files rv_i and rv32_i to capture instructions relevant for rv32i
        # configuration. The dataset is a list of 4-element tuples :
        # (list_of_extensions, title, list_of_instructions, include_pseudo_ops). If list_of_instructions
        # is empty then it indicates that all instructions of the all the extensions
        # in list_of_extensions need to be dumped. If not empty, then only the
        # instructions listed in list_of_instructions will be dumped into latex.
        caption = ""
        type_list = ["R-type", "I-type", "S-type", "B-type", "U-type", "J-type"]
        dataset_list: list[tuple[list[str], str, list[str], bool]] = [
            (["_i", "32_i"], "RV32I Base Instruction Set", [], False)
        ]
        dataset_list.append((["_i"], "", ["fence_tso", "pause"], True))
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        type_list = ["R-type", "I-type", "S-type"]
        dataset_list = [
            (["64_i"], "RV64I Base Instruction Set (in addition to RV32I)", [], False)
        ]
        dataset_list.append(
            (["_zifencei"], "RV32/RV64 Zifencei Standard Extension", [], False)
        )
        dataset_list.append(
            (["_zicsr"], "RV32/RV64 Zicsr Standard Extension", [], False)
        )
        dataset_list.append((["_m", "32_m"], "RV32M Standard Extension", [], False))
        dataset_list.append(
            (["64_m"], "RV64M Standard Extension (in addition to RV32M)", [], False)
        )
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        type_list = ["R-type"]
        dataset_list = [(["_a"], "RV32A Standard Extension", [], False)]
        dataset_list.append(
            (["64_a"], "RV64A Standard Extension (in addition to RV32A)", [], False)
        )
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        type_list = ["R-type", "R4-type", "I-type", "S-type"]
        dataset_list = [(["_f"], "RV32F Standard Extension", [], False)]
        dataset_list.append(
            (["64_f"], "RV64F Standard Extension (in addition to RV32F)", [], False)
        )
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        type_list = ["R-type", "R4-type", "I-type", "S-type"]
        dataset_list = [(["_d"], "RV32D Standard Extension", [], False)]
        dataset_list.append(
            (["64_d"], "RV64D Standard Extension (in addition to RV32D)", [], False)
        )
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        type_list = ["R-type", "R4-type", "I-type", "S-type"]
        dataset_list = [(["_q"], "RV32Q Standard Extension", [], False)]
        dataset_list.append(
            (["64_q"], "RV64Q Standard Extension (in addition to RV32Q)", [], False)
        )
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        caption = "\\caption{Instruction listing for RISC-V}"
        type_list = ["R-type", "R4-type", "I-type", "S-type"]
        dataset_list = [
            (["_zfh", "_d_zfh", "_q_zfh"], "RV32Zfh Standard Extension", [], False)
        ]
        dataset_list.append(
            (
                ["64_zfh"],
                "RV64Zfh Standard Extension (in addition to RV32Zfh)",
                [],
                False,
            )
        )
        make_ext_latex_table(type_list, dataset_list, latex_file, 32, caption)

        ## The following is demo to show that Compressed instructions can also be
        # dumped in the same manner as above

        # type_list = ['']
        # dataset_list = [(['_c', '32_c', '32_c_f','_c_d'],'RV32C Standard Extension', [])]
        # dataset_list.append((['64_c'],'RV64C Standard Extension (in addition to RV32C)', []))
        # make_ext_latex_table(type_list, dataset_list, latex_file, 16, caption)


def make_ext_latex_table(
    type_list: "list[str]",
    dataset: "list[tuple[list[str], str, list[str], bool]]",
    latex_file: TextIO,
    ilen: int,
    caption: str,
):
    """
    For a given collection of extensions this function dumps out a complete
    latex table which includes the encodings of the instructions.

    The ilen input indicates the length of the instruction for which the table
    is created.

    The caption input is used to create the latex-table caption.

    The type_list input is a list of instruction types (R, I, B, etc) that are
    treated as header for each table. Each table will have its own requirements
    and type_list must include all the instruction-types that the table needs.
    Note, all elements of this list must be present in the latex_inst_type
    dictionary defined in constants.py

    The latex_file is a file pointer to which the latex-table will dumped into

    The dataset is a list of 3-element tuples containing:
        (list_of_extensions, title, list_of_instructions)
    The list_of_extensions must contain all the set of extensions whose
    instructions must be populated under a given title. If list_of_instructions
    is not empty, then only those instructions mentioned in list_of_instructions
    present in the extension will be dumped into the latex-table, other
    instructions will be ignored.

    Once the above inputs are received then function first creates table entries
    for the instruction types. To simplify things, we maintain a dictionary
    called latex_inst_type in constants.py which is created in the same way the
    instruction dictionary is created. This allows us to re-use the same logic
    to create the instruction types table as well

    Once the header is created, we then parse through every entry in the
    dataset. For each list dataset entry we use the create_inst_dict function to
    create an exhaustive list of instructions associated with the respective
    collection of the extension of that dataset. Then we apply the instruction
    filter, if any, indicated by the list_of_instructions of that dataset.
    Thereon, for each instruction we create a latex table entry.

    Latex table specification for ilen sized instructions:
        Each table is created with ilen+1 columns - ilen columns for each bit of the
        instruction and one column to hold the name of the instruction.

        For each argument of an instruction we use the arg_lut from constants.py
        to identify its position in the encoding, and thus create a multicolumn
        entry with the name of the argument as the data. For hardcoded bits, we
        do the same where we capture a string of continuous 1s and 0s, identify
        the position and assign the same string as the data of the
        multicolumn entry in the table.

    """
    column_size = "".join(["p{0.002in}"] * (ilen + 1))

    type_entries = (
        """
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
    \\cline{2-33}\n&\n\n
"""
        if ilen == 32
        else """
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
    \\cline{2-17}\n&\n\n
"""
    )

    # depending on the type_list input we create a subset dictionary of
    # latex_inst_type dictionary present in constants.py
    type_dict = {
        key: value for key, value in latex_inst_type.items() if key in type_list
    }

    # iterate ovr each instruction type and create a table entry
    for t in type_dict:
        fields: list[tuple[int, int, str]] = []

        # first capture all "arguments" of the type (funct3, funct7, rd, etc)
        # and capture their positions using arg_lut.
        for f in type_dict[t]["variable_fields"]:
            (msb, lsb) = arg_lut[f]
            name = f if f not in latex_mapping else latex_mapping[f]
            fields.append((msb, lsb, name))

        # iterate through the 32 bits, starting from the msb, and assign
        # argument names to the relevant portions of the instructions. This
        # information is stored as a 3-element tuple containing the msb, lsb
        # position of the arugment and the name of the argument.
        msb = ilen - 1
        y = ""
        for r in range(0, ilen):
            if y != "":
                fields.append((msb, ilen - 1 - r + 1, y))
                y = ""
            msb = ilen - 1 - r - 1
            if r == 31:
                if y != "":
                    fields.append((msb, 0, y))
                y = ""

        # sort the arguments in decreasing order of msb position
        fields.sort(key=lambda y: y[0], reverse=True)

        # for each argument/string of 1s or 0s, create a multicolumn latex table
        # entry
        entry = ""
        for r, (msb, lsb, name) in enumerate(fields):
            if r == len(fields) - 1:
                entry += (
                    f"\\multicolumn{{{msb - lsb + 1}}}{{|c|}}{{{name}}} & {t} \\\\\n"
                )
            elif r == 0:
                entry += f"\\multicolumn{{{msb - lsb + 1}}}{{|c|}}{{{name}}} &\n"
            else:
                entry += f"\\multicolumn{{{msb - lsb + 1}}}{{c|}}{{{name}}} &\n"
        entry += f"\\cline{{2-{ilen+1}}}\n&\n\n"
        type_entries += entry

    # for each entry in the dataset create a table
    content = ""
    for ext_list, title, filter_list, include_pseudo in dataset:
        instr_dict: InstrDict = {}

        # for all extensions list in ext_list, create a dictionary of
        # instructions associated with those extensions.
        for e in ext_list:
            instr_dict.update(create_inst_dict(["rv" + e], include_pseudo))

        # if filter_list is not empty then use that as the official set of
        # instructions that need to be dumped into the latex table
        inst_list = list(instr_dict.keys()) if not filter_list else filter_list

        # for each instruction create an latex table entry just like how we did
        # above with the instruction-type table.
        instr_entries = ""
        for inst in inst_list:
            if inst not in instr_dict:
                logging.error(
                    f"in make_ext_latex_table: Instruction: {inst} not found in instr_dict"
                )
                raise SystemExit(1)
            fields = []

            # only if the argument is available in arg_lut we consume it, else
            # throw error.
            for f in instr_dict[inst]["variable_fields"]:
                if f not in arg_lut:
                    logging.error(
                        f"Found variable {f} in instruction {inst} whose mapping is not available"
                    )
                    raise SystemExit(1)
                (msb, lsb) = arg_lut[f]
                name = (
                    f.replace("_", ".") if f not in latex_mapping else latex_mapping[f]
                )
                fields.append((msb, lsb, name))

            msb = ilen - 1
            y = ""
            if ilen == 16:
                encoding = instr_dict[inst]["encoding"][16:]
            else:
                encoding = instr_dict[inst]["encoding"]
            for r in range(0, ilen):
                x = encoding[r]
                if (msb, ilen - 1 - r + 1) in latex_fixed_fields:
                    fields.append((msb, ilen - 1 - r + 1, y))
                    msb = ilen - 1 - r
                    y = ""
                if x == "-":
                    if y != "":
                        fields.append((msb, ilen - 1 - r + 1, y))
                        y = ""
                    msb = ilen - 1 - r - 1
                else:
                    y += str(x)
                if r == ilen - 1:
                    if y != "":
                        fields.append((msb, 0, y))
                    y = ""

            fields.sort(key=lambda y: y[0], reverse=True)
            entry = ""
            for r, (msb, lsb, name) in enumerate(fields):
                if r == len(fields) - 1:
                    entry += f'\\multicolumn{{{msb - lsb + 1}}}{{|c|}}{{{name}}} & {inst.upper().replace("_",".")} \\\\\n'
                elif r == 0:
                    entry += f"\\multicolumn{{{msb - lsb + 1}}}{{|c|}}{{{name}}} &\n"
                else:
                    entry += f"\\multicolumn{{{msb - lsb + 1}}}{{c|}}{{{name}}} &\n"
            entry += f"\\cline{{2-{ilen+1}}}\n&\n\n"
            instr_entries += entry

        # once an entry of the dataset is completed we create the whole table
        # with the title of that dataset as sub-heading (sort-of)
        if title != "":
            content += f"""

\\multicolumn{{{ilen}}}{{c}}{{}} & \\\\
\\multicolumn{{{ilen}}}{{c}}{{\\bf {title} }} & \\\\
\\cline{{2-{ilen+1}}}

            &
{instr_entries}
"""
        else:
            content += f"""
{instr_entries}
"""

    header = f"""
\\newpage

\\begin{{table}}[p]
\\begin{{small}}
\\begin{{center}}
    \\begin{{tabular}} {{{column_size}l}}
    {" ".join(['&']*ilen)} \\\\

            &
{type_entries}
"""
    endtable = f"""

\\end{{tabular}}
\\end{{center}}
\\end{{small}}
{caption}
\\end{{table}}
"""
    # dump the contents and return
    latex_file.write(header + content + endtable)
