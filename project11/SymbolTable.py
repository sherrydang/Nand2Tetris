class SymbolTable:
    def __init__(self):
        self.table = {}
        self.index = {'static': 0, 'field': 0, 'argument': 0, 'local': 0}

    # empty the symbol table
    def reset(self):
        self.table = {}
        self.index = {'static': 0, 'field': 0, 'argument': 0, 'local': 0}

    # add to table a new variable of given name, type and kind
    # assign to it the index value of that kind, and adds 1 to the index
    def define(self, name, _type, kind):
        self.table[name] = {"type": _type, "kind": kind, "index": self.index[kind]}
        self.index[kind] += 1
        return

    # return the number of variables of given kind already defined in the table
    def var_count(self, kind):
        count = 0
        for symbol in self.table.values():
            if symbol["kind"] == kind:
                count += 1
        return count

    def total_count(self):
        return len(self.table)

    # return the kind of the named identifier, if the identifier not found, return None
    def kind_of(self, name):
        symbol = self.table.get(name)
        if symbol:
            return symbol["kind"]
        return None

    # return the type of the named variable
    def type_of(self, name):
        symbol = self.table.get(name)
        if symbol:
            return symbol["type"]
        return None

    # return the index of the named variable
    def index_of(self, name):
        symbol = self.table.get(name)
        if symbol:
            return symbol["index"]
        return None
