_NOTHING = {}

class PISP_CELL:
    def __init__(self, val=None) -> None:
        self.val = val
    
    def __call__(self, val=_NOTHING):
        if val is _NOTHING:
            return self.get()
        return self.set(val)
    
    def set(self, val):
        self.val = val
        return val

    def get(self):
        return self.val

def PISP_GET(coll, n=0):
    if type(coll) in (list, tuple, str):
        if n < 0: return None
        if n >= len(coll): return None
        return coll[n]
    elif type(coll) is dict:
        return coll.get(n)

def PISP_SET(coll, n, val=None):
    coll[n] = val
    return val

def PISP_CALL(fun, *args):
    return fun(*args)

def PISP_EITHER(*vals):
    for v in vals:
        if v != None: return v

def PISP_LIST(*els): return [*els]
def PISP_FOR(coll, func):
    for i in coll: func(i)

def empty_func(*els):
    if len(els) < 1: return None
    return els[-1]

def PISP_FOREVER():
    cnt = -1
    while True:
        cnt += 1
        yield cnt
        
def PISP_DICT(): return {}