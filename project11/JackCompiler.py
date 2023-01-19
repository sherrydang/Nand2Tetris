import glob
import os
import sys

import CompilationEngine
import JackTokenizer

if len(sys.argv) != 2:
    print("Usage: JackAnalyzer file.jack")
else:
    file = sys.argv[1]

    # handle single file
    if file.endswith('.jack'):
        tokenizer = JackTokenizer.JackTokenizer()
        tokenizer.tokenize(file)
        # output to .vm
        path_name, ext = os.path.splitext(file)
        outfile_name = path_name + '.vm'
        engine = CompilationEngine.CompilationEngine(tokenizer, outfile_name)
        engine.compile_class()
    # handle folder
    else:
        # Get a list of all the .jack files in the folder
        jack_files = glob.glob(file + '**/*.jack', recursive=True)

        # Iterate over the list of .jack files
        for file in jack_files:
            tokenizer = JackTokenizer.JackTokenizer()
            tokenizer.tokenize(file)
            # output to .xml
            path_name, ext = os.path.splitext(file)
            outfile_name = path_name + '.vm'
            engine = CompilationEngine.CompilationEngine(tokenizer, outfile_name)
            engine.compile_class()
