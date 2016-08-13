#!/usr/bin/python

"""
A simple module for parsing the opcodes definition file for RISCV and
automatically generating most of the code for a Verilog decoder.

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

    def __init__(self, name, args, fields):
        """
        Initialise the class.
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


    def __init__(self, inputFile):
        """
        Initialise the class with all parameters.
        """

        self.inputFilePath = inputFile
        self.instructions  = {}
        self.valid_args    = ["rd", "rs1", "rs2", "rs3", "imm20", "imm12", 
            "imm12lo", "imm12hi", "shamtw", "shamt", "rm","pred","succ",
            "aqrl"]
        
        self.__parseInputFile__()


def parseArguments():
    """
    Parse any and all command line arguments.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--opcodes-file", help="The opcodes file to parse.")

    args = parser.parse_args()
    return args


def main():
    """
    Runs when the module is run as a standalone script.
    """

    args = parseArguments()

    gen  = VerilogGen(args.opcodes_file)
    gen.printInstructions()
    
    return 0

if(__name__ == "__main__"):
    sys.exit(main())
else:
    pass
