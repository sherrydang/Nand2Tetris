class Parser(object):
    @staticmethod
    def command_type(line):
        return line.split()[0]

    @staticmethod
    def arg1(line):
        try:
            return line.split()[1]
        except IndexError:
            return -1

    @staticmethod
    def arg2(line):
        try:
            return line.split()[2]
        except IndexError:
            return -1
