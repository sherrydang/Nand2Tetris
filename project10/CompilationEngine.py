import re


class CompilationEngine:

    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.output_handle = None

    def open_output_file(self):
        # Open the output file in write mode
        self.output_handle = open(self.output_file, 'w')

    def close_output_file(self):
        # Close the output file
        self.output_handle.close()

    def write_to_output_file(self, text):
        # Write the given text to the output file
        self.output_handle.write(text)

    def process(self, raw_token=None):
        # handle expression
        if raw_token is None:
            self.print_xml_token()
        elif self.tokenizer.current() == raw_token:
            self.print_xml_token()
        else:
            print(self.tokenizer.current() + self.tokenizer.next() + " syntax error")
        self.tokenizer.advance()

    def print_xml_token(self):
        xml_tag = self.tokenizer.token_xml_tag(self.tokenizer.token_type(self.tokenizer.current()))
        token = self.tokenizer.current().strip('"').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        xml_content = f"<{xml_tag}> {token} </{xml_tag}>\n"
        self.output_handle.write(xml_content)
        return

    def compile_class(self):
        # Read tokens from the tokenizer and write output to the output file
        self.open_output_file()
        self.write_to_output_file("<class>\n")
        self.process("class")  # class
        self.process()  # ClassName
        self.process("{")  # {
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current() in ("static", "field"):
                self.compile_class_var_dec()
            elif self.tokenizer.current() in ("function", "constructor", "method"):
                self.compile_subroutine()
            else:
                self.process()

        self.write_to_output_file("</class>\n")
        self.close_output_file()
        self.indent_xml_file(self.output_file)

    def compile_class_var_dec(self):
        self.write_to_output_file("<classVarDec>\n")
        while self.tokenizer.current() != ';':
            self.process()
        self.process()  # process ;
        self.write_to_output_file("</classVarDec>\n")
        return

    def compile_subroutine(self):
        self.write_to_output_file("<subroutineDec>\n")
        while self.tokenizer.current() != '(':
            self.process()  # constructor|function|method type name
        self.process('(')
        self.compile_parameter_list()
        self.process(')')
        self.compile_subroutine_body()
        self.write_to_output_file("</subroutineDec>\n")
        return

    def compile_parameter_list(self):
        self.write_to_output_file("<parameterList>\n")
        while self.tokenizer.current() != ')':
            self.process()
        self.write_to_output_file("</parameterList>\n")
        return

    def compile_subroutine_body(self):
        self.write_to_output_file("<subroutineBody>\n")
        self.process("{")
        while self.tokenizer.current() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.process("}")
        self.write_to_output_file("</subroutineBody>\n")
        return

    def compile_var_dec(self):
        self.write_to_output_file("<varDec>\n")
        while self.tokenizer.current() != ";":
            self.process()
        self.process(";")
        self.write_to_output_file("</varDec>\n")
        return

    def compile_statements(self):
        self.write_to_output_file("<statements>\n")

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

        self.write_to_output_file("</statements>\n")
        return

    def compile_let(self):
        self.write_to_output_file("<letStatement>\n")
        while self.tokenizer.current() != ';':
            # eg. let a = 'expression'
            # eg. let array[expression] = 'expression';
            if self.tokenizer.current() in ('=', '['):
                self.process()
                self.compile_expression()
            else:
                self.process()
        self.process(";")
        self.write_to_output_file("</letStatement>\n")
        return

    def compile_if(self):
        self.write_to_output_file("<ifStatement>\n")
        self.process("if")
        self.process("(")
        self.compile_expression()
        self.process(")")
        self.process("{")
        self.compile_statements()
        self.process("}")
        if self.tokenizer.current() == "else":
            self.compile_else()
        self.write_to_output_file("</ifStatement>\n")
        return

    def compile_else(self):
        self.process("else")
        self.process("{")
        self.compile_statements()
        self.process("}")
        return

    def compile_while(self):
        self.write_to_output_file("<whileStatement>\n")
        self.process("while")
        while self.tokenizer.current() != "{":
            if self.tokenizer.current() == '(':
                self.process()
                self.compile_expression()
            else:
                self.process()
        self.process("{")
        self.compile_statements()
        self.process("}")
        self.write_to_output_file("</whileStatement>\n")
        return

    def compile_do(self):
        self.write_to_output_file("<doStatement>\n")
        while self.tokenizer.current() != ";":
            if self.tokenizer.current() == '(':
                self.process()
                self.compile_expression_list()
            else:
                self.process()
        self.process(";")
        self.write_to_output_file("</doStatement>\n")
        return

    def compile_return(self):
        self.write_to_output_file("<returnStatement>\n")
        self.process("return")
        if self.tokenizer.current() != ";":
            self.compile_expression()
        self.process(";")
        self.write_to_output_file("</returnStatement>\n")
        return

    def compile_expression(self):
        self.write_to_output_file("<expression>\n")
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current() in (')', ';', ']', ','):  # expression terminator
                break
            else:
                if self.tokenizer.current() in ('(', '~'):  # term
                    self.compile_term()
                elif self.tokenizer.token_type(self.tokenizer.current()) == 'SYMBOL':
                    self.process()
                else:
                    self.compile_term()
        self.write_to_output_file("</expression>\n")
        return

    def compile_term(self):
        self.write_to_output_file("<term>\n")

        # (expression)
        if self.tokenizer.current() == '(':
            self.process('(')
            self.compile_expression()
            self.process(')')

        # unaryOp term
        elif self.tokenizer.current() in ('-', '~'):
            self.process()  # process unaryOp
            self.compile_term()  # process term

        # integerConstant | stringConstant | keywordConstant | varName | varName[expression]
        # | subroutineCall
        else:
            self.process()

            # varName[expression]
            if self.tokenizer.current() == '[':
                self.process()
                while self.tokenizer.has_more_tokens():
                    if self.tokenizer.current() == ']':
                        self.process(']')
                        break
                    else:
                        self.compile_expression()

            # subroutineCall
            # varName.methodName(expressionList)
            if self.tokenizer.current() == '.':
                self.process('.')
                self.process()
                self.process('(')
                self.compile_expression_list()
                self.process(')')

        self.write_to_output_file("</term>\n")
        return

    def compile_expression_list(self):
        self.write_to_output_file("<expressionList>\n")
        while self.tokenizer.current() != ')':
            if self.tokenizer.current() == ',':
                self.process(',')
                self.compile_expression()
            else:
                self.compile_expression()
        self.write_to_output_file("</expressionList>\n")
        return

    @staticmethod
    def indent_xml_file(input_file, indent_val="  "):
        # Open the input file in read mode
        with open(input_file, 'r') as f:
            # Read the lines of the file
            lines = f.readlines()

        # Indent each line that starts with a tag
        indented_lines = []
        indent_level = 0  # Current indentation level
        for line in lines:
            # Use a regular expression to match opening and closing tags
            matches = re.finditer(r"</?[^<>]+>", line)
            indented_line = line
            if matches:
                for match in matches:
                    # Check for opening and closing tags
                    tag = match.group()
                    if tag.startswith("</"):  # Closing tag
                        indent_level -= 1  # Decrease indentation level
                        # Indent the line if it contains a tag
                        indented_line = indent_val * indent_level + line
                    elif not tag.startswith("<?"):  # Opening tag (skip processing instructions)
                        # Indent the line if it contains a tag
                        indented_line = indent_val * indent_level + line
                        indent_level += 1  # Increase indentation level
            else:
                # Don't indent the line if it doesn't contain a tag
                indented_line = line
            indented_lines.append(indented_line)

        # Write the indented lines to the output file
        with open(input_file, 'w') as f:
            f.writelines(indented_lines)
