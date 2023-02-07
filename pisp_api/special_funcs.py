SPEC_FUNCS = {
    "forever": "PISP_FOREVER",
    "dict": "PISP_DICT",
    "set": "PISP_SET",
    "get": "PISP_GET",
    "call": "PISP_CALL",
    "either": "PISP_EITHER",
    "cell": "PISP_CELL",
    "list": "PISP_LIST",
    "for": "PISP_FOR",
}

def process_spec_func(name):
    val = SPEC_FUNCS.get(name)
    if val != None: return val
    return name