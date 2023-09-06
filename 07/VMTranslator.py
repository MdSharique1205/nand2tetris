import sys


class VMTranslator:

    outfile = None

    def __init__(self, filepath):
        print(filepath)
        
        # Setting outfile
        filepath = file.split('/')
        filename = filepath[-1]
        filename = filename.split('.')[0]
        outfile = filename + '.asm'
        filepath[-1] = outfile
        self.outfile = '/'.join(filepath)
    
    def logical_handler(self, line):
        #1. Get the top two elements 
        #2. Setup these two elements for opertaion
        #3. Fetch which operation needs to be performed
        #4. Perform the operation
        #5. Push the result into stack
        
def parser():
    pass


def codewriter():
    pass


def main():
    file = sys.argv[1]
    # eg. file = a/b/cde.vm
    #
    # with open(file) as input_file:
    #     lines = input_file.readlines()
    #     for line in lines:
    #         # 1. Cleaning
    #         # 2. Logical or Memory
    #         # 3. For Logical -> pop last 2, push operation
    #         # 4. For Memory --> Manipulate stack
    #         
    #         # 1. Cleaning
    #         if line.startswith('//'):
    #             continue
    #         line = '  Helo  a    WOrld fsdf few'
    #         print('// ' + line)
    #         
    #         # line = ' '.join(line.split())
    #         line = line.split()
    #         logical = True if len(line) is 1 else False
    #         print(' '.join(line))
    #          
    #         if logical:
    #                  
    VMTranslator(file)
            
if __name__ == "__main__":
    main()
