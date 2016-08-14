#!/usr/bin/python

"""
A simple module for parsing the opcodes definition file for RISCV and
automatically generating code for a Verilog decoder. Because RISCV is designed
to be implemented many different ways, a full decoder cannot be generated,
because the output interface is not known. However, all of the monotonous
code to individually identify an individual instruction is generated, and
can be easily integrated into an existing interface.

No optimisation of the decoder is performed, it is assumed that any synthesis
tool you use is smart enough to spot shared logic, of which there is a lot!

Author: Ben Marshall
"""

import sys
import argparse

FIELD_IGNORE = -1
FIELD_PRED   = -2

class Instruction:
    """
    Contains information on a single instruction.
    """

    def safeName(self):
        """
        Returns a verilog-safe instruction name.
        """
        return self.name.replace(".","_").lower()

    def __init__(self, name, args, fields):
        """
        Initialise the class with a given instruction name / memonic,
        set of arguments and bitfields.
        """

        self.name = name
        self.args = args
        self.fields = []

        for f in fields:
            hi = int(f.split("..")[0])
            lo = int(f.split("..")[1].split("=")[0])
            vl = f.split("=")[1]
            
            if(vl.startswith("0x")):
                vl = int(vl[2:],16)
            elif(vl == "ignore"):
                vl = FIELD_IGNORE
            elif(vl == "pred"):
                vl = FIELD_PRED
            else:
                vl = int(vl)

            self.fields.append((hi,lo,vl))


class VerilogGen:
    """
    Container class for all decoder generation.
    """

    
    def printInstructions(self):
        """
        Prints all of the parsed instructions to stdout
        """
        for i in self.instructions.keys():
            ins = self.instructions[i]

            sys.stdout.write("> %s (" % ins.name)

            for arg in ins.args:
                sys.stdout.write("%s " % arg)

            sys.stdout.write(")")
            
            for field in ins.fields:
                sys.stdout.write(" (%d,%d,%d)" % field)
            print("")


    def __parseInputFile__(self):
        """
        Parses the input file into the class's internal data structures.
        """

        with open(self.inputFilePath,"r") as fh:
            
            lines = fh.readlines()

            for line in lines:

                if(line[0] == '#' or line[0] == '\n' or line[0] == ' '):
                    continue # Ignore, these are comments.

                tokens = [T for T in line[:-1].split(" ") if T != ""]

                i_name      = tokens[0]
                i_args      = []
                i_fields    = []
                for a in tokens[1:]:
                    if(a in self.valid_args):
                        i_args.append(a)
                    elif(a[1:] in self.valid_args):
                        i_args.append(a)
                    else:
                        i_fields.append(a)

                self.instructions[i_name] = Instruction(i_name,i_args,i_fields)
    
    def writeStandardRanges(self):
        """
        Writes a collection of constant bit ranges, useful for the manually
        coded parts of the decoder.
        """
        towrite = """
        `define RISCV_RS1       19:15
        `define RISCV_RS2       24:20
        `define RISCV_RD        11:7
        `define RISCV_IMM_11_0  31:20
        `define RISCV_IMM_11_5  31:25
        `define RISCV_IMM_4_0   11:7
        `define RISCV_IMM_31_12 31:12
        `define RISCV_FUNC_7    31:25  
        `define RISCV_FUNC_3    14:12
        """
        self.outputFile.write(towrite+"\n")

    def writeInstructionDecode(self):
        """
        Writes out all of the 'wire instrX = ....' code to the output file.
        """

        for i in self.instructions.keys():
            
            instr = self.instructions[i]
            tr = "wire %s%s =    " % (self.wire_prefix, instr.safeName())
            indent = len(tr)-4
            emitted = 0

            for i in range(0,len(instr.fields)):

                field = instr.fields[i]

                if(field[2] >= 0):
                    if(emitted >= 1):
                        tr += "\n" + " "*indent+" && "
                    fwidth = 1 + (field[0]-field[1])
                    val    = "%d'd%d" % (fwidth,field[2])
                    tr += "(%s[%d:%d] == %s)" % (self.input_signal, field[0],
                                                    field[1], val)
                    emitted += 1
                else:
                    continue

            tr += ";\n"
            self.outputFile.write(tr)


    def __init__(self, inputFile, outputFile):
        """
        Initialise the class with all parameters.
        """

        self.inputFilePath  = inputFile
        self.outputFilePath = outputFile
        self.outputFile     = open(self.outputFilePath,"w")

        self.wire_prefix    = "gen_"
        self.input_signal   = "decode_in"

        self.instructions  = {}
        self.valid_args    = ["rd", "rs1", "rs2", "rs3", "imm20", "imm12", 
            "imm12lo", "imm12hi", "shamtw", "shamt", "rm","pred","succ",
            "aqrl"]
        
        self.__parseInputFile__()


def parseArguments():
    """
    Parse any and all command line arguments.
    """

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--opcodes-file", 
                        help="The opcodes file to parse.",
                        default="opcodes")
    parser.add_argument("--verilog-file", 
                        help="The Verilog output file.",
                        default="riscv-decode.v")
    parser.add_argument("--wire-prefix",
                        help="A prefix for all generated signals.",
                        default="gen_")
    parser.add_argument("--input-signal", 
                        help="The input signal to the decoder containing the raw instruction.",
                        default="to_decode")

    args = parser.parse_args()
    return args


def main():
    """
    Runs when the module is run as a standalone script.
    """

    args = parseArguments()

    gen  = VerilogGen(args.opcodes_file, args.verilog_file)
    if(args.input_signal):
        gen.input_signal = args.input_signal
    if(args.wire_prefix):
        gen.wire_prefix  = args.wire_prefix
    gen.writeInstructionDecode()
    
    return 0

if(__name__ == "__main__"):
    sys.exit(main())
else:
    pass
