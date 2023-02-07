from pisp_api.lex import TOKEN_TYPE_FLOAT, TOKEN_TYPE_NUM, TOKEN_TYPE_PAR, TOKEN_TYPE_STR, TOKEN_TYPE_VAR
from dataclasses import dataclass

@dataclass
class Call:
    name: str
    args: list[any]
    size: int

@dataclass
class Var:
    name: str

@dataclass
class Data:
    value: any

def parse(toks):
    pos = 0
    arr = []
    while pos < len(toks):
        toksX = toks[pos:]
        op = _parse_one(toksX)
        if op == None: raise Exception("Unknown operation found: " + str(toksX[0]))
        pos += (op.size if type(op) is Call else 1)
        arr.append(op)
    return arr

def _parse_one(toks):
    call = _call(toks)
    if call != None: return call
    firstTok = toks[0]
    if firstTok.type == TOKEN_TYPE_NUM: return Data(firstTok.value)
    if firstTok.type == TOKEN_TYPE_STR: return Data(firstTok.value)
    if firstTok.type == TOKEN_TYPE_FLOAT: return Data(firstTok.value)
    if firstTok.type == TOKEN_TYPE_VAR: return Var(firstTok.value)
    

def _call(toks):
    if len(toks) < 3: return None
    if not _is_open_par(toks[0]): return None
    if toks[1].type != TOKEN_TYPE_VAR: raise Exception(f"Call name for token should be of type VAR: {toks[1]}")
    pos = 2
    args = []
    isClosed = False
    while pos < len(toks):
        toksX = toks[pos:]
        if _is_closed_par(toksX[0]):
            # Mark operation as closed
            isClosed = True
            break
        op = _parse_one(toksX)
        if op == None: raise Exception("During argument parsing inside Call None is found")
        pos += (op.size if type(op) is Call else 1)
        args.append(op)
    # Do not allow unclosed operation
    if not isClosed: return None
    return Call(toks[1].value, args, pos+1)


def _is_open_par(tok):
    if tok.type != TOKEN_TYPE_PAR: return False
    return tok.value in "([{"

def _is_closed_par(tok):
    if tok.type != TOKEN_TYPE_PAR: return False
    return tok.value in ")]}"