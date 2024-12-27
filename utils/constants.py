import csv
import re

# TODO: The constants in this file should be in all caps.
overlapping_extensions = {
    "rv_zcmt": {"rv_c_d"},
    "rv_zcmp": {"rv_c_d"},
    "rv_c": {"rv_zcmop"},
}

overlapping_instructions = {
    "c_addi": {"c_nop"},
    "c_lui": {"c_addi16sp"},
    "c_mv": {"c_jr"},
    "c_jalr": {"c_ebreak"},
    "c_add": {"c_ebreak", "c_jalr"},
}

isa_regex = re.compile(
    "^RV(32|64|128)[IE]+[ABCDEFGHJKLMNPQSTUVX]*(Zicsr|Zifencei|Zihintpause|Zam|Ztso|Zkne|Zknd|Zknh|Zkse|Zksh|Zkg|Zkb|Zkr|Zks|Zkn|Zba|Zbc|Zbb|Zbp|Zbr|Zbm|Zbs|Zbe|Zbf|Zbt|Zmmul|Zbpbo|Zca|Zcf|Zcd|Zcb|Zcmp|Zcmt){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zmmul){,1}(_Zam){,1}(_Zba){,1}(_Zbb){,1}(_Zbc){,1}(_Zbe){,1}(_Zbf){,1}(_Zbm){,1}(_Zbp){,1}(_Zbpbo){,1}(_Zbr){,1}(_Zbs){,1}(_Zbt){,1}(_Zkb){,1}(_Zkg){,1}(_Zkr){,1}(_Zks){,1}(_Zkn){,1}(_Zknd){,1}(_Zkne){,1}(_Zknh){,1}(_Zkse){,1}(_Zksh){,1}(_Ztso){,1}(_Zca){,1}(_Zcf){,1}(_Zcd){,1}(_Zcb){,1}(_Zcmp){,1}(_Zcmt){,1}$"
)

# regex to find <msb>..<lsb>=<val> patterns in instruction
fixed_ranges = re.compile(
    r"\s*(?P<msb>\d+.?)\.\.(?P<lsb>\d+.?)\s*=\s*(?P<val>\d[\w]*)[\s$]*", re.M
)

# regex to find <lsb>=<val> patterns in instructions
# single_fixed = re.compile('\s+(?P<lsb>\d+)=(?P<value>[\w\d]*)[\s$]*', re.M)
single_fixed = re.compile(r"(?:^|[\s])(?P<lsb>\d+)=(?P<value>[\w]*)((?=\s|$))", re.M)

# regex to find the overloading condition variable
var_regex = re.compile(r"(?P<var>[a-zA-Z][\w\d]*)\s*=\s*.*?[\s$]*", re.M)

# regex for pseudo op instructions returns the dependent filename, dependent
# instruction, the pseudo op name and the encoding string
pseudo_regex = re.compile(
    r"^\$pseudo_op\s+(?P<filename>rv[\d]*_[\w].*)::\s*(?P<orig_inst>.*?)\s+(?P<pseudo_inst>.*?)\s+(?P<overload>.*)$",
    re.M,
)

imported_regex = re.compile(
    r"^\s*\$import\s*(?P<extension>.*)\s*::\s*(?P<instruction>.*)", re.M
)


def read_int_map_csv(filename: str) -> "list[tuple[int, str]]":
    """
    Reads a CSV file and returns a list of tuples.
    Each tuple contains an integer value (from the first column) and a string (from the second column).

    Args:
        filename (str): The name of the CSV file to read.

    Returns:
        list of tuple: A list of (int, str) tuples extracted from the CSV file.
    """
    with open(filename, encoding="utf-8") as f:
        csv_reader = csv.reader(f, skipinitialspace=True)
        return [(int(row[0], 0), row[1]) for row in csv_reader]


causes = read_int_map_csv("causes.csv")
csrs = read_int_map_csv("csrs.csv")
csrs32 = read_int_map_csv("csrs32.csv")


def read_arg_lut_csv(filename: str) -> "dict[str, tuple[int, int]]":
    """
    Load the argument lookup table (arg_lut) from a CSV file, mapping argument names to their bit positions.
    """
    with open(filename, encoding="utf-8") as f:
        csv_reader = csv.reader(f, skipinitialspace=True)
        return {row[0]: (int(row[1]), int(row[2])) for row in csv_reader}


arg_lut = read_arg_lut_csv("arg_lut.csv")

# for mop
arg_lut["mop_r_t_30"] = (30, 30)
arg_lut["mop_r_t_27_26"] = (27, 26)
arg_lut["mop_r_t_21_20"] = (21, 20)
arg_lut["mop_rr_t_30"] = (30, 30)
arg_lut["mop_rr_t_27_26"] = (27, 26)
arg_lut["c_mop_t"] = (10, 8)

# dictionary containing the mapping of the argument to the what the fields in
# the latex table should be
latex_mapping = {
    "imm12": "imm[11:0]",
    "rs1": "rs1",
    "rs2": "rs2",
    "rd": "rd",
    "imm20": "imm[31:12]",
    "bimm12hi": "imm[12$\\vert$10:5]",
    "bimm12lo": "imm[4:1$\\vert$11]",
    "imm12hi": "imm[11:5]",
    "imm12lo": "imm[4:0]",
    "jimm20": "imm[20$\\vert$10:1$\\vert$11$\\vert$19:12]",
    "zimm": "uimm",
    "shamtw": "shamt",
    "shamtd": "shamt",
    "shamtq": "shamt",
    "rd_p": "rd\\,$'$",
    "rs1_p": "rs1\\,$'$",
    "rs2_p": "rs2\\,$'$",
    "rd_rs1_n0": "rd/rs$\\neq$0",
    "rd_rs1_p": "rs1\\,$'$/rs2\\,$'$",
    "c_rs2": "rs2",
    "c_rs2_n0": "rs2$\\neq$0",
    "rd_n0": "rd$\\neq$0",
    "rs1_n0": "rs1$\\neq$0",
    "c_rs1_n0": "rs1$\\neq$0",
    "rd_rs1": "rd/rs1",
    "zimm6hi": "uimm[5]",
    "zimm6lo": "uimm[4:0]",
    "c_nzuimm10": "nzuimm[5:4$\\vert$9:6$\\vert$2$\\vert$3]",
    "c_uimm7lo": "uimm[2$\\vert$6]",
    "c_uimm7hi": "uimm[5:3]",
    "c_uimm8lo": "uimm[7:6]",
    "c_uimm8hi": "uimm[5:3]",
    "c_uimm9lo": "uimm[7:6]",
    "c_uimm9hi": "uimm[5:4$\\vert$8]",
    "c_nzimm6lo": "nzimm[4:0]",
    "c_nzimm6hi": "nzimm[5]",
    "c_imm6lo": "imm[4:0]",
    "c_imm6hi": "imm[5]",
    "c_nzimm10hi": "nzimm[9]",
    "c_nzimm10lo": "nzimm[4$\\vert$6$\\vert$8:7$\\vert$5]",
    "c_nzimm18hi": "nzimm[17]",
    "c_nzimm18lo": "nzimm[16:12]",
    "c_imm12": "imm[11$\\vert$4$\\vert$9:8$\\vert$10$\\vert$6$\\vert$7$\\vert$3:1$\\vert$5]",
    "c_bimm9lo": "imm[7:6$\\vert$2:1$\\vert$5]",
    "c_bimm9hi": "imm[8$\\vert$4:3]",
    "c_nzuimm5": "nzuimm[4:0]",
    "c_nzuimm6lo": "nzuimm[4:0]",
    "c_nzuimm6hi": "nzuimm[5]",
    "c_uimm8splo": "uimm[4:2$\\vert$7:6]",
    "c_uimm8sphi": "uimm[5]",
    "c_uimm8sp_s": "uimm[5:2$\\vert$7:6]",
    "c_uimm10splo": "uimm[4$\\vert$9:6]",
    "c_uimm10sphi": "uimm[5]",
    "c_uimm9splo": "uimm[4:3$\\vert$8:6]",
    "c_uimm9sphi": "uimm[5]",
    "c_uimm10sp_s": "uimm[5:4$\\vert$9:6]",
    "c_uimm9sp_s": "uimm[5:3$\\vert$8:6]",
}

# created a dummy instruction-dictionary like dictionary for all the instruction
# types so that the same logic can be used to create their tables
latex_inst_type = {
    "R-type": {
        "variable_fields": ["opcode", "rd", "funct3", "rs1", "rs2", "funct7"],
    },
    "R4-type": {
        "variable_fields": ["opcode", "rd", "funct3", "rs1", "rs2", "funct2", "rs3"],
    },
    "I-type": {
        "variable_fields": ["opcode", "rd", "funct3", "rs1", "imm12"],
    },
    "S-type": {
        "variable_fields": ["opcode", "imm12lo", "funct3", "rs1", "rs2", "imm12hi"],
    },
    "B-type": {
        "variable_fields": ["opcode", "bimm12lo", "funct3", "rs1", "rs2", "bimm12hi"],
    },
    "U-type": {
        "variable_fields": ["opcode", "rd", "imm20"],
    },
    "J-type": {
        "variable_fields": ["opcode", "rd", "jimm20"],
    },
}
latex_fixed_fields = [
    (31, 25),
    (24, 20),
    (19, 15),
    (14, 12),
    (11, 7),
    (6, 0),
]

# Pseudo-ops present in the generated encodings.
# By default pseudo-ops are not listed as they are considered aliases
# of their base instruction.
emitted_pseudo_ops = [
    "pause",
    "prefetch_i",
    "prefetch_r",
    "prefetch_w",
    "rstsa16",
    "rstsa32",
    "srli32_u",
    "slli_rv32",
    "srai_rv32",
    "srli_rv32",
    "umax32",
    "c_mop_1",
    "c_sspush_x1",
    "c_mop_3",
    "c_mop_5",
    "c_sspopchk_x5",
    "c_mop_7",
    "c_mop_9",
    "c_mop_11",
    "c_mop_13",
    "c_mop_15",
    "mop_r_0",
    "mop_r_1",
    "mop_r_2",
    "mop_r_3",
    "mop_r_4",
    "mop_r_5",
    "mop_r_6",
    "mop_r_7",
    "mop_r_8",
    "mop_r_9",
    "mop_r_10",
    "mop_r_11",
    "mop_r_12",
    "mop_r_13",
    "mop_r_14",
    "mop_r_15",
    "mop_r_16",
    "mop_r_17",
    "mop_r_18",
    "mop_r_19",
    "mop_r_20",
    "mop_r_21",
    "mop_r_22",
    "mop_r_23",
    "mop_r_24",
    "mop_r_25",
    "mop_r_26",
    "mop_r_27",
    "mop_r_28",
    "sspopchk_x1",
    "sspopchk_x5",
    "ssrdp",
    "mop_r_29",
    "mop_r_30",
    "mop_r_31",
    "mop_r_32",
    "mop_rr_0",
    "mop_rr_1",
    "mop_rr_2",
    "mop_rr_3",
    "mop_rr_4",
    "mop_rr_5",
    "mop_rr_6",
    "mop_rr_7",
    "sspush_x1",
    "sspush_x5",
    "lpad",
    "bclri.rv32",
    "bexti.rv32",
    "binvi.rv32",
    "bseti.rv32",
    "zext.h.rv32",
    "rev8.h.rv32",
    "rori.rv32",
]
