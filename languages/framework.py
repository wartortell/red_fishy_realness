__author__ = 'Wartortell'

import random

code_elements = ["function", "math", "api", "conditional", "loop", "string_work", "real"]

# Dictionary of globals
global_vars = {"int": [],
               "char": [],
               "string": []}

# List of function strings
functions = []


def code_function(real_code, signature):
    ret = ""

    # Create the local variables that are available at this point in the code
    ret += "%s %s(" % (signature["return"], signature["name"])
    for argument in signature["args"]:
        pass

    # Create the function code block

    return ""


def code_math(locals, tab="  "):
    return ""


def code_api(locals, tab="  "):
    return ""


def code_conditional(real_code, tab="  "):
    return ""


def code_loop(tab="  "):
    return ""


def code_string_work(tab="  "):
    return ""


def code_block(real_code, tab="  "):
    ret = ""

    # Keep creating code until there isn't any more real code to include
    # As real code is used, it will be removed from the list
    while len(real_code) > 0:
        r = random.randint(1, len(code_elements))

        # Handle functions
        if code_elements[r] == "function":
            real_count = random.randint(1, len(real_code) / 2)
            signature = {"name": "",
                         "return": "",
                         "args": []}
            functions.insert(0, code_function(real_code[:real_count], signature))

            real_code = real_code[real_count:]
        
        # Handle MATH!
        elif code_elements[r] == "math":
            ret += code_math(locals, tab)
            
        # Handle API function calls
        elif code_elements[r] == "api":
            ret += code_api(locals, tab)
            
        # Handle conditionals
        elif code_elements[r] == "conditional":
            ret += code_conditional(locals, tab)
        
        # Handle loops
        elif code_elements[r] == "loop":
            ret += code_loop()

        # Handle string manipulations
        elif code_elements[r] == "string_work":
            ret += code_loop()
            
        # Handle real code
        elif code_elements[r] == "real":
            ret += "%s%s\n" % (tab, real_code[0])
            del real_code[0]


def create_code(real_code):

    signature = {"name": "main",
                 "return": "int",
                 "args": [{"name": "argc", "type": "int"}, {"name": "argv", "type": "char**"}]}

    functions.append(code_function(real_code, signature))

    return functions


def parse_real_code(code_lines):
    real_code = {"imports": [],
                 "globals": [],
                 "code": []}

    fake_globals = []

    for i in range(len(code_lines)):
        pass

    return real_code, fake_globals