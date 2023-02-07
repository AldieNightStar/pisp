from pisp_api.lex import lex
from pisp_api.parser import parse
from pisp_api.compiler import compile as _compile

import os
import io

def compile_src(src):
    tokens = lex(src)
    operations = parse(tokens)
    return _compile(operations)

def compile(filenames):
    for filename in filenames:
        with io.open(filename, encoding="utf-8") as file_in:
            with io.open(noext(filename)+".py", encoding="utf-8", mode='w') as file_out:
                file_out.write(compile_src(file_in.read()))

def noext(filename):
    return os.path.splitext(filename)[0]

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: pisp.py file.lsp file2.lsp file3.lsp")
    else:
        compile(args)
        print("OK")