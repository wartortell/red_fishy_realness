__author__ = 'wartortell'

import random
import string

from fishier import Fishier


class FishierCpp(Fishier):
    def create_code(self):
        pass

    def parse_real_code(self):
        pass

    def parse_function(self):
        pass

# The different elements of code that are currently supported
code_elements = ["function", "math", "conditional", "loop",  "real"] # "string_work", "api",

# The different types that are currently supported
code_types = ["int", "char", "char*"]
code_types_dict = {"int": 0, "char": 2, "char*": 3}

# List of function strings
functions = []

# Dictionary of used variable names: name -> type
used_variables = {}
used_functions = {}

# The size of a tab
tab_size = " " * 2

# Difficulty scale, greater means more red herring code
difficulty = 7

# This is the maximum number of code levels of red herring code that can be generated
# This must be used to avoid infinite recursion
max_code_levels = 10

configuration = None


def pick_random_variable(var_type, args, local_vars, global_vars):
    """
    Description:
        Pick a randomized variable to use

    :param type: the type of variable you want to use
    :param args: list of currently available function parameters
    :param local_vars: list of currently available local variables
    :param global_vars: list of currently available global variables
    :return: string: the variable name to use
    """

    use_me = random.randint(1, 3)

    while True:
        if use_me == 1:
            random.shuffle(args)
            for a in args:
                if a["type"] == var_type:
                    return a["name"]
            use_me = random.randint(2, 3)

        elif use_me == 2:
            random.shuffle(local_vars)
            for b in local_vars:
                if b["type"] == var_type:
                    return b["name"]
            use_me = 3

        elif use_me == 3:
            random.shuffle(global_vars)
            for c in global_vars:
                if c["type"] == var_type:
                    return c["name"]
            use_me = 1


def create_random_variable(var_type, prefix):
    """
    Description:
        Generate a randomized variable
    :param type_index:
    :return:
    """

    v = {"type": var_type, "name": ""}
    while (v["name"] == "") or (v["name"] in used_variables):
        v["name"] = "%s_%s" % (prefix, random_alphanum(8))

    if v["type"] == "int":
        v["init_value"] = str(random.randint(0, pow(2, 32)))
        v["line"] = "%s %s = %s;" % (v["type"], v["name"], v["init_value"])
    elif v["type"] == "char":
        v["init_value"] = random.choice(string.ascii_letters + string.digits)
        if v["init_value"] == '\\':
            v["init_value"] = '$'
        v["line"] = "%s %s = \'%c\';" % (v["type"], v["name"], v["init_value"])
    elif v["type"] == "char*":
        v["init_value"] = random_alphanum(random.randint(4, 32))
        v["line"] = "%s %s = \"%s\";" % (v["type"], v["name"], v["init_value"])

    used_variables[v["name"]] = v["type"]

    return v


# Generate a random alphanumeric string
def random_alphanum(length):
    return''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)).replace("\\", "\\\\")


def code_function(real_code, fake_globals, signature, code_levels):
    ret = ""

    ret += "%s %s(" % (signature["return"], signature["name"])
    for argument in signature["args"]:
        ret += "%s %s, " % (argument["type"], argument["name"])
    ret = "%s)\n{\n" % ret[:-2]

    local_vars = []
    for i in range(len(code_types)):
        for j in range(random.randint(1, 10)):
            local_vars.append(create_random_variable(code_types[i], "lvar"))

    random.shuffle(local_vars)

    for i in range(len(local_vars)):
        ret += "%s%s\n" % (tab_size, local_vars[i]["line"])
    ret += "%s\n" % tab_size

    # Create the function code block
    ret += code_block(real_code, signature, fake_globals, local_vars, code_levels, tab_size)

    ret += "%sreturn %s;\n" % (tab_size, pick_random_variable(signature["return"],
                                                              signature["args"],
                                                              local_vars,
                                                              fake_globals))

    return "%s}\n" % ret


def code_math(current_signature, local_vars, fake_globals, tab="  "):
    ret = ""

    for i in range(random.randint(1, difficulty)):
        op = random.choice(["+", "-", "*", "^", "&", "|"])

        v1 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)
        v2 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)
        v3 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)

        ret += "%s%s = %s %s %s;\n" % (tab, v1, v2, op, v3)

    return ret


def code_api(current_signature, local_vars, fake_globals, tab="  "):
    ret = ""

    op = random.choice(["WriteFile", "CreateReg", "CreateMutex"])

    v1 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)
    v2 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)
    v3 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)

    if op == "WriteFile":
        pass
    elif op == "CreateReg":
        pass
    elif op == "CreateMutex":
        pass

    return ret


def code_conditional(real_code, current_signature, local_vars, fake_globals, code_levels, tab):
    ret = ""

    v = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)

    ret += "%sif (%s * 0) {\n" % (tab, v)
    ret += code_block([], current_signature, fake_globals, local_vars, code_levels, tab + tab_size)
    ret += "%s}\n" % tab
    ret += "%selse {\n" % tab
    ret += code_block(real_code, current_signature, fake_globals, local_vars, code_levels, tab + tab_size)
    ret += "%s}\n" % tab

    return ret


def code_loop(tab="  "):
    return ""


def code_string_work(current_signature, local_vars, fake_globals, tab="  "):
    ret = ""

    for i in range(random.randint(1, difficulty)):
        op = random.choice(["strlen", "strcpy", "strncpy", "strcmp"])

        s1 = pick_random_variable("char*", current_signature["args"], local_vars, fake_globals)
        s2 = pick_random_variable("char*", current_signature["args"], local_vars, fake_globals)
        s3 = pick_random_variable("char*", current_signature["args"], local_vars, fake_globals)
        c1 = pick_random_variable("char", current_signature["args"], local_vars, fake_globals)
        i1 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)
        #i2 = i1
        #while i2 == i1:
        i2 = pick_random_variable("int", current_signature["args"], local_vars, fake_globals)

#        if op == "strchr":
#            ret += "%s%s = %s(%s, %s);\n" % (tab, s1, op, s2, c1)
        if op == "strlen":
            ret += "%s%s = %s(%s);\n" % (tab, i1, op, s1)
        elif op == "strcpy":
            # We have to check that the destination has room for the source
            ret += "%s%s = strlen(%s);\n" % (tab, i1, s1)
            ret += "%s%s = strlen(%s);\n" % (tab, i2, s2)
            ret += "%sif(%s >= %s) %s(%s, %s);\n" % (tab, i1, i2, op, s1, s2)
        elif op == "strncpy":
            # We have to use the destination's size
            ret += "%s%s = strlen(%s);\n" % (tab, i1, s1)
            ret += "%s%s(%s, %s, %s);\n" % (tab, op, s1, s2, i1)
        elif op == "strcmp":
            ret += "%s%s = %s(%s, %s);\n" % (tab, i1, op, s1, s2)

    return ret


def code_sleep(current_signature, local_vars, fake_globals, tab="  "):
    pass


def code_block(real_code, current_signature, fake_globals, local_vars, code_levels, tab="  "):
    ret = ""
    global configuration

    # Keep creating code until there isn't any more real code to include
    # As real code is used, it will be removed from the list
    while True:
        r = configuration.choose_weighted()

        # Handle functions
        if r == "function":
            if code_levels <= 0:
                continue
            code_levels -= 1

            real_count = random.randint(0, len(real_code) / 2)

            # Create the new function signature
            signature = {"name": "", "return": random.choice(code_types), "args": []}
            while (signature["name"] == "") or (signature["name"] in used_functions):
                signature["name"] = "sub_%s" % random_alphanum(random.randint(5, 32))
            used_functions[signature["name"]] = signature["return"]

            # Create random arguments for the function
            for arg_count in range(random.randint(1, 5)):
                signature["args"].append(create_random_variable(random.choice(code_types), "avar"))

            # Create the function call
            ret += "%s%s = %s(" % (tab,
                                   pick_random_variable(signature["return"], current_signature["args"],
                                                        local_vars, fake_globals),
                                   signature["name"])

            for a in signature["args"]:
                random_var = pick_random_variable(a["type"], current_signature["args"],
                                                  local_vars, fake_globals)
                ret += "%s, " % random_var
            ret = "%s);\n\n" % ret[:-2]

            # Create the function's code
            functions.append(code_function(real_code[:real_count], fake_globals, signature, code_levels))

            real_code = real_code[real_count:]

        # Handle MATH!
        elif r == "math":
            ret += code_math(current_signature, local_vars, fake_globals, tab)
            ret += "%s\n" % tab

        # Handle API function calls
        elif r == "api":
            ret += code_api(current_signature, local_vars, fake_globals, tab)

        # Handle conditionals
        elif r == "conditional":
            if code_levels <= 0:
                continue
            code_levels -= 1

            real_count = random.randint(0, len(real_code) / 2)
            ret += code_conditional(real_code[:real_count], current_signature, local_vars, fake_globals, code_levels, tab)
            real_code = real_code[real_count:]

        # Handle loops
        elif r == "loop":
            ret += code_loop()

        # Handle string manipulations
        elif r == "string_work":
            ret += code_string_work(current_signature, local_vars, fake_globals, tab)
            ret += "%s\n" % tab

        # Handle sleep
        elif r == "sleep":
            ret += code_sleep(current_signature, local_vars, fake_globals, tab)
            ret += "%s\n" % tab

        # Handle real code
        elif r == "real":
            # If there's no real code left, end the code block
            if len(real_code) == 0:
                break

            # Otherwise add a real code statement
            ret += "%s%s\n" % (tab, real_code[0])
            del real_code[0]

    return ret


def create_code(config, real_code, fake_globals):

    global configuration
    configuration = config

    signature = {"name": "main",
                 "return": "int",
                 "args": [{"name": "argc", "type": "int"}, {"name": "argv", "type": "char**"}]}

    used_variables["argc"] = "int"
    used_variables["argv"] = "char**"

    functions.append(code_function(real_code["code"], fake_globals, signature, max_code_levels))

    return functions


def parse_real_code(code_lines):
    real_code = {"imports": [],
                 "globals": [],
                 "code": []}

    fake_globals = []

    # Get to the Imports section
    i = 0
    while not (code_lines[i].strip() == "//IMPORTS"):
        i += 1
    i += 1

    # Parse the Imports section
    while not (code_lines[i].strip() == "//GLOBALS"):
        if (not (code_lines[i].strip() == "")) and (not code_lines[i].strip().startswith("//")):
            real_code["imports"].append(code_lines[i].strip())
        i += 1
    i += 1

    # Parse the Globals section
    while not (code_lines[i].strip() == "//CODE"):
        if (not (code_lines[i].strip() == "")) and (not code_lines[i].strip().startswith("//")):
            real_code["globals"].append(code_lines[i].strip())
        i += 1
    i += 1

    # Parse the Code section
    while not (code_lines[i].strip() == "//END"):
        if (not (code_lines[i].strip() == "")) and (not code_lines[i].strip().startswith("//")):
            real_code["code"].append(code_lines[i].strip())
        i += 1

    # Create the fake globals based on the real globals
    for i in range(len(real_code["globals"])):
        for j in range(random.randint(1, 3)):
            g = create_random_variable(real_code["globals"][i].split(" ")[0], "gvar")
            fake_globals.append(g)

    return real_code, fake_globals