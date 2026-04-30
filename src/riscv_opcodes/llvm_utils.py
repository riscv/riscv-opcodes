import logging
import os
import re
from dataclasses import asdict, dataclass
from enum import Enum, IntEnum, auto, unique
from pathlib import Path
from typing import Any, List, Optional, Sequence, Set, Tuple

from .shared_utils import CsrDict, InstrDict, read_extension_file

logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_bits(value: int, offset: int, n: int) -> str:
    decimal = (value >> offset) & ((1 << n) - 1)
    return "0b" + "{0:b}".format(decimal).zfill(n)



def _is_vector(mnemonic: str) -> bool:
    return mnemonic.startswith(("V", "v"))


def _ext_basename(ext_path: str) -> str:
    """Return the basename of an extension file path, e.g. 'unratified/rv_xssr' -> 'rv_xssr'."""
    return os.path.basename(ext_path)


def _ext_to_name(ext_basename: str) -> str:
    """Strip leading 'rv[32]_x' to get the RISC-V extension name, e.g. 'rv_xssr' -> 'ssr'."""
    name = ext_basename
    if name.startswith("rv_x"):
        name = name[4:]
    if name.startswith("rv32_x"):
        name = name[6:]
    if name.startswith("rv64_x"):
        name = name[6:]
    return name


def _ext_to_defprefix(ext_name: str) -> str:
    return ext_name.upper() + "_"


def _ext_to_decoderns(ext_name: str) -> str:
    return ext_name


def _ext_to_camel(ext_name: str) -> str:
    parts = [part for part in re.split(r"[^0-9A-Za-z]+", ext_name) if part]
    return "".join(part[:1].upper() + part[1:] for part in parts)


def _ext_to_feature_name(ext_name: str) -> str:
    return f"FeatureVendor{_ext_to_camel('x' + ext_name)}"


def _ext_to_feature_flag(ext_name: str) -> str:
    return f"HasVendor{_ext_to_camel('x' + ext_name)}"


def _ext_to_feature_label(ext_name: str) -> str:
    return ("x" + ext_name)[:1].upper() + ("x" + ext_name)[1:]


def _feature_description(ext_basename: str) -> str:
    lines: list[str] = []
    for raw_line in read_extension_file(ext_basename).splitlines():
        if not raw_line.startswith("#"):
            break
        line = raw_line.removeprefix("#").strip()
        if not line:
            if lines:
                break
            continue
        if line.startswith(("INFO:", "format of a line")):
            continue
        lines.append(line)
        if line.endswith("extension"):
            break
    if not lines:
        return "Custom extension"
    return " ".join(lines)


def _ext_predicates(ext_basename: str) -> list[str]:
    predicates = [_ext_to_feature_flag(_ext_to_name(ext_basename))]
    if ext_basename.startswith("rv32_"):
        predicates.append("IsRV32")
    elif ext_basename.startswith("rv64_"):
        predicates.append("IsRV64")
    return predicates


def _render_properties(properties: dict) -> str:
    if not properties:
        return ""
    items = ", ".join(f"{k} = {v}" for k, v in properties.items())
    return f"let {items} in\n"


def _indent_block(text: str, prefix: str = "    ") -> str:
    return "".join(prefix + line if line else line for line in text.splitlines(keepends=True))


FP_MEM_LOAD_MNEMONICS = {"flh", "flah", "flb", "flab"}
FP_MEM_STORE_MNEMONICS = {"fsh", "fsah", "fsb", "fsab"}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@unique
class DataType(Enum):
    f8 = "B"
    f8alt = "AB"
    f16 = "H"
    f16alt = "AH"
    f32 = "S"
    f64 = "D"
    integer = "X"
    uinteger = "XU"
    long = "L"
    ulong = "LU"
    wide = "W"
    uwide = "WU"

    @classmethod
    def from_str(cls, type_str: str) -> "DataType":
        for label in cls:
            if type_str == label.value:
                return cls(label)
        raise ValueError(f"DataType: cannot recognize data type from string: '{type_str}'")


# ---------------------------------------------------------------------------
# Instruction format
# ---------------------------------------------------------------------------

@unique
class InstructionFormat(IntEnum):
    R = 0
    RPRS3 = auto()
    RLUIMM5 = auto()
    I = auto()
    R_RDZ = auto()
    U = auto()
    R4 = auto()
    RVF = auto()
    RFRM = auto()
    IFRM = auto()
    R4FRM = auto()
    IIMM12 = auto()
    IIMM12_RM = auto()
    SIMM12 = auto()
    IVF = auto()
    ISHAMT = auto()
    ISHAMTW = auto()
    IIMM12_RS1Z = auto()
    IIMM12_RDZ = auto()
    FREP_O = auto()
    RIMM5 = auto()
    RIMM5_RS1Z = auto()
    RIMM6 = auto()
    R_RS1Z = auto()
    R_RDZ_RS2Z = auto()
    BIMM12 = auto()

    @classmethod
    def _operand_map(cls):
        return (
            (cls.R,      {"rd", "rs1", "rs2"}),
            (cls.RPRS3,  {"rs1", "rs2", "prs3"}),
            (cls.RLUIMM5, {"rd", "rs1", "rs2", "Luimm5"}),
            (cls.I,      {"rd", "rs1"}),
            (cls.R_RDZ,  {"rs1", "rs2"}),
            (cls.U,      {"rd"}),
            (cls.R4,     {"rd", "rs1", "rs2", "rs3"}),
            (cls.RVF,    {"rd", "rs1", "rs2"}),
            (cls.RFRM,   {"rd", "rs1", "rs2", "rm"}),
            (cls.IFRM,   {"rd", "rs1", "rm"}),
            (cls.R4FRM,  {"rs1", "rs2", "rs3", "rd", "rm"}),
            (cls.IIMM12, {"rs1", "rd", "imm12"}),
            (cls.IIMM12_RM, {"rs1", "rd", "imm12", "rm"}),
            (cls.SIMM12, {"rs1", "rs2", "imm12lo", "imm12hi"}),
            (cls.IVF,    {"rd", "rs1"}),
            (cls.ISHAMT, {"rd", "rs1", "shamt"}),
            (cls.ISHAMT, {"rd", "rs1", "shamtd"}),
            (cls.ISHAMTW, {"rd", "rs1", "shamtw"}),
            (cls.IIMM12_RS1Z, {"rd", "imm12"}),
            (cls.IIMM12_RDZ, {"rs1", "imm12"}),
            (cls.FREP_O, {"rs1", "imm12", "stagger_max", "stagger_mask"}),
            (cls.RIMM5, {"rd", "rs1", "imm5"}),
            (cls.RIMM5_RS1Z, {"rd", "imm5"}),
            (cls.RIMM6, {"rd", "rs1", "imm6"}),
            (cls.R_RS1Z, {"rd", "rs2"}),
            (cls.R_RDZ_RS2Z, {"rs1"}),
            (cls.BIMM12, {"rs1", "imm5", "bimm12hi", "bimm12lo"}),
        )

    @classmethod
    def from_operands(cls, operands: Set[str]) -> "InstructionFormat":
        for fmt, ops in cls._operand_map():
            if operands == ops:
                return cls(fmt)
        raise ValueError(
            f"InstructionFormat: cannot recognize format from operands: {operands}"
        )


# ---------------------------------------------------------------------------
# Encoding dataclass
# ---------------------------------------------------------------------------

@dataclass
class Encoding:
    opcode: str
    rs1: str
    rs2: str
    csr: str
    funct2: str
    funct3: str
    funct6: str
    funct7: str
    imm12: str
    imm11_7: str
    imm11_5: str
    imm12hi: str
    imm12lo: str
    f2: str
    vecfltop: str
    r: str
    vfmt: str

    @classmethod
    def from_int(cls, value: int) -> "Encoding":
        return cls(
            opcode   = _extract_bits(value,  0,  7),
            rs1      = _extract_bits(value, 15,  5),
            rs2      = _extract_bits(value, 20,  5),
            csr      = _extract_bits(value, 20, 12),
            funct2   = _extract_bits(value, 25,  2),
            funct3   = _extract_bits(value, 12,  3),
            funct6   = _extract_bits(value, 26,  6),
            funct7   = _extract_bits(value, 25,  7),
            imm12    = _extract_bits(value, 20, 12),
            imm11_7  = _extract_bits(value, 27,  5),
            imm11_5  = _extract_bits(value, 25,  7),
            imm12hi  = _extract_bits(value, 25,  7),
            imm12lo  = _extract_bits(value,  7,  5),
            f2       = _extract_bits(value, 30,  2),
            vecfltop = _extract_bits(value, 25,  5),
            r        = _extract_bits(value, 14,  1),
            vfmt     = _extract_bits(value, 12,  2),
        )

    @classmethod
    def from_string(cls, s: str) -> "Encoding":
        return cls.from_int(int(s, 0))


# ---------------------------------------------------------------------------
# Instruction dataclass
# ---------------------------------------------------------------------------

@dataclass
class Instruction:
    mnemonic: str
    encoding: Encoding
    format: InstructionFormat
    encoding_repr: str

    @classmethod
    def from_dict(cls, mnemonic: str, spec: dict) -> "Instruction":
        fmt = InstructionFormat.from_operands(set(spec["variable_fields"]))
        print(f"Instruction {mnemonic}: operands {spec['variable_fields']} -> format {fmt}")
        enc = Encoding.from_string(spec["match"])
        if _is_vector(mnemonic):
            if fmt == InstructionFormat.R:
                fmt = InstructionFormat.RVF
            elif fmt == InstructionFormat.I:
                fmt = InstructionFormat.IVF
            else:
                raise RuntimeError(
                    f"Unknown vector instruction format for {mnemonic}: {fmt}"
                )
        return cls(mnemonic=mnemonic, encoding=enc, format=fmt,
                   encoding_repr=spec["encoding"])


# ---------------------------------------------------------------------------
# Operand type resolution
# ---------------------------------------------------------------------------

TBLGEN_OPERAND_TYPES = {
    DataType.f8:       "FPR16",
    DataType.f8alt:    "FPR16",
    DataType.f16:      "FPR16",
    DataType.f16alt:   "FPR16",
    DataType.f32:      "FPR32",
    DataType.f64:      "FPR64",
    DataType.integer:  "GPR",
    DataType.uinteger: "GPR",
    DataType.long:     "GPR",
    DataType.ulong:    "GPR",
    DataType.wide:     "GPR",
    DataType.uwide:    "GPR",
}


def _get_dtypes(mnemonic: str) -> dict:
    if mnemonic == "flh":
        return {"rs1": "GPR", "rd": TBLGEN_OPERAND_TYPES[DataType.f16]}
    elif mnemonic == "flah":
        return {"rs1": "GPR", "rd": TBLGEN_OPERAND_TYPES[DataType.f16alt]}
    elif mnemonic == "flb":
        return {"rs1": "GPR", "rd": TBLGEN_OPERAND_TYPES[DataType.f8]}
    elif mnemonic == "flab":
        return {"rs1": "GPR", "rd": TBLGEN_OPERAND_TYPES[DataType.f8alt]}
    elif mnemonic == "fsh":
        return {"rs1": "GPR", "rs2": TBLGEN_OPERAND_TYPES[DataType.f16]}
    elif mnemonic == "fsah":
        return {"rs1": "GPR", "rs2": TBLGEN_OPERAND_TYPES[DataType.f16alt]}
    elif mnemonic == "fsb":
        return {"rs1": "GPR", "rs2": TBLGEN_OPERAND_TYPES[DataType.f8]}
    elif mnemonic == "fsab":
        return {"rs1": "GPR", "rs2": TBLGEN_OPERAND_TYPES[DataType.f8alt]}

    # COPIFT instructions exchange data through SSR-backed floating-point
    # registers even when their mnemonics resemble integer/FP conversions or
    # comparisons. Their visible asm operands are therefore all FPR64.
    if mnemonic.endswith(".copift"):
        return {"rs1": "FPR64", "rs2": "FPR64", "rs3": "FPR64", "rd": "FPR64"}

    mn = mnemonic
    if _is_vector(mn):
        mn = re.sub(r"[\._][rR]", "", mn)

    inst_t = mn.upper().replace(".", "_").split("_")[1:]
    try:
        source_t = TBLGEN_OPERAND_TYPES[DataType.from_str(inst_t[-1])]
        dest_t   = TBLGEN_OPERAND_TYPES[DataType.from_str(inst_t[0])]
    except (ValueError, IndexError):
        # No recognizable FP type suffix: treat as integer instruction.
        return {"rs1": "GPR", "rs2": "GPR", "rs3": "GPR", "rd": "GPR"}

    predicates = ("fclass", "feq", "fne", "fgt", "flt", "fle", "fge")
    if re.match(r"^(v)?({})".format("|".join(predicates)), mnemonic, re.IGNORECASE):
        dest_t = TBLGEN_OPERAND_TYPES[DataType.integer]

    return {"rs1": source_t, "rs2": source_t, "rs3": source_t, "rd": dest_t}


def _get_properties(mnemonic: str) -> dict:
    props = {"hasSideEffects": 0, "mayLoad": 0, "mayStore": 0}
    if mnemonic in ("flh", "flah", "flb", "flab"):
        props["mayLoad"] = 1
    elif mnemonic in ("fsh", "fsah", "fsb", "fsab"):
        props["mayStore"] = 1
    elif mnemonic in ("p.beqimm", "p.bneimm"):
        props["isBranch"] = 1
        props["isTerminator"] = 1
    return props


# ---------------------------------------------------------------------------
# Instruction TableGen rendering
# ---------------------------------------------------------------------------

def _tblgen_def(inst: Instruction, ext_name: str) -> str:
    e = inst.encoding
    dtype = _get_dtypes(inst.mnemonic)
    defprefix = _ext_to_defprefix(ext_name)
    decoderns = _ext_to_decoderns(ext_name)
    tblgen_name = defprefix + inst.mnemonic.upper().replace(".", "_")
    mnemonic = inst.mnemonic.replace("_", ".")
    props = _get_properties(inst.mnemonic)
    props["DecoderNamespace"] = f'"{decoderns}"'
    props_str = _render_properties(props)

    fmt = inst.format
    if fmt == InstructionFormat.R:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstR<\n"
            f"                {e.funct7}, // funct7\n"
            f"                {e.funct3}, // funct3\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $rs2\">,\n"
            f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.RLUIMM5:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, uimm5:$imm5),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $rs2, $imm5\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<5> rs1;\n"
            f"    bits<5> rs2;\n"
            f"    bits<5> imm5;\n"
            f"    let Inst{{31-30}} = {e.funct2};\n"
            f"    let Inst{{29-25}} = imm5;\n"
            f"    let Inst{{24-20}} = rs2;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.RPRS3:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rs3']}:$prs3),\n"
            f"                \"{mnemonic}\", \"$rs1, $rs2, $prs3\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rs1;\n"
            f"    bits<5> rs2;\n"
            f"    bits<5> prs3;\n"
            f"    let Inst{{31-25}} = {e.funct7};\n"
            f"    let Inst{{24-20}} = rs2;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = prs3;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.RIMM5:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, uimm5:$imm5),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $imm5\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<5> rs1;\n"
            f"    bits<5> imm5;\n"
            f"    let Inst{{31-25}} = {e.funct7};\n"
            f"    let Inst{{24-20}} = imm5;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.RIMM5_RS1Z:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins uimm5:$imm5),\n"
            f"                \"{mnemonic}\", \"$rd, $imm5\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<5> imm5;\n"
            f"    let Inst{{31-25}} = {e.funct7};\n"
            f"    let Inst{{24-20}} = imm5;\n"
            f"    let Inst{{19-15}} = 0b00000;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.RIMM6:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, simm6:$imm6),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $imm6\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<5> rs1;\n"
            f"    bits<6> imm6;\n"
            f"    let Inst{{31-26}} = {e.funct6};\n"
            f"    let Inst{{25-20}} = imm6;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.R_RS1Z:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs2']}:$rs2),\n"
            f"                \"{mnemonic}\", \"$rd, $rs2\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<5> rs2;\n"
            f"    let Inst{{31-25}} = {e.funct7};\n"
            f"    let Inst{{24-20}} = rs2;\n"
            f"    let Inst{{19-15}} = {e.rs1};\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.R_RDZ_RS2Z:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs1']}:$rs1),\n"
            f"                \"{mnemonic}\", \"$rs1\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rs1;\n"
            f"    let Inst{{31-25}} = {e.funct7};\n"
            f"    let Inst{{24-20}} = 0b00000;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = 0b00000;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.I:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstI<\n"
            f"                {e.funct3}, // funct3\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1\">,\n"
            f"                Sched<[]> {{\n"
            f"    let imm12 = {e.imm12};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.IIMM12:
        if inst.mnemonic in FP_MEM_LOAD_MNEMONICS:
            return (
                f"{props_str}"
                f"def {tblgen_name} : RVInstI<\n"
                f"                {e.funct3}, // funct3\n"
                f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
                f"                (outs {dtype['rd']}:$rd),\n"
                f"                (ins GPRMem:$rs1, simm12:$imm12),\n"
                f"                \"{mnemonic}\", \"$rd, ${{imm12}}(${{rs1}})\">,\n"
                f"                Sched<[]>;\n"
            )
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstI<\n"
                f"                {e.funct3}, // funct3\n"
                f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
                f"                (outs {dtype['rd']}:$rd),\n"
                f"                (ins {dtype['rs1']}:$rs1, simm12:$imm12),\n"
                f"                \"{mnemonic}\", \"$rd, $rs1, ${{imm12}}(${{rs1}})\">,\n"
                f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.IIMM12_RM:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, simm12:$imm12, frmarg:$frm),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $imm12, $frm\",\n"
            f"                [], InstFormatI>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<5> rs1;\n"
            f"    bits<12> imm12;\n"
            f"    bits<3> frm;\n"
            f"    let Inst{{31-20}} = imm12;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = frm;\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
            f"def: InstAlias<\"{mnemonic} $rd, $rs1, $imm12\",\n"
            f"               ({tblgen_name} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, simm12:$imm12, FRM_DYN)>;\n"
        )
    elif fmt == InstructionFormat.IIMM12_RS1Z:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins simm12:$imm12),\n"
            f"                \"{mnemonic}\", \"$rd, $imm12\",\n"
            f"                [], InstFormatI>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rd;\n"
            f"    bits<12> imm12;\n"
            f"    let Inst{{31-20}} = imm12;\n"
            f"    let Inst{{19-15}} = 0b00000;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = rd;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.IIMM12_RDZ:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs1']}:$rs1, simm12:$imm12),\n"
            f"                \"{mnemonic}\", \"$rs1, $imm12\",\n"
            f"                [], InstFormatI>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rs1;\n"
            f"    bits<12> imm12;\n"
            f"    let Inst{{31-20}} = imm12;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = 0b00000;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.FREP_O:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs1']}:$rs1, simm12:$imm12, uimm3:$stagger_max, uimm4:$stagger_mask),\n"
            f"                \"{mnemonic}\", \"$rs1, $imm12, $stagger_max, $stagger_mask\",\n"
            f"                [], InstFormatI>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<12> imm12;\n"
            f"    bits<5> rs1;\n"
            f"    bits<3> stagger_max;\n"
            f"    bits<4> stagger_mask;\n"
            f"    let Inst{{31-20}} = imm12;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = stagger_max;\n"
            f"    let Inst{{11-8}} = stagger_mask;\n"
            f"    let Inst{{7}} = 0b1;\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.SIMM12:
        if inst.mnemonic in FP_MEM_STORE_MNEMONICS:
            return (
                f"{props_str}"
                f"def {tblgen_name} : RVInstS<\n"
                f"                {e.funct3}, // funct3\n"
                f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
                f"                (outs ),\n"
                f"                (ins {dtype['rs2']}:$rs2, GPRMem:$rs1, simm12:$imm12),\n"
                f"                \"{mnemonic}\", \"$rs2, ${{imm12}}(${{rs1}})\">,\n"
                f"                Sched<[]>;\n"
            )
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstS<\n"
                f"                {e.funct3}, // funct3\n"
                f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs2']}:$rs2, {dtype['rs1']}:$rs1, simm12:$imm12),\n"
            f"                \"{mnemonic}\", \"$rs2, ${{imm12}}(${{rs1}})\">,\n"
            f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.ISHAMT:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstIShift<\n"
            f"                {e.imm11_7}, // imm11_7\n"
            f"                {e.funct3}, // funct3\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, uimmlog2xlen:$shamt),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $shamt\">,\n"
            f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.ISHAMTW:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstIShiftW<\n"
            f"                {e.imm11_5}, // imm11_5\n"
            f"                {e.funct3}, // funct3\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, uimm5:$shamt),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $shamt\">,\n"
            f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.R_RDZ:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInst<\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2),\n"
            f"                \"{mnemonic}\", \"$rs1, $rs2\",\n"
            f"                [], InstFormatR>,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> rs1;\n"
            f"    bits<5> rs2;\n"
            f"    let Inst{{31-25}} = {e.funct7};\n"
            f"    let Inst{{24-20}} = rs2;\n"
            f"    let Inst{{19-15}} = rs1;\n"
            f"    let Inst{{14-12}} = {e.funct3};\n"
            f"    let Inst{{11-7}} = {e.imm12lo};\n"
            f"    let Inst{{6-0}} = {e.opcode};\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.BIMM12:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstB<\n"
            f"                {e.funct3}, // funct3\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs ),\n"
            f"                (ins {dtype['rs1']}:$rs1, simm5:$imm5, simm13_lsb0:$imm12),\n"
            f"                \"{mnemonic}\", \"$rs1, $imm5, $imm12\">,\n"
            f"                Sched<[]> {{\n"
            f"    bits<5> imm5;\n"
            f"    let rs2 = imm5;\n"
            f"}}\n"
        )
    elif fmt == InstructionFormat.R4:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstR4<\n"
            f"                {e.funct2}, // funct2\n"
            f"                {e.funct3}, // funct3\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rs3']}:$rs3),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $rs2, $rs3\">,\n"
            f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.RFRM:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstRFrm<\n"
            f"                {e.funct7}, // funct7\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, frmarg:$frm),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $rs2, $frm\">,\n"
            f"                Sched<[]>;\n"
            f"def: InstAlias<\"{mnemonic} $rd, $rs1, $rs2\",\n"
            f"               ({tblgen_name} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, FRM_DYN)>;\n"
        )
    elif fmt == InstructionFormat.IFRM:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstRFrm<\n"
            f"                {e.funct7}, // funct7\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, frmarg:$frm),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $frm\">,\n"
            f"                Sched<[]>\n"
            f"                {{ let rs2 = {e.rs2}; }}\n"
            f"def: InstAlias<\"{mnemonic} $rd, $rs1\",\n"
            f"               ({tblgen_name} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, FRM_DYN)>;\n"
        )
    elif fmt == InstructionFormat.R4FRM:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstR4Frm<\n"
            f"                {e.funct2}, // funct2\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rs3']}:$rs3, frmarg:$frm),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $rs2, $rs3, $frm\">,\n"
            f"                Sched<[]>;\n"
            f"def: InstAlias<\"{mnemonic} $rd, $rs1, $rs2, $rs3\",\n"
            f"               ({tblgen_name} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rd']}:$rs3, FRM_DYN)>;\n"
        )
    elif fmt == InstructionFormat.RVF:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstR<\n"
            f"                {e.funct7}, // funct7 = f2:vecfltop\n"
            f"                {e.funct3}, // funct3 = r:vfmt\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1, $rs2\">,\n"
            f"                Sched<[]>;\n"
        )
    elif fmt == InstructionFormat.IVF:
        return (
            f"{props_str}"
            f"def {tblgen_name} : RVInstR<\n"
            f"                {e.funct7}, // funct7 = f2:vecfltop\n"
            f"                {e.funct3}, // funct3 = r:vfmt\n"
            f"                RISCVOpcode<\"{tblgen_name}\", {e.opcode}>,\n"
            f"                (outs {dtype['rd']}:$rd),\n"
            f"                (ins {dtype['rs1']}:$rs1),\n"
            f"                \"{mnemonic}\", \"$rd, $rs1\">,\n"
            f"                Sched<[]> {{\n"
            f"    let rs2 = {e.rs2};\n"
            f"}}\n"
        )
    else:
        raise NotImplementedError(f"TableGen rendering not implemented for format: {fmt}")


def _tblgen_alias(
    inst: Instruction,
    uses_mnemonic: str,
    uses_extension: str,
    defprefix: Optional[str],
) -> str:
    dtype = _get_dtypes(inst.mnemonic)
    mnemonic = inst.mnemonic.replace("_", ".")
    use = uses_mnemonic.upper().replace(".", "_")
    if defprefix:
        use = defprefix + use

    fmt = inst.format
    if fmt == InstructionFormat.R:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $rs2\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2), 0>;\n"
        )
    elif fmt == InstructionFormat.RLUIMM5:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $rs2, $imm5\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, uimm5:$imm5), 0>;\n"
        )
    elif fmt == InstructionFormat.RPRS3:
        return (
            f"def : InstAlias<\"{mnemonic} $rs1, $rs2, $prs3\","
            f" ({use} {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rs3']}:$prs3), 0>;\n"
        )
    elif fmt == InstructionFormat.RIMM5:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $imm5\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, uimm5:$imm5), 0>;\n"
        )
    elif fmt == InstructionFormat.RIMM5_RS1Z:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $imm5\","
            f" ({use} {dtype['rd']}:$rd, uimm5:$imm5), 0>;\n"
        )
    elif fmt == InstructionFormat.RIMM6:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $imm6\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, simm6:$imm6), 0>;\n"
        )
    elif fmt == InstructionFormat.R_RS1Z:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs2\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs2']}:$rs2), 0>;\n"
        )
    elif fmt == InstructionFormat.R_RDZ_RS2Z:
        return (
            f"def : InstAlias<\"{mnemonic} $rs1\","
            f" ({use} {dtype['rs1']}:$rs1), 0>;\n"
        )
    elif fmt == InstructionFormat.R_RDZ:
        return (
            f"def : InstAlias<\"{mnemonic} $rs1, $rs2\","
            f" ({use} {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2), 0>;\n"
        )
    elif fmt == InstructionFormat.I:
        rm_arg = ""
        if uses_mnemonic.startswith("fcvt") and uses_extension != "rv_xsflts":
            rm_arg = ", FRM_DYN"
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1{rm_arg}), 0>;\n"
        )
    elif fmt == InstructionFormat.IIMM12:
        if inst.mnemonic in FP_MEM_LOAD_MNEMONICS:
            return (
                f"def : InstAlias<\"{mnemonic} $rd, $imm12($rs1)\","
                f" ({use} {dtype['rd']}:$rd, GPRMem:$rs1, simm12:$imm12), 0>;\n"
            )
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $imm12\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, simm12:$imm12), 0>;\n"
        )
    elif fmt == InstructionFormat.IIMM12_RM:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $imm12, frmarg:$frm\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, simm12:$imm12, frmarg:$frm), 0>;\n"
        )
    elif fmt == InstructionFormat.IIMM12_RS1Z:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $imm12\","
            f" ({use} {dtype['rd']}:$rd, simm12:$imm12), 0>;\n"
        )
    elif fmt == InstructionFormat.IIMM12_RDZ:
        return (
            f"def : InstAlias<\"{mnemonic} $rs1, $imm12\","
            f" ({use} {dtype['rs1']}:$rs1, simm12:$imm12), 0>;\n"
        )
    elif fmt == InstructionFormat.FREP_O:
        return (
            f"def : InstAlias<\"{mnemonic} $rs1, $imm12, $stagger_max, $stagger_mask\","
            f" ({use} {dtype['rs1']}:$rs1, simm12:$imm12, uimm3:$stagger_max, uimm4:$stagger_mask), 0>;\n"
        )
    elif fmt == InstructionFormat.SIMM12:
        if inst.mnemonic in FP_MEM_STORE_MNEMONICS:
            return (
                f"def : InstAlias<\"{mnemonic} $rs2, $imm12($rs1)\","
                f" ({use} {dtype['rs2']}:$rs2, GPRMem:$rs1, simm12:$imm12), 0>;\n"
            )
        return (
            f"def : InstAlias<\"{mnemonic} $rs2, $rs1, $imm12\","
            f" ({use} {dtype['rs2']}:$rs2, {dtype['rs1']}:$rs1, simm12:$imm12), 0>;\n"
        )
    elif fmt == InstructionFormat.ISHAMT:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $shamt\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, uimmlog2xlen:$shamt), 0>;\n"
        )
    elif fmt == InstructionFormat.ISHAMTW:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $shamt\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, uimm5:$shamt), 0>;\n"
        )
    elif fmt == InstructionFormat.R4:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $rs2, $rs3\","
            f" ({use}  {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rs3']}:$rs3), 0>;\n"
        )
    elif fmt == InstructionFormat.RFRM:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $rs2\","
            f" ({use}  {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, FRM_DYN), 0>;\n"
        )
    elif fmt == InstructionFormat.IFRM:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, FRM_DYN), 0>;\n"
        )
    elif fmt == InstructionFormat.R4FRM:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $rs2, $rs3, frmarg:$frm\","
            f" ({use}  {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2, {dtype['rs3']}:$rs3, frmarg:$frm), 0>;\n"
        )
    elif fmt == InstructionFormat.RVF:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1, $rs2\","
            f" ({use}  {dtype['rd']}:$rd, {dtype['rs1']}:$rs1, {dtype['rs2']}:$rs2), 0>;\n"
        )
    elif fmt == InstructionFormat.IVF:
        return (
            f"def : InstAlias<\"{mnemonic} $rd, $rs1\","
            f" ({use} {dtype['rd']}:$rd, {dtype['rs1']}:$rs1), 0>;\n"
        )
    else:
        raise NotImplementedError(f"Alias rendering not implemented for format: {fmt}")


# ---------------------------------------------------------------------------
# CSR TableGen rendering
# ---------------------------------------------------------------------------

def _csr_def_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", name)
    return "SysReg_" + sanitized.upper()


def _tblgen_csr_def(num: int, name: str) -> str:
    return f'def {_csr_def_name(name)} : SysReg<"{name}", 0x{num:03X}>;'


def make_llvm_csrs(csr_dict: CsrDict):
    """Generate LLVM TableGen CSR definitions from per-extension CSR files."""
    lines = [
        "// Auto-generated by riscv_opcodes. DO NOT EDIT.",
        "",
    ]

    all_csrs = [pair for pairs in csr_dict.values() for pair in pairs]
    for num, name in sorted(all_csrs, key=lambda item: item[0]):
        lines.append(_tblgen_csr_def(num, name))

    Path("csr.td").write_text("\n".join(lines) + "\n", encoding="utf-8")
    logging.info("csr.td generated successfully")


def make_llvm_features(extensions: Sequence[str]):
    """Generate LLVM TableGen feature definitions from the selected extensions."""
    lines = [
        "// Auto-generated by riscv_opcodes. DO NOT EDIT.",
        "",
    ]
    seen: set[str] = set()

    for ext in extensions:
        ext_basename = _ext_basename(ext)
        if ext_basename in seen:
            continue
        seen.add(ext_basename)

        ext_name = _ext_to_name(ext_basename)
        feature_name = _ext_to_feature_name(ext_name)
        feature_flag = _ext_to_feature_flag(ext_name)
        feature_label = _ext_to_feature_label(ext_name)
        feature_desc = _feature_description(ext_basename)
        feature_method = feature_flag[:1].lower() + feature_flag[1:]

        lines.extend([
            f"def {feature_name}",
            f'    : SubtargetFeature<"x{ext_name}", "{feature_flag}", "true",',
            f'                       "\'{feature_label}\' ({feature_desc})">;',
            f"def {feature_flag}",
            f'    : Predicate<"Subtarget->{feature_method}()">,',
            f"      AssemblerPredicate<(all_of {feature_name}),",
            f'                         "\'{feature_label}\' ({feature_desc})">;',
            "",
        ])

    Path("feature.td").write_text("\n".join(lines), encoding="utf-8")
    logging.info("feature.td generated successfully")

# ---------------------------------------------------------------------------
# LIT test rendering
# ---------------------------------------------------------------------------

def _get_asm_operands(inst: Instruction) -> List[str]:
    if inst.mnemonic in FP_MEM_LOAD_MNEMONICS:
        return ["ft0", "0(x0)"]
    if inst.mnemonic in FP_MEM_STORE_MNEMONICS:
        return ["ft0", "0(x0)"]

    asm_operand_map = {
        InstructionFormat.R:      ("rd", "rs1", "rs2"),
        InstructionFormat.RLUIMM5: ("rd", "rs1", "rs2", "imm5"),
        InstructionFormat.RPRS3:  ("rs1", "rs2", "prs3"),
        InstructionFormat.I:      ("rd", "rs1"),
        InstructionFormat.R_RDZ:  ("rs1", "rs2"),
        InstructionFormat.U:      ("rd",),
        InstructionFormat.R4:     ("rd", "rs1", "rs2", "rs3"),
        InstructionFormat.RVF:    ("rd", "rs1", "rs2"),
        InstructionFormat.RFRM:   ("rd", "rs1", "rs2", "rm"),
        InstructionFormat.IFRM:   ("rd", "rs1", "rm"),
        InstructionFormat.R4FRM:  ("rs1", "rs2", "rs3", "rd", "rm"),
        InstructionFormat.IIMM12: ("rs1", "rd", "imm12"),
        InstructionFormat.IIMM12_RM: ("rd", "rs1", "imm12", "rm"),
        InstructionFormat.IIMM12_RS1Z: ("rd", "imm12"),
        InstructionFormat.IIMM12_RDZ: ("rs1", "imm12"),
        InstructionFormat.FREP_O: ("rs1", "imm12", "stagger_max", "stagger_mask"),
        InstructionFormat.SIMM12: ("rs1", "rs2", "imm12lo", "imm12hi"),
        InstructionFormat.IVF:    ("rd", "rs1"),
        InstructionFormat.ISHAMT: ("rd", "rs1", "shamt"),
        InstructionFormat.ISHAMTW: ("rd", "rs1", "shamt"),
        InstructionFormat.RIMM5: ("rd", "rs1", "imm5"),
        InstructionFormat.RIMM5_RS1Z: ("rd", "imm5"),
        InstructionFormat.RIMM6: ("rd", "rs1", "imm6"),
        InstructionFormat.R_RS1Z: ("rd", "rs2"),
        InstructionFormat.R_RDZ_RS2Z: ("rs1",),
    }
    dtypes = _get_dtypes(inst.mnemonic)
    operands = []
    for op in asm_operand_map[inst.format]:
        if op == "rm":
            operands.append("rne")
        elif op in {"imm12", "imm12lo", "imm12hi", "shamt", "imm5", "imm6", "stagger_max", "stagger_mask"}:
            operands.append("0")
        elif dtypes.get(op) == "GPR" or (op == "prs3" and dtypes.get("rs3") == "GPR"):
            operands.append("x0")
        else:
            operands.append("ft0")
    return operands


def _to_lit_test(instructions: dict, ext_name: str) -> str:
    lines = [
        f"# RUN: llvm-mc %s -triple=riscv64 -mattr=+d,+{ext_name.lower()} "
        f"-riscv-no-aliases -show-encoding | FileCheck %s",
        "",
    ]
    for _, inst in instructions.items():
        operands = _get_asm_operands(inst)
        asm = "{} {}".format(inst.mnemonic, ", ".join(operands))
        enc = inst.encoding_repr.replace("-", "0")
        assert len(enc) == 32, f"Unexpected encoding length for {inst.mnemonic}"
        chunks_repr = re.findall("[01]{8}", enc)
        assert len(chunks_repr) == 4
        chunks_int = [int(v, 2) for v in chunks_repr]
        chunks_hex = ["0x{:02x}".format(v) for v in chunks_int]
        encoding = "[{}]".format(",".join(reversed(chunks_hex)))
        lines.append(f"# CHECK: encoding: {encoding}")
        lines.append(asm)
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def make_llvm(instr_dict: InstrDict, extensions: Sequence[str], csr_dict: CsrDict):
    """Generate LLVM TableGen definitions.

    Generates instruction definitions from the provided instruction dictionary.
    Groups instructions by their first listed extension and writes one
    ``inst.<extname>.td`` file per extension group.

    Also generates ``feature.td`` and ``csr.td`` files with LLVM feature and
    CSR definitions.
    """
    # Group instructions by their canonical extension basename.
    groups: dict[str, dict] = {}
    for mnemonic, spec in instr_dict.items():
        ext_paths = spec.get("extension", [])
        if not ext_paths:
            continue
        ext_key = _ext_basename(ext_paths[0])
        groups.setdefault(ext_key, {})[mnemonic] = spec

    for ext_basename_str, group_spec in groups.items():
        ext_name = _ext_to_name(ext_basename_str)
        defprefix = _ext_to_defprefix(ext_name)
        predicates = ", ".join(_ext_predicates(ext_basename_str))

        instructions: dict[str, Instruction] = {}
        pseudos: List[Instruction] = []
        uses: List[Tuple[str, str]] = []

        for mnemonic, spec in group_spec.items():
            mn = mnemonic.replace("_", ".")
            try:
                inst = Instruction.from_dict(mn, spec)
            except (ValueError, NotImplementedError) as e:
                logging.warning(f"Skipping {mn}: {e}")
                continue
            if "is_pseudo_of" in spec:
                inst_use = spec["is_pseudo_of"]["instruction"]
                ext_use  = spec["is_pseudo_of"]["extension"]
                pseudos.append(inst)
                uses.append((inst_use, ext_use))
            else:
                instructions[mn] = inst

        lines = [
            "// Auto-generated by riscv_opcodes. DO NOT EDIT.",
            "",
            f"let Predicates = [{predicates}] in {{",
        ]

        for _, inst in instructions.items():
            try:
                lines.append(_indent_block(_tblgen_def(inst, ext_name)))
            except (ValueError, NotImplementedError) as e:
                logging.warning(f"Skipping render of {inst.mnemonic}: {e}")

        for pseudo, (inst_use, ext_use) in zip(pseudos, uses):
            pfx = defprefix if inst_use in instructions else None
            if pfx is None:
                logging.info(
                    f"Alias to another extension: {pseudo.mnemonic:10} -> {ext_use}::{inst_use}"
                )
            lines.append(_indent_block(_tblgen_alias(pseudo, inst_use, ext_use, pfx)))

        lines.append("}")

        out_path = Path(f"inst.{ext_name}.td")
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logging.info(f"inst.{ext_name}.td generated successfully")

    make_llvm_features(extensions)
    make_llvm_csrs(csr_dict)
