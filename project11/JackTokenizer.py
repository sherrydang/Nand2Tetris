import re
import string


class JackTokenizer:

    def __init__(self):
        self.tokens = []
        self.current_index = 0

    def has_more_tokens(self):
        return self.current_index < len(self.tokens)

    def advance(self):
        token = self.tokens[self.current_index]
        self.current_index += 1
        return token

    def current(self):
        return self.tokens[self.current_index]

    def next(self):
        return self.tokens[self.current_index + 1]

    def tokenize(self, file):
        # Open the file
        with open(file, 'r') as infile:
            for line in infile:
                line = line.strip()
                if line == '' or line.startswith('*') or line.startswith('//') or line.startswith('/**'):
                    continue
                # remove comment
                line = line.split('//', 1)[0]

                # Use a regular expression to split the line into words
                # words = re.findall(r"\w+|[^\w\s]", line)
                words = re.findall(r"\w+|\"[^\"]*\"|[^\w\s]", line)

                # replace <, >
                for word in words:
                    self.tokens.append(word)

        # store tokens to file
        # with open("./tokens", 'w') as f:
        #     f.write(str(self.tokens))
        # return

    @staticmethod
    def token_type(token):
        if token in ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
                     'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']:
            return 'KEYWORD'
        elif token in [';', '.', '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>',
                       '=', '~']:
            return 'SYMBOL'
        elif token.isdigit() and 0 <= int(token) <= 32767:
            return 'INT_CONST'
        elif token[0] == '"':
            return 'STRING_CONST'
        elif re.fullmatch(r'^[a-zA-Z]\w*(?![;().,])$', token):
            return 'IDENTIFIER'
        else:
            return 'OTHER'

    @staticmethod
    def keyword(token):
        return token.upper()

    @staticmethod
    def token_xml_tag(token):
        mapping = {
            'KEYWORD': 'keyword',
            'IDENTIFIER': 'identifier',
            'SYMBOL': 'symbol',
            'STRING_CONST': 'stringConstant',
            'INT_CONST': 'integerConstant'
        }
        return mapping.get(token, 'unknown')
