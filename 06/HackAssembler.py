# Convention

# Functionality
# This program converts file written in Symbolic Hack-Assembly to Binary Hack-Assembly language. 

# I/O
# Input: From file Xxx.asm
# Output: To file Xxx.hack

# Assumptions:
# 1. Xxx.asm (input file) is error free.

# Components
# 1. Parser: Unpacks instructions and arranges data in format used by the program
# 2. Code: Resolves each field into its corresponding binary value
# 3. SymbolTable: HashMap mapping symbol to address value
# 4. Main: Driver Function, initializes I/O file


# Assembler Function
# The Assembler will do its job in 2-passes
# 1st pass: It will identify all the symbols and add them to the symbolTable
# 2nd pass: Convert all the symbolic instructions to binary instructions


# Instuction sample


import sys

# Steps:
# 1. Read Input file
# 2. Generate the Output File 
# 3. 


# CONSTANTS
COMP_MAP = {
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "X": "110000",
    "!X": "110001",
    "-D": "001111",
    "-X": "110011",
    "D+1": "011111",
    "X+1": "110111",
    "D-1": "001110",
    "X-1": "110010",
    "D+X": "000010",
    "X+D": "000010",
    "D-X": "010011",
    "X-D": "000111",
    "D&X": "000000",
    "X&D": "000000",
    "D|X": "010101",
    "X|D": "010101",
}

DEST_MAP = {
    "-1": "000",
    "M" : "001",
    "D" : "010",
    "DM" : "011",
    "MD" : "011",
    "A" : "100",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "ADM":"111",
    "AMD": "111",
    "DAM": "111",
    "DMA": "111",
    "DAM": "111",
    "DMA": "111"
}

JUMP_MAP = {
    "-1" : "000",
    "JGT" : "001",
    "JEQ" : "010",
    "JGE" : "011",
    "JLT" : "100",
    "JNE" : "101",
    "JLE" : "110",
    "JMP" : "111"
}

class HackAssembler:
    
    input = None
    out_file = None
    symbolTable = {}
    var_addr = None

    def __init__(self, input_file):
        self.input = input_file
        self.symbolTable = self.init_symbol_table()
        self.out_file = self.out_file_name(input_file)
        self.var_addr = 16
        self.Main()

    def init_symbol_table(self):
        symbolTable = {
            "SP"     :     0,
            "LCL"    :     1,
            "ARG"    :     2,
            "THIS"   :     3,
            "THAT"   :     4,
            "SCREEN" : 16384,
            "KBD"    : 24576,
        }

        #registers
        for i in range(16):
            symbolTable[f"R{i}"] = i
        
        return symbolTable

    def str_to_15(self, str):    
        while len(str) < 15:
            str = '0'+ str
        return str

    def out_file_name(self, file_name):
        temp = file_name.split('.')
        of_name = "{}.hack".format(temp[0])
        return of_name
    
    def A_Instruction(self, line):
        var = line[1:]
        
        addr = None
        if var.isdigit():
            addr = int(var)
            addr = self.str_to_15(bin(addr).replace('0b',''))
            return '0'+addr

        if var not in self.symbolTable.keys():
            self.symbolTable[var] = self.var_addr
            self.var_addr += 1
        
        addr = self.str_to_15(bin(self.symbolTable[var]).replace("0b",""))
        ins = '0'+addr
        return ins

    def L_Instruction(self, line):
        label = line[1:-1]
        addr = self.symbolTable[label]
        # symbolic_ins = '@{}'.format(addr)
        addr_bin = self.str_to_15(bin(addr).replace("0b", ""))
        ins = '0' + addr_bin

        return ins

    def C_Instruction(self, line):
        
        dest = "-1"
        comp = None
        jump = "-1"

        if ";J" in line:
            [line, jump] = line.split(';')
        if "=" in line:
            [dest, line] = line.split('=')

        if ';' in line:
            comp = line[:-1]
        else:
            comp = line

        # comp
        a = '0'
        if 'M' in comp:
            a = '1'
        comp = comp.replace('M','X')
        comp = comp.replace('A','X')
        
        
        bin_comp = COMP_MAP[comp]

        # dest
        bin_dest = DEST_MAP[dest]

        # jump
        bin_jump = JUMP_MAP[jump]

        ins = "111"+a+bin_comp+bin_dest+bin_jump
        return ins

    def Main(self):
        inFile = open(self.input,"r")
        inFile_lines = inFile.readlines()
        outFile = open(self.out_file,"w")

        # 1st pass - Add constants into symbolTable
        # Initialise constant values
        
        # Add
        lineCount = 0
        for _line in inFile_lines:
            line = _line
            line = line.replace(' ','')
            line = line.replace('\n','')

            if line == "" or line.startswith('//'):
                continue
            
            line = line.split('//')[0]
            

            if line.startswith('(') and line.endswith(')'):
                label = line[1:].split(')')[0]
                self.symbolTable[label] = lineCount
                lineCount -= 1
            
            lineCount += 1
            
        # 2nd pass - 
        for _line in inFile_lines:
            line = _line
            line = line.replace(' ','')
            line = line.replace('\n','')
            
            if line == "" or line.startswith('//'):
                continue
            
            line = line.split('//')[0]

            instruction = None

            if line.startswith('@'):
                instruction = self.A_Instruction(line)
            elif line.startswith('('):
                continue
            else:
                instruction = self.C_Instruction(line)

            if instruction:
                outFile.write(instruction)
                outFile.write('\n')


def main():

    if len(sys.argv) < 2:
        print("Error: No input file provided.\n")
        print("Input format:")
        print("python HackAssembler.py <input_file>")
        return

    HackAssembler(sys.argv[1])
    



if __name__ == "__main__":
    main()
