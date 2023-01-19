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
M=-1 // lt = true
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
@Foo.{}
D=M
@SP
A=M
M=D   
@SP   
M=M+1
'''.format(arg2)

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
@Foo.{}
M=D
'''.format(arg2)

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
