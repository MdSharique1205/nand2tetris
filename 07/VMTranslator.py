import sys

COMMAND_TYPES = ["C_ARITHMETIC", "C_PUSH", "C_POP"]
ARITHMETIC_COMMANDS = ["add", "sub", "neg"]
COMPARISON_COMMANDS = ["eq", "gt", "lt"]
LOGICAL_COMMANDS = ["and", "or", "not"]

SEGMENT_MAPPING = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "temp": "TEMP",
}


class VMTranslator:

    outfile = None
    infile = None

    def __init__(self, filepath):
        self.infile = filepath
        self.outfile = filepath.split(".")[0] + ".asm"
        self.process()

    def process(self):
        with codeWriter(self.outfile) as code_writer:
            with open(self.infile, "r") as input_file:
                for line in input_file.readlines():
                    [command_type, arg1, arg2] = parser(line)
                    if command_type == COMMAND_TYPES[0]:
                        code_writer.write_arithmetic(command_type, arg1)
                    elif command_type in COMMAND_TYPES[1:3]:
                        code_writer.write_push_pop(command_type, arg1, arg2)
                    else:
                        print("Undefined command: ", command_type, arg1, arg2)


def parser(line):
    command_type = ""
    arg1 = ""
    arg2 = 0
    # 1. Remove spaces from start of line
    i = 0
    while i < len(line) and line[i] == " ":
        i += 1
    if i == len(line):
        line = ""
    else:
        line = line[i:]
    # 2. If starts with // ignore the line
    if line == "" or line == "\n" or line.startswith("//"):
        return ["-1", "-1", -1]
    # 3. Remove comment at the end of line, if any
    line = line.split("//")[0]
    # 4. Split the line into command and arguments
    line = line.split("\n")[0]
    line = line.split(" ")
    # 5. Determine type of command
    if line[0] == "push":
        command_type = "C_PUSH"
        arg1 = line[1]
        arg2 = line[2]
    elif line[0] == "pop":
        command_type = "C_POP"
        arg1 = line[1]
        arg2 = line[2]
    elif line[0] in ARITHMETIC_COMMANDS + COMPARISON_COMMANDS + LOGICAL_COMMANDS:
        command_type = "C_ARITHMETIC"
        arg1 = line[0]
    # 6. Return [command_type, arg1, arg2]
    return [command_type, arg1, arg2]


class codeWriter:
    file = None
    count = 0

    def __init__(self, filepath):
        self.filepath = filepath
        self.count = 0

    def __enter__(self):
        self.file = open(self.filepath, "w")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.write("// End of file\n")
        self.file.write("(END)\n")
        self.file.write("@END\n")
        self.file.write("0;JMP\n")
        self.file.close()

    def __pop_one(self):
        # Pop to R13
        self.file.write("@SP\n")
        self.file.write("M=M-1\n")
        self.file.write("A=M\n")
        self.file.write("D=M\n")

        self.file.write("@R13\n")
        self.file.write("M=D\n")

    def __pop_two(self):
        self.__pop_one()
        # Pop to R14
        self.file.write("@SP\n")
        self.file.write("M=M-1\n")
        self.file.write("A=M\n")
        self.file.write("D=M\n")

        self.file.write("@R14\n")
        self.file.write("M=D\n")

    def __push_D(self):
        self.file.write("@SP\n")
        self.file.write("A=M\n")
        self.file.write("M=D\n")
        # SP++
        self.file.write("@SP\n")
        self.file.write("M=M+1\n")

    def __true_false_logic(self):
        self.file.write(f"(TRUE{self.count})\n")
        self.file.write("D=-1\n")
        self.file.write(f"@NEXT{self.count}\n")
        self.file.write("0;JMP\n")
        self.file.write(f"(FALSE{self.count})\n")
        self.file.write("D=0\n")
        self.file.write(f"@NEXT{self.count}\n")
        self.file.write("0;JMP\n")
        self.file.write(f"(NEXT{self.count})\n")

    def write_arithmetic(self, command_type, arg1=None):
        self.file.write(f"// {command_type} {arg1} \n")
        if arg1 == ARITHMETIC_COMMANDS[0]:
            self.__pop_two()
            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=D+M\n")
            self.__push_D()

        elif arg1 == ARITHMETIC_COMMANDS[1]:
            self.__pop_two()
            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=M-D\n")
            self.__push_D()

        elif arg1 == ARITHMETIC_COMMANDS[2]:
            self.__pop_one()
            self.file.write("@R13\n")
            self.file.write("D=-M\n")
            self.__push_D()

        elif arg1 == LOGICAL_COMMANDS[0]:
            self.__pop_two()
            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=M&D\n")
            self.__push_D()

        elif arg1 == LOGICAL_COMMANDS[1]:
            self.__pop_two()
            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=M|D\n")
            self.__push_D()

        elif arg1 == LOGICAL_COMMANDS[2]:
            self.__pop_one()
            self.file.write("@R13\n")
            self.file.write("D=!M\n")
            self.__push_D()

        elif arg1 == COMPARISON_COMMANDS[0]:
            self.__pop_two()

            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=M-D\n")

            self.file.write(f"@TRUE{self.count}\n")
            self.file.write("D;JEQ\n")
            self.file.write(f"@FALSE{self.count}\n")
            self.file.write("D;JMP\n")
            self.__true_false_logic()
            self.__push_D()
            self.count += 1

        elif arg1 == COMPARISON_COMMANDS[1]:
            self.__pop_two()

            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=M-D\n")

            self.file.write(f"@TRUE{self.count}\n")
            self.file.write("D;JGT\n")
            self.file.write(f"@FALSE{self.count}\n")
            self.file.write("D;JMP\n")
            self.__true_false_logic()
            self.__push_D()
            self.count += 1

        elif arg1 == COMPARISON_COMMANDS[2]:
            self.__pop_two()

            self.file.write("@R13\n")
            self.file.write("D=M\n")
            self.file.write("@R14\n")
            self.file.write("D=M-D\n")

            self.file.write(f"@TRUE{self.count}\n")
            self.file.write("D;JLT\n")
            self.file.write(f"@FALSE{self.count}\n")
            self.file.write("D;JMP\n")
            self.__true_false_logic()
            self.__push_D()
            self.count += 1

    def write_push_pop(self, command_type, arg1, arg2):
        self.file.write(f"// {command_type} {arg1} {arg2}\n")
        if command_type == COMMAND_TYPES[1]:
            if arg1 not in ["constant", "pointer", "static"]:
                self.file.write("@" + arg2 + "\n")
                self.file.write("D=A\n")
                self.file.write("@" + SEGMENT_MAPPING[arg1] + "\n")
                self.file.write("A=M+D\n")
                self.file.write("D=M\n")
            elif arg1 == "pointer":
                if arg2 == "0":
                    self.file.write("@THIS\n")
                    self.file.write("D=M\n")
                elif arg2 == "1":
                    self.file.write("@THAT\n")
                    self.file.write("D=M\n")
            elif arg1 == "static":
                self.file.write(f"@{16 + int(arg2)}\n")
                self.file.write("D=M\n")
            elif arg1 == "constant":
                self.file.write("@" + arg2 + "\n")
                self.file.write("D=A\n")

            self.file.write("@SP\n")
            self.file.write("A=M\n")
            self.file.write("M=D\n")
            # SP++
            self.file.write("@SP\n")
            self.file.write("M=M+1\n")
        elif command_type == COMMAND_TYPES[2]:
            if arg1 not in ["constant", "pointer", "static"]:
                self.file.write("@" + arg2 + "\n")
                self.file.write("D=A\n")
                self.file.write("@" + SEGMENT_MAPPING[arg1] + "\n")
                self.file.write("D=M+D\n")
            elif arg1 == "pointer":
                if arg2 == "0":
                    self.file.write("@THIS\n")
                    self.file.write("D=A\n")
                elif arg2 == "1":
                    self.file.write("@THAT\n")
                    self.file.write("D=A\n")
            elif arg1 == "static":
                self.file.write(f"@{16 + int(arg2)}\n")
                self.file.write("D=A\n")
            elif arg1 == "constant":
                self.file.write("@" + arg2 + "\n")
                self.file.write("D=A\n")
            self.file.write("@R13\n")
            self.file.write("M=D\n")

            # SP--
            self.file.write("@SP\n")
            self.file.write("M=M-1\n")
            self.file.write("A=M\n")
            self.file.write("D=M\n")

            self.file.write("@R13\n")
            self.file.write("A=M\n")
            self.file.write("M=D\n")


def main():
    file = sys.argv[1]
    VMTranslator(file)


if __name__ == "__main__":
    main()
