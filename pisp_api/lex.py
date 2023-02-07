from dataclasses import dataclass
import re

TOKEN_TYPE_PAR   = "par"
TOKEN_TYPE_STR   = "str"
TOKEN_TYPE_NUM   = "num"
TOKEN_TYPE_FLOAT = "float"
TOKEN_TYPE_VAR   = "var"

_NUMBER = re.compile(r"\d+")
_NUMBER_FLOAT = re.compile(r"\d+\.\d+")
_ETC = re.compile(r"\S+")

@dataclass
class Token:
    value: any
    type: str

def lex(text):
    arr = []
    pos = 0
    while pos < len(text):
        textX = text[pos:]
        if textX[0] in " \t\r\n":
            pos += 1
            continue
        commentSize = _com(textX)
        if commentSize != None:
            pos += commentSize
            continue
        parenthesis = _par(textX)
        if parenthesis != None:
            pos += 1
            arr.append(Token(parenthesis, TOKEN_TYPE_PAR))
            continue
        number = _num(textX)
        if number != None:
            pos += len(number)
            if ("." in number):
                arr.append(Token(float(number), TOKEN_TYPE_FLOAT))
            else:
                arr.append(Token(int(number), TOKEN_TYPE_NUM))
            continue
        string, string_size = _str(textX)
        if string_size > 0:
            pos += string_size
            arr.append(Token(string, TOKEN_TYPE_STR))
            continue
        var_value = _var(textX)
        if var_value != None:
            pos += len(var_value)
            arr.append(Token(var_value, TOKEN_TYPE_VAR))
            continue
        raise Exception(f"Unknown tokens next: {textX[0:32]} ...")
    return arr

def tryLexRe(re, src):
    g = re.match(src)
    if g == None:
        return None
    return g.group(0)

def _var(t):
    etc = tryLexRe(_ETC, t)
    if etc == None: return None
    sb = []
    for c in etc:
        if _par(c) != None:
            break
        sb.append(c)
    return "".join(sb)

# Comment
def _com(t):
    if not t[0] in "#;": return None
    cnt = 0
    for c in t:
        if c == '\n': break
        cnt += 1
    return cnt


def _num(t):
    minus = False
    if t[0] == "-":
        t = t[1:]
        minus = True
    num = tryLexRe(_NUMBER_FLOAT, t)
    if num != None: return ("-" if minus else "") + num
    num = tryLexRe(_NUMBER, t)
    if num != None: return ("-" if minus else "") + num

def _str(s):
    end = s[0]
    if not end in "\"'`":
        return None, 0
    sb = []
    esc = False
    addsize = 2
    for c in s[1:]:
        if esc:
            esc = False
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            elif c == "0":
                c = "\0"
            elif c == "r":
                c = "\r"
            sb.append(c)
            continue
        if c == "\\":
            esc = True
            addsize += 1
            continue
        if c == end:
            return "".join(sb), len(sb) + addsize
        sb.append(c)
    return None, 0

# Parenthesis
def _par(t):
    if t[0] in "()[]{}": return t[0]