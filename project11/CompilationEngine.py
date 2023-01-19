import re

import SymbolTable
import VMWriter


class CompilationEngine:

    def __init__(self, tokenizer, output_file):
        self.class_name = None
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.vm_writer = VMWriter.VMWriter(output_file)
        self.class_symbols = SymbolTable.SymbolTable()
        self.subroutine_symbols = SymbolTable.SymbolTable()
        self.subroutine_symbols = SymbolTable.SymbolTable()
        self.ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        self.if_level = 0
        self.while_level = 0
        self.methods = {}
        self.method_list()

    def method_list(self):
        for i in range(len(self.tokenizer.tokens)):
            if self.tokenizer.tokens[i] == "method":
                self.methods[self.tokenizer.tokens[i + 2]] = 0
        return

    def process(self, raw_token=None):
        # handle expression
        if raw_token is None:
            self.tokenizer.advance()
        elif self.tokenizer.current() == raw_token:
            self.tokenizer.advance()
        else:
            print(self.tokenizer.current() + self.tokenizer.next() + " syntax error")
            self.tokenizer.advance()

    def compile_class(self):
        self.process('class')
        self.class_name = self.tokenizer.current()
        self.process()
        self.process('{')
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current() in ("static", "field", "arg", "var"):
                self.compile_class_var_dec()
            elif self.tokenizer.current() in ("constructor", "function", "method"):
                self.compile_subroutine_dec()
            else:
                self.process()
        return

    def compile_class_var_dec(self):
        # e.g var int value
        kind = self.tokenizer.current()
        self.process()
        _type = self.tokenizer.current()
        self.process()
        name = self.tokenizer.current()
        self.process()
        self.class_symbols.define(name, _type, kind)
        while self.tokenizer.current() == ',':
            self.process(',')
            name = self.tokenizer.current()
            self.process()
            self.class_symbols.define(name, _type, kind)
        self.process(';')
        return

    def compile_subroutine_dec(self):
        if self.tokenizer.current() == "constructor":
            self.compile_constructor()
            return
        elif self.tokenizer.current() == "function":
            self.compile_function()
            return
        elif self.tokenizer.current() == "method":
            self.compile_method()
            return
        return

    def compile_constructor(self):
        # reset subroutine symbol table
        self.subroutine_symbols.reset()
        self.process()  # function
        self.process()  # void
        func_name = self.tokenizer.current()  # function_name
        self.process()
        self.process('(')
        self.compile_parameter_list()
        # initialize jump level
        self.while_level = 0
        self.if_level = 0
        self.process(')')
        pattern = 'function ' + self.class_name + '.' + func_name
        self.vm_writer.write_function(pattern)
        # ** push constant args_count
        attributes = self.class_symbols.var_count('field')
        self.vm_writer.write_push('constant', attributes)
        # ** call Memory.alloc
        self.vm_writer.write_call('Memory.alloc', 1)
        # pop pointer 0 -> set this
        self.vm_writer.write_pop('pointer', 0)
        self.compile_subroutine_body()
        # set params count
        self.set_function_params_count(pattern)

        return

    def compile_method(self):
        # reset subroutine symbol table
        self.subroutine_symbols.reset()
        self.process()  # function
        self.process()  # void
        func_name = self.tokenizer.current()  # function_name
        self.process()
        self.process('(')
        self.subroutine_symbols.define('this', 'field', 'argument')  # dummy argument refer to this
        self.compile_parameter_list()
        # initialize jump level
        self.while_level = 0
        self.if_level = 0
        self.process(')')
        pattern = 'function ' + self.class_name + '.' + func_name
        self.vm_writer.write_function(pattern)
        # ** load this
        self.vm_writer.write_push('argument', 0)
        self.vm_writer.write_pop('pointer', 0)
        self.compile_subroutine_body()
        # set params count
        self.set_function_params_count(pattern)

        return

    # subroutine declaration
    def compile_function(self):
        # reset subroutine symbol table
        self.subroutine_symbols.reset()
        self.process()  # function
        self.process()  # void
        func_name = self.tokenizer.current()  # function_name
        self.process()
        self.process('(')
        self.compile_parameter_list()
        # initialize jump level
        self.while_level = 0
        self.if_level = 0
        self.process(')')
        pattern = 'function ' + self.class_name + '.' + func_name
        self.vm_writer.write_function(pattern)
        self.compile_subroutine_body()
        # set params count
        self.set_function_params_count(pattern)

        return

    # backtracking the function variable count
    def set_function_params_count(self, pattern):
        with open(self.output_file, "r") as f:
            content = f.read()

        new_line = pattern + ' ' + str(self.subroutine_symbols.var_count('local'))
        content = re.sub(pattern, new_line, content)

        with open(self.output_file, "w") as f:
            f.write(content)

    def compile_subroutine_call(self):

        # If the called subroutine is void
        # Just after the call, the generated VM code call gets rid of the return value using the
        # command pop temp 0
        subroutine_name = ''
        while self.tokenizer.current() != '(':
            subroutine_name += self.tokenizer.current()
            self.process()

        self.process('(')
        self.compile_parameter_list()
        self.process(')')

        # The generated VM code ends with push constant 0 and then return
        self.vm_writer.write_push('constant', '0')
        self.vm_writer.write_return()
        return

    def compile_parameter_list(self):
        count = 0
        while self.tokenizer.current() != ')':
            if self.tokenizer.current() == ',':
                self.process()
                continue
            _type = self.tokenizer.current()
            self.process()
            name = self.tokenizer.current()
            self.process()
            self.subroutine_symbols.define(name, _type, 'argument')
            count += 1
        return count

    def compile_subroutine_body(self):
        self.process("{")
        while self.tokenizer.current() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.process("}")
        return

    def compile_var_dec(self):
        # e.g var int value
        kind = ''
        if self.tokenizer.current() == 'var':
            kind = 'local'
        self.process()
        _type = self.tokenizer.current()
        self.process()
        name = self.tokenizer.current()
        self.process()
        self.subroutine_symbols.define(name, _type, kind)
        while self.tokenizer.current() == ',':
            self.process(',')
            name = self.tokenizer.current()
            self.process()
            self.subroutine_symbols.define(name, _type, kind)
        self.process(';')
        return

    def compile_statements(self):

        while self.tokenizer.current() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.current() == "let":
                self.compile_let()
            if self.tokenizer.current() == "if":
                self.compile_if()
            if self.tokenizer.current() == "while":
                self.compile_while()
            if self.tokenizer.current() == "do":
                self.compile_do()
            if self.tokenizer.current() == "return":
                self.compile_return()

        return

    def compile_let(self):
        self.process('let')
        var_name = self.tokenizer.current()
        self.process()  # varName
        # let varName[expression1] = expression2;
        if self.tokenizer.current() == '[':
            # arr[x]
            segment = ''
            index = 0
            if var_name in self.subroutine_symbols.table:
                segment = self.subroutine_symbols.kind_of(var_name)
                index = self.subroutine_symbols.index_of(var_name)
            elif var_name in self.class_symbols.table:
                segment = self.class_symbols.kind_of(var_name)
                index = self.class_symbols.index_of(var_name)
            self.process('[')
            self.compile_expression()  # call compileExpression to compute and push expression1
            self.process(']')
            self.vm_writer.write_push(segment, index)  # push arr
            self.vm_writer.write('add\n')  # top stack value = address of arr[expression1]
            self.process('=')
            self.compile_expression()  # call compileExpression to compute and push expression2
            self.vm_writer.write_pop('temp', 0)  # temp 0 = the value of expression2
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        # let varName = expression;
        elif self.tokenizer.current() == '=':
            self.process('=')
            self.compile_expression()
            segment = ''
            index = 0
            if var_name in self.subroutine_symbols.table:
                segment = self.subroutine_symbols.kind_of(var_name)
                index = self.subroutine_symbols.index_of(var_name)
            elif var_name in self.class_symbols.table:
                segment = self.class_symbols.kind_of(var_name)
                index = self.class_symbols.index_of(var_name)
            if segment == 'field':
                segment = 'this'
            self.vm_writer.write_pop(segment, index)
        self.process(";")
        return

    def compile_if(self):
        self.process("if")
        self.process('(')
        self.compile_expression()
        self.process(')')
        label_1 = 'IF_TRUE' + str(self.if_level)
        label_2 = 'IF_FALSE' + str(self.if_level)
        label_end = 'IF_END' + str(self.if_level)
        self.if_level += 1
        self.vm_writer.write_if(label_1)
        self.vm_writer.write_goto(label_2)
        # if true, go to label 1
        self.vm_writer.write_label(label_1)
        self.process('{')
        self.compile_statements()
        self.process('}')
        # if false, go to else, label 2
        if self.tokenizer.current() == 'else':
            self.vm_writer.write_goto(label_end)  # end tag for if true
            self.process('else')
            # label 2
            self.vm_writer.write_label(label_2)
            self.process('{')
            self.compile_statements()
            self.process('}')
            self.vm_writer.write_label(label_end)
        # no else
        else:
            self.vm_writer.write_label(label_2)
        return

    def compile_while(self):
        self.process("while")
        label_1 = 'WHILE_EXP' + str(self.while_level)
        label_end = 'WHILE_END' + str(self.while_level)
        self.while_level += 1
        self.vm_writer.write_label(label_1)
        self.process('(')
        self.compile_expression()
        self.process(')')
        self.vm_writer.write('not\n')
        self.vm_writer.write_if(label_end)
        self.process('{')
        self.compile_statements()
        self.process('}')
        self.vm_writer.write_goto(label_1)  # loop again
        self.vm_writer.write_label(label_end)  # end loop
        return

    def compile_do(self):
        self.process("do")
        self.compile_expression()
        self.vm_writer.write_pop('temp', 0)
        self.process(";")
        return

    def compile_return(self):
        self.process("return")
        # return null
        if self.tokenizer.current() == ";":
            self.vm_writer.write_push('constant', 0)
            self.vm_writer.write_return()
        else:
            self.compile_expression()
            self.vm_writer.write_return()
        self.process(";")
        return

    def compile_expression(self):
        self.compile_term()  # term only

        # term (op term) *
        op = self.tokenizer.current()
        if op in self.ops:
            self.process()
            self.compile_term()  # term2
            self.vm_writer.write_arithmetic(op)  # op
        return

    def compile_term(self):
        token_type = self.tokenizer.token_type(self.tokenizer.current())

        # if the term is a constant
        if token_type == 'INT_CONST':
            self.vm_writer.write_push('constant', self.tokenizer.current())
            self.process()

        # if the term is a string
        elif token_type == 'STRING_CONST':
            string = self.tokenizer.current()
            string = string[1:-1]  # get rid of double quote
            self.vm_writer.write_push('constant', len(string))
            self.vm_writer.write_call('String.new', 1)
            for char in string:
                code = ord(char)
                self.vm_writer.write_push('constant', code)
                self.vm_writer.write_call('String.appendChar', 2)
            self.process()

        # if the term is other constant: true, false, null, this...
        elif self.tokenizer.current() == 'true':
            self.vm_writer.write_push('constant', 0)
            self.vm_writer.write('not\n')
            self.process()

        elif self.tokenizer.current() == 'false':
            self.vm_writer.write_push('constant', 0)
            self.process()

        elif self.tokenizer.current() == 'null':
            self.vm_writer.write_push('constant', 0)
            self.process()

        elif self.tokenizer.current() == 'this':
            self.vm_writer.write_push('pointer', 0)
            self.process()

        # if term is array[index]
        elif self.tokenizer.next() == '[':
            var_name = self.tokenizer.current()
            self.process()
            segment = ''
            index = 0
            if var_name in self.subroutine_symbols.table:
                segment = self.subroutine_symbols.kind_of(var_name)
                index = self.subroutine_symbols.index_of(var_name)
            elif var_name in self.class_symbols.table:
                segment = self.class_symbols.kind_of(var_name)
                index = self.class_symbols.index_of(var_name)
            self.process('[')
            self.compile_expression()
            self.process(']')
            self.vm_writer.write_push(segment, index)  # push arr
            self.vm_writer.write('add\n')  # add
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('that', 0)

        # if term is a non-object variable
        elif self.tokenizer.current() in self.subroutine_symbols.table and self.tokenizer.next() != '.':
            var_name = self.tokenizer.current()
            kind = self.subroutine_symbols.kind_of(var_name)
            if kind == 'field':
                kind = 'this'
            index = self.subroutine_symbols.index_of(var_name)
            self.vm_writer.write_push(kind, index)
            self.process()

        # if term is a class-level non-object variable
        elif self.tokenizer.current() in self.class_symbols.table and self.tokenizer.next() != '.':
            var_name = self.tokenizer.current()
            kind = self.class_symbols.kind_of(var_name)
            if kind == 'field':
                kind = 'this'
            index = self.class_symbols.index_of(var_name)
            self.vm_writer.write_push(kind, index)
            self.process()

        # if term is unaryOp term
        elif self.tokenizer.current() in ('~', '-'):
            unary_op = self.tokenizer.current()
            self.process()
            self.compile_term()
            self.vm_writer.write_unary(unary_op)

        # (exp)
        elif self.tokenizer.current() == '(':
            self.process('(')
            self.compile_expression()
            self.process(')')

        # call method | constructor: obj.subName(exp1, exp2...expn)
        elif self.tokenizer.next() == '.':
            table_name = None
            obj_name = self.tokenizer.current()
            self.process()
            self.process('.')
            func_name = self.tokenizer.current()
            self.process()
            obj_type = None

            if obj_name in self.class_symbols.table:
                obj_type = self.class_symbols.type_of(obj_name)
                table_name = 'class_symbols'

            if obj_name in self.subroutine_symbols.table:
                obj_type = self.subroutine_symbols.type_of(obj_name)
                table_name = 'subroutine_symbols'

            call_text = ''

            # 1. method call - obj type
            if obj_type:
                call_text += obj_type
                segment = ''
                var_index = 0
                if table_name == 'class_symbols':
                    segment = self.class_symbols.kind_of(obj_name)
                    var_index = self.class_symbols.index_of(obj_name)
                elif table_name == 'subroutine_symbols':
                    segment = self.subroutine_symbols.kind_of(obj_name)
                    var_index = self.subroutine_symbols.index_of(obj_name)
                if segment == 'field':
                    segment = 'this'
                self.vm_writer.write_push(segment, var_index)

            # 2. constructor call
            else:
                call_text = obj_name

            # obj.subName
            call_text += '.'
            call_text += func_name

            # process expression
            self.process('(')
            var_count = self.compile_expression_list()
            self.process(')')

            if obj_type:
                var_count += 1

            # write method call
            self.vm_writer.write_call(call_text, var_count)

        # f(exp1...expn)
        # e.g draw()
        elif self.tokenizer.next() == '(':
            func_name = self.tokenizer.current()
            self.process()

            # process expression
            self.process('(')
            var_count = 0

            # call method
            if func_name in self.methods:
                self.vm_writer.write_push('pointer', 0)
                var_count += 1

            var_count += self.compile_expression_list()
            func_name = self.class_name + '.' + func_name
            self.vm_writer.write_call(func_name, var_count)
            self.process(')')

        else:
            raise ValueError("Invalid term:", self.tokenizer.current())

    def compile_expression_list(self):
        exp_count = 0
        while self.tokenizer.current() != ')':
            if self.tokenizer.current() == ',':
                self.process(',')
                self.compile_expression()
            else:
                self.compile_expression()
            exp_count += 1
        return exp_count
