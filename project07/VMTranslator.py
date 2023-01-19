import sys
import CodeWriter
import Parser


class VMTranslator(object):
    def __init__(self):
        self.parser = Parser.Parser()
        self.coder = CodeWriter

    def translate(self, filename):

        src_file = open(filename, 'r')
        spf_name = filename.split('.')[0]
        tar_file = open(spf_name + '.asm', 'w')

        func_nr = 1
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
                if cmd_type == "push" or cmd_type == "pop":
                    w_line = self.coder.write_push_pop(cmd_type, arg1, arg2)

                # Arithmetic command
                elif cmd_type in ("add", "sub", "neg", "or", "eq", "gt", "lt", "and", "or", "not"):
                    func_nr += 1
                    w_line = self.coder.write_arithmetic(cmd_type, func_nr)

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
    translator.translate(f_name)
