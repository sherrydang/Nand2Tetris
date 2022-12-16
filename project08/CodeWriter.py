class CodeWriter:
    # Declare an instance variable
    def __init__(self):
        self.myFile = None

    # Declare an instance variable
    @property
    def my_file(self):
        return self.my_file

    @my_file.setter
    def my_file(self, value):
        self.my_file = value


def write_arithmetic(c_type, func_nr):
    line = ""
    # write add

    if c_type == "add":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M // get a
A=A-1
D=D+M
M=D // b = a + b
'''
    if c_type == "sub":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M //y = RAM[SP-1]
A=A-1 //x = RAM[SP-2]
D=M-D //
M=D // b = a - b
'''
    if c_type == "neg":
        line = '''
@SP
A=M-1 //x = RAM[SP-1]
M=-M //neg x
        '''

    if c_type == "eq":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M //y = RAM[SP-1]
A=A-1 //x = RAM[SP-2] 
D=M-D //RAM[SP-2] = x - y
@EQ{}
D;JEQ
@SP // not equal
A=M-1
M=0
@END{}
0;JMP
(EQ{})
@SP
A=M-1
M=-1
(END{})
'''.format(func_nr, func_nr, func_nr, func_nr)

    if c_type == "gt":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M //y = RAM[SP-1]
A=A-1 //x = RAM[SP-2] 
D=M-D //RAM[SP-2] = x - y
@GT{}
D;JGT
@SP // not great than
A=M-1
M=0
@END{}
0;JMP
(GT{})
@SP
A=M-1
M=-1
(END{})
'''.format(func_nr, func_nr, func_nr, func_nr)

    if c_type == "lt":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M //y = RAM[SP-1]
A=A-1 //x = RAM[SP-2] 
D=M-D //RAM[SP-2] = x - y
@LT{}
D;JLT
@SP // lt = false
A=M-1
M=0
@END{}
0;JMP
(LT{})
@SP
A=M-1
M=1 // lt = true
(END{})
'''.format(func_nr, func_nr, func_nr, func_nr)

    if c_type == "and":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M //y = RAM[SP-1]
A=A-1 //x = RAM[SP-2] 
D=D&M //x and y
M=D //write to RAM[SP-2]
'''

    if c_type == "or":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M //y = RAM[SP-1]
A=A-1 //x = RAM[SP-2] 
D=D|M //x or y
M=D //write to RAM[SP-2]
'''.format(func_nr)

    if c_type == "not":
        line = '''
@SP
A=M-1 //x = RAM[SP-1]
M=!M //not x
'''

    return line


def write_push_pop(cmd_type, arg1, arg2):
    func_type = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "temp": "5"
    }

    line = ""

    # push {local|argument|this|that} i
    if arg1 in ("local", "argument", "this", "that") and cmd_type == "push":
        line = '''
@{}
D=A
@{} // base address: LCL,ARG,THIS,THAT
A=M+D // addr = base + i
D=M
@SP
A=M
M=D //RAM[SP] = RAM[addr]
@SP
M=M+1
'''.format(arg2, func_type.get(arg1))

    # push constant i
    if arg1 == "constant" and cmd_type == "push":
        line = '''
@{}
D=A
@SP
A=M
M=D
@SP
M = M + 1
'''.format(arg2)

    # push static
    if arg1 == "static" and cmd_type == "push":
        line = '''
@{}.Foo.{}
D=M
@SP
A=M
M=D   
@SP   
M=M+1
'''.format(CodeWriter.my_file, arg2)

    # push temp
    if arg1 == "temp" and cmd_type == "push":
        line = '''
@5
D=A
@{}
A=D+A // addr = 5 + i
D=M
@SP
A=M
M=D
@SP
M=M+1
'''.format(arg2)

    # push pointer
    if arg1 == "pointer" and cmd_type == "push":
        pointer = ""
        if arg2 == "0":
            pointer = "THIS"
        if arg2 == "1":
            pointer = "THAT"
        line = '''
@{}
D=M
@SP
A=M
M=D
@SP
M=M+1
'''.format(pointer)

    # pop {local|argument|this|that} i
    if arg1 in ("local", "argument", "this", "that", "temp") and cmd_type == "pop":
        line = '''
@{}
D=M
@{}
D=D+A // addr = LCL|ARG|THIS|THAT + i          
@R13
M=D // save addr
@SP
M=M-1// SP--
A=M
D=M // D=RAM[SP]
@R13
A=M
M=D // RAM[addr] = RAM[SP]        
'''.format(func_type.get(arg1), arg2)

    # pop temp i
    if arg1 == "temp" and cmd_type == "pop":
        line = '''
@{}
D=A
@{}
D=D+A // addr = 5 + i          
@R13
M=D // save addr
@SP
M=M-1// SP--
A=M
D=M // D=RAM[SP]
@R13
A=M
M=D // RAM[addr] = RAM[SP]        
'''.format(func_type.get(arg1), arg2)

    # pop static
    if arg1 == "static" and cmd_type == "pop":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M // D = stack.pop
@{}.Foo.{}
M=D
'''.format(CodeWriter.my_file, arg2)

    # pop pointer 0/1
    if arg1 == "pointer" and cmd_type == "pop":
        pointer = ""
        if arg2 == "0":
            pointer = "THIS"
        if arg2 == "1":
            pointer = "THAT"
        line = '''
@SP
M=M-1
A=M
D=M
@{}
M=D
'''.format(pointer)

    return line


def write_label(arg1):
    line = "\n(" + arg1 + ")\n"
    return line


def write_goto(arg1):
    line = "\n@" + arg1 + "\n"
    line += "0;JMP\n"
    return line


def write_if_goto(arg1):
    # let cond = stack.pop()
    # if cond jump to execute the cmd just after label
    # else execute the next command
    line = '''
@SP
M=M-1// SP--
A=M
D=M // D = stack.pop()
@{}
D;JGT
'''.format(arg1)
    return line


def write_call(arg1, arg2, ret_nr):
    # push retAddrLabel
    lines = '''
// push retAddrLabel
@{}.$RET{}
D=A
@SP
A=M
M=D 
@SP
M=M+1
    '''.format(arg1, ret_nr)

    # save the caller's LCL/ARG/THIS/THAT
    for tag in ("LCL", "ARG", "THIS", "THAT"):
        lines += '''
// push {}
@{}
D=M
@SP
A=M
M=D 
@SP
M=M+1
    '''.format(tag, tag)

    # repositions ARG
    lines += '''
// ARG = SP -5 - nArgs
@5
D=A
@SP
D=M-D
@R13
M=D
@{}
D=A
@R13
D=M-D 
@ARG
M=D
'''.format(arg2)

    # repositions LCL
    lines += '''
// repositions LCL
@SP
D=M
@LCL
M=D
'''
    # transfers control to the callee
    lines += write_goto(arg1)

    # injects this label into the code
    lines += '''
({}.$RET{})
'''.format(arg1, ret_nr)

    return lines


# handling function
def write_function(arg1, arg2):
    lines = ""

    # function's entry point (label)
    lines += '''
({})
    '''.format(arg1)

    # initializes nVars local variables
    for i in range(0, int(arg2)):
        lines += write_push_pop("push", "constant", 0)

    return lines


# handling return
def write_return(ret_nr):
    lines = ""

    # gets the address at the frames' end
    lines += '''
// endFrame = LCL
@LCL
D=M
@END_FRAME
M=D
    '''

    # to avoid return_addr get overwrite when argument list is empty, save the return_addr temporarily at R15
    # goto retAddr // jumps to the return address
    lines += '''
// retrieve return address
@5
D=A
@END_FRAME
A=M-D
D=M
@RET_ADDR
M=D
'''.format(ret_nr)

    # *ARG = pop() // puts the return value for the caller
    lines += '''
// put back return value to caller's stack: *ARG = pop()'''
    lines += write_push_pop("pop", "argument", 0)

    # SP = ARG + 1 // repositions SP
    lines += '''
// repositions SP = ARG + 1
@ARG
D=M+1
@SP
M=D 
'''

    lines += '''
// restores THAT = *(endFrame - 1)
@END_FRAME
A=M-1
D=M
@THAT
M=D
'''

    # restores THIS = *(endFrame - 2)

    lines += '''
// restores THIS = *(endFrame - 2) 
@2
D=A
@END_FRAME
A=M-D
D=M
@THIS
M=D  
'''

    # restores ARG = *(endFrame - 3)
    lines += '''
// restores ARG = *(endFrame - 3)
@3
D=A
@END_FRAME
A=M-D
D=M
@ARG
M=D
'''

    # LCL = *(endFrame - 4) // restores LCL
    lines += '''
// restore LCL = *(endFrame - 4)
@4
D=A
@END_FRAME
A=M-D
D=M
@LCL
M=D
'''

    # goto retAddr // jumps to the return address
    lines += '''
// retrieve return address
@RET_ADDR
A=M
0;JMP
'''.format(ret_nr)

    return lines


def write_push_pop_static(cmd_type, arg1, arg2, file):
    line = ""
    # push static
    if arg1 == "static" and cmd_type == "push":
        line = '''
@{}.Foo.{}
D=M
@SP
A=M
M=D   
@SP   
M=M+1
'''.format(file, arg2)

    # pop static
    if arg1 == "static" and cmd_type == "pop":
        line = '''
@SP
M=M-1 //sp--
A=M
D=M // D = stack.pop
@{}.Foo.{}
M=D
'''.format(file, arg2)
    return line


def write_init():
    lines = '''
@Sys.init
0;JMP
'''
    return lines
