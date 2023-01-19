class VMWriter:
    def __init__(self, file):
        self.f_name = file
        self.f = open(self.f_name, 'w')
        self.f.truncate(0)

    def write(self, text):
        self.f = open(self.f_name, 'a')
        self.f.write(text)
        self.f.close()

    def write_push(self, segment, index):
        text = 'push ' + segment + ' ' + str(index) + '\n'
        self.write(text)
        return

    def write_pop(self, segment, index):
        text = 'pop ' + segment + ' ' + str(index) + '\n'
        self.write(text)
        return

    def write_arithmetic(self, command):
        if command == '+':
            self.write('add\n')
        elif command == '-':
            self.write('sub\n')
        elif command == '*':
            self.write('call Math.multiply 2\n')
        elif command == '/':
            self.write('call Math.divide 2\n')
        elif command == '&':
            self.write('and\n')
        elif command == '|':
            self.write('or\n')
        elif command == '<':
            self.write('lt\n')
        elif command == '>':
            self.write('gt\n')
        elif command == '=':
            self.write('eq\n')
        return

    def write_unary(self, unary_op):
        if unary_op == '-':
            self.write('neg\n')
        elif unary_op == '~':
            self.write('not\n')

    def write_label(self, label):
        self.write('label ' + label + '\n')
        return

    def write_if(self, label):
        self.write('if-goto ' + label + '\n')
        return

    def write_goto(self, label):
        self.write('goto ' + label + '\n')
        return

    def write_call(self, name, n_args):
        text = 'call ' + name + ' ' + str(n_args) + '\n'
        self.write(text)
        return

    def write_function(self, name):
        text = name + '\n'
        self.write(text)
        return

    def write_return(self):
        self.write('return\n')
        return

    def close(self):
        return
