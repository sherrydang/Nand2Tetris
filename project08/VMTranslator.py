import sys
import glob
import CodeWriter
import Parser
import os


class VMTranslator(object):
    def __init__(self):
        self.parser = Parser.Parser()
        self.coder = CodeWriter

    def translate(self, filename):

        src_file = open(filename, 'r')
        spf_name = filename.split('.')[0]
        tar_file = open(spf_name + '.asm', 'w')
        spf_name = spf_name.split('/')[1]

        func_nr = 1
        ret_nr = 1
        for line in src_file:
            # remove comment
            line = line.rsplit('//')[0]
            # remove empty line
            line = line.strip()
            w_line = ""

            # skip empty line
            if line:
                cmd_type = self.parser.command_type(line)
                arg1 = self.parser.arg1(line)
                arg2 = self.parser.arg2(line)

                # Push Pop command
                if (cmd_type == "push" or cmd_type == "pop") and arg1 == "static":
                    w_line = self.coder.write_push_pop_static(cmd_type, arg1, arg2,
                                                              spf_name)

                elif cmd_type == "push" or cmd_type == "pop":
                    # self.stack.append(arg1)
                    w_line = self.coder.write_push_pop(cmd_type, arg1, arg2)

                # Arithmetic command
                elif cmd_type in ("add", "sub", "neg", "or", "eq", "gt", "lt", "and", "or", "not"):
                    func_nr += 1
                    w_line = self.coder.write_arithmetic(cmd_type, func_nr)

                elif cmd_type == "label":
                    w_line = self.coder.write_label(arg1)

                elif cmd_type == "goto":
                    w_line = self.coder.write_goto(arg1)

                elif cmd_type == "if-goto":
                    w_line = self.coder.write_if_goto(arg1)

                elif cmd_type == "call":
                    w_line = self.coder.write_call(arg1, arg2, ret_nr)
                    ret_nr += 1

                elif cmd_type == "function":
                    if arg1 == "Sys.init":
                        w_line = self.coder.write_init()
                    else:
                        w_line = self.coder.write_function(arg1, arg2)

                elif cmd_type == "return":
                    w_line = self.coder.write_return(ret_nr)
                    ret_nr += 1

                tar_file.write("//" + line)
                tar_file.write(w_line + "\n")

        src_file.close()
        tar_file.close()


if len(sys.argv) != 2:
    print("Usage: VMTranslator file.vm")
else:
    f_name = sys.argv[1]
    translator = VMTranslator()

    # handle single file
    if f_name.endswith('.vm'):
        translator.translate(f_name)

    # handle folder
    else:
        final_asm_file = f_name + '/' + f_name + '.asm'

        # remove existing asm, create from new
        if os.path.exists(final_asm_file):
            os.remove(final_asm_file)

        # Get a list of all the .vm files in the folder
        vm_files = glob.glob(f_name + '/*.vm')

        # Iterate over the list of .vm files
        for file in vm_files:
            translator.translate(file)

        # rename the main file
        os.rename(f_name + '/Sys.asm', final_asm_file)

        # concatenate all files
        with open(final_asm_file, "a") as file1:
            asm_files = glob.glob(f_name + '/*.asm')
            for file in asm_files:
                if file != final_asm_file:
                    with open(file, "r") as file2:
                        # Read the contents of file2.txt
                        contents = file2.read()
                        # Write the contents of file2.txt to file1.txt
                        file1.write(contents)
                        file2.close()
            file1.close()


