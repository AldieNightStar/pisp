from pisp_api.parser import Call, Var, Data
import time
from random import randint
from pisp_api.special_funcs import process_spec_func
from dataclasses import dataclass


OPERATORS = (
    '+', '-', '*', '/', '%', '<', '>', '==', '<=', '>=', '!=',
    'and', 'or', 'is', 'not', '.'
)

def tab(s, ignoreFirst=False):
    first = "    " if not ignoreFirst else "" 
    return first + s.replace("\n", "\n    ")


class _CompileEnv:
    def __init__(self) -> None:
        pass


# ops is a list of Either[Call | Var | Data]
def compile(ops):
    env = _CompileEnv()
    rendered_ops = []
    if True:
        for op in ops:
            rendered_ops.append(render_op(op, env))
    sb = []
    sb.append("from pisp_api import *\n")
    sb.append("\n".join(rendered_ops))
    return "\n".join(sb)


def render_op(op, env: _CompileEnv):
    if type(op) is Data:
        if type(op.value) is str:
            return f"\"{_escaped_str(op.value)}\""
        else:
            return str(op.value)
    elif type(op) is Var:
        return op.name
    elif type(op) is Call:
        # (do ...)
        # alias: (do:arg ...)
        if _is_call_contains_diviers(op):
            op = _get_params_and_bodies(op)

        is_block, block_alias = _is_block(op)
        if is_block:
            return _render_lambda_from_args(op.args, env, block_alias)
        elif _is_local(op):
            return _render_local(op.args, env)
        elif _is_raw(op):
            return _render_raw(op.args)
        elif _is_def(op):
            return _render_def(op.args, env)
        elif _is_if(op):
            return _render_if(op.args, env)
        elif _is_operator(op):
            return _render_operator(op, env)
        return _render_call(op, env)
    raise Exception("Unexprected Operation type: " + str(op))


def _param_req_var(var):
    if not type(var) is Var:
        raise Exception(f"Variable require, not: " + var)
    return var.name


def _param_req_body(op: Call):
    if not type(op) is Call or not _is_block(op):
        raise Exception("Block is required, not: " + str(op))
    return op.args


def _is_def(op: Call):
    return op.name == "def"

def _is_if(op: Call):
    return op.name == "if"


def _render_def(args, env: _CompileEnv):
    if len(args) < 2:
        raise Exception("Function requires at least 2 arguments")

    # Taking name of the new function
    name = _param_req_var(args[0])

    # Function Body is a last argument
    body_args = _param_req_body(args[-1])

    # Gathering middle argument as argument names
    argnames = args[1:-1]

    arr = []
    for arg_name in argnames:
        arr.append(_param_req_var(arg_name))
    argnames = ", ".join(arr)

    # Render function output
    sb = []
    sb.append(
        f"def {name}({argnames}): return {_render_few_calls(body_args, env)}\n")
    return "\n".join(sb)


def _render_raw(args):
    exc = Exception("Raw requires one string argument")
    if len(args) < 1:
        raise exc
    firstArg = args[0]
    if not type(firstArg) is Data:
        raise exc
    if not type(firstArg.value) is str:
        raise exc
    return firstArg.value


def _is_raw(op: Call):
    return op.name == "raw"


def _is_block(op: Call):
    if not type(op) is Call: return False, ""
    name = op.name
    if ":" in name:
        arr = name.split(":", 1)
        return arr[0] == "do", arr[1]
    return op.name == "do", "*args"


def _is_local(op: Call):
    return op.name == "local"


def _render_call(op: Call, env: _CompileEnv):
    args = [render_op(arg, env) for arg in op.args]
    args_s = ",\n".join(args)
    name = process_spec_func(op.name)
    return f"{name}({tab(args_s, True)})"


def _render_few_calls(args, env: _CompileEnv):
    rendered_ops = []
    for op in args:
        rendered_ops.append(render_op(op, env))
    rendered_ops_joined = ",\n".join(rendered_ops)
    return f"empty_func({tab(rendered_ops_joined, True)})"


def _render_lambda_from_args(args, env: _CompileEnv, alias="*args"):
    return f"lambda {alias}: {tab(_render_few_calls(args, env), True)}"


def _validate_all_vars(args):
    for a in args:
        if not type(a) is Var: raise Exception(f"Can't use other parameter rather than variables: {args}")
    return args

def _populate_with(coll, val, n):
    for i in range(n):
        coll.append(val)
    return coll

def _render_local(args, env: _CompileEnv):
    # (local count 0 (do ...))
    if len(args) < 2:
        raise Exception("Local declaration should have at least 2 arguments. Names then body")

    # last argument should be block
    body = args[-1]
    if not _is_block(body): raise Exception("Third argument of local should be block")
    
    # Also we will validate that all params is vars
    args = _validate_all_vars(args[0:-1])
    
    # Need to generate CELL default values
    cell_func_name = process_spec_func("cell")
    
    arg_names = ", ".join([arg.name for arg in args])
    arg_values = ", ".join(_populate_with([], f"{cell_func_name}()", len(args)))

    # Rendering
    return f"(lambda {arg_names}: {_render_few_calls(body.args, env)})({arg_values})"


def _render_if(args, env: _CompileEnv):
    # (if active (do ...) (do ...))
    if len(args) < 2:
        raise Exception("If should take at least 2 arguments")
    bodyThen = _param_req_body(args[1])
    bodyElse = None
    if len(args) > 2:
        bodyElse = _param_req_body(args[2])
    
    bodyThen_rendered = tab(_render_few_calls(bodyThen, env), True)
    bodyElse_rendered = "None"
    if bodyElse != None:
        bodyElse_rendered = tab(_render_few_calls(bodyElse, env), True)
    toRender = f"{bodyThen_rendered} if {render_op(args[0], env)} else {bodyElse_rendered}"
    return toRender

def _is_operator(call: Call):
    return call.name in OPERATORS

def _render_operator(op: Call, env: _CompileEnv):
    if len(op.args) < 2: raise Exception(f"Operator {op.name} requires at least 2 parameters")
    rendered_gen = [render_op(o, env) for o in op.args]
    divided_by_operators_s = (f"{op.name}").join(rendered_gen)
    return f"({divided_by_operators_s})"

def _escaped_str(s):
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\0", "\\0")
    s = s.replace("\\", "\\\\")
    s = s.replace("\"", "\\\"")
    return s

def _is_divier(v: Var):
    if not type(v) is Var: return False, ""
    if v.name == "::": return True, "*args"
    if v.name.startswith("::"): return True, v.name[2:]
    return False, "*args"
    # (if (== 10 10) :: "OK" :: "BAD")

def _is_call_contains_diviers(call: Call):
    for arg in call.args:
        is_divider, _ = _is_divier(arg)
        if is_divider: return True
    return False

def _get_params_and_bodies(call: Call):
    # args: list of either Var, Data, Call
    reading_params = True
    params = []
    bodies = [] # list[list[any]]
    current_body = []
    previous_body_alias = None
    for arg in call.args:
        is_dividier, divider_alias = _is_divier(arg)
        
        if is_dividier:
            # If it's first time, we will assign alias faster than it will be used
            if previous_body_alias == None:
                previous_body_alias = divider_alias
            if reading_params:
                reading_params = False
            else:
                bodies.append(Call(f"do:{previous_body_alias}", current_body, 0))
                current_body = []
                previous_body_alias = divider_alias
            continue
        if reading_params:
            params.append(arg)
        else:
            current_body.append(arg)
    # If there are remaining some body data, add it to bodies
    if len(current_body) > 0:
        bodies.append(Call(f"do:{previous_body_alias}", current_body, 0))
    params_and_bodies = [*params, *bodies]
    return Call(call.name, params_and_bodies, 0)