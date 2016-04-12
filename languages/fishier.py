import re
import copy
import math
import string
import random

from generators import VarGenerators
from parsers import CodeParsers


class Fishier:
    def __init__(self, real_code, config):
        with open(real_code, "r") as f:
            self.code_original = f.read()

        self.config = config

        self.obfuscated_prefix = []
        self.obfuscated_code = []
        self.obfuscated_functions = []

        self.obfuscated_code_string = ""

        self.code_functions = []

        # List of libraries to be included
        self.libraries = []

        # List of fake global variables
        self.code_fake_globals = []

        # Each obfuser will clean up the code that is passed to it and store it as this list
        self.code_clean = []

        # The allowed code types, and a dictionary for randomizing them
        self.code_types = []
        self.code_types_dict = {}

        # List of used function names and used variable names
        self.used_functions = set()
        self.used_variables = set()

        # The regexes for matching different code constructs
        self.regex_function = ""
        self.regex_conditional = ""
        self.regex_loop = ""
        self.regex_return = ""
        self.regex_assignment = ""

        # The size of tabs in the code
        self.tab_size = "    "

        # The difficulty of the obfuscator, can be ramped up and down for more red herring code
        self.difficulty = 5

        # The number of levels of recursion to use
        self.recursion = int(self.config.recursion)

        # The current language, this will be set by the subclass
        self.language = None

        # The list of variable types used in the language
        self.var_types = []

    def create_code(self):
        # Find unused variable types in the language config and store them back
        self.find_unusers()

        # Clean up the original code base
        self.clean_code()

        # Create the full code block from the cleaned code
        code_block = self.create_code_block(self.code_clean, {"name": "", "return": "", "args": []}, [],
                                            add_return=False, code_levels=self.recursion, in_func=False)

        # Create the code strings
        self.fill_obfuscated_code(code_block["code"])
        self.obfuscated_code_string = self.fill_code_string(self.obfuscated_code, 0)

        # Post process them to do any final fixes
        self.post_process_code_string()

    def find_unusers(self):
        for var_type in self.language["var_types"].keys():
            unusers = []
            for op in self.language["math"]["operations"].keys():
                for v_types in self.language["math"]["operations"][op]["var_types"]:
                    if var_type in v_types:
                        unusers.append("math")
                        break
            for op in self.language["memory"]["operations"].keys():
                for v_types in self.language["memory"]["operations"][op]["var_types"]:
                    if var_type in v_types:
                        unusers.append("memory")
                        break
            for op in self.language["strings"]["operations"].keys():
                for v_types in self.language["strings"]["operations"][op]["var_types"]:
                    if var_type in v_types:
                        unusers.append("strings")
                        break

            self.language["var_types"][var_type]["unusers"] = unusers

    def create_abstracted_code_block(self, abstract, real_code, signature, local_vars, lv, in_func=False):
        if abstract == "`f`":
            return self.create_code_block([], signature, local_vars, False, lv, in_func)
        elif abstract == "`r`":
            return self.create_code_block(real_code, signature, local_vars, False, lv, in_func)

    def create_code_block(self, real_code, current_signature, lv,
                          add_return=False, code_levels=10, in_func=False):
        ret = {"code": [], "used_vars": []}

        unused_locals = []

        old_local_vars = copy.copy(lv)

        self.var_types = self.language["var_types"].keys()

        # Generate local variables for the code block if it's in a function or if variables
        # outside of functions are alright
        new_local_vars = []
        if int(self.language["features"]["gen_vars_outside_functions"]) or in_func:
            for i in range(len(self.var_types)):
                for j in range(random.randint(1, 2)):
                    new_local_vars.append(self.create_random_variable(self.var_types[i], "lvar"))
        random.shuffle(new_local_vars)

        # Add them to the code block return
        for lv in new_local_vars:
            unused_locals.append(lv)

        local_vars = old_local_vars
        local_vars.extend(new_local_vars)

        # Check for any assignments of variables and mix them into the other initializations
        assignments = []
        if real_code:
            while real_code[0].strip() in ["{", "}", ""]:
                del real_code[0]

            while re.match(self.regex_assignment, real_code[0].strip()):
                assignments.append(real_code[0])
                del real_code[0]

        if assignments:
            if new_local_vars:
                ass_break = len(new_local_vars)/len(assignments)
                ass = [new_local_vars[i::ass_break] for i in range(ass_break)]
                for i in range(len(ass)):
                    for a in ass[i]:
                        ret["code"].append(a["line"])
                    if i < len(assignments):
                        ret["code"].append(assignments[i].strip())

            else:
                for a in assignments:
                    ret["code"].append(a.strip())

        else:
            for lv in new_local_vars:
                ret["code"].append(lv["line"])

        # Keep creating code until there isn't any more real code to include
        # As real code is used, it will be removed from the list
        while True:
            r = self.config.choose_weighted()

            # If there's no real code left but we have unused local variables, focus what we create to use them
            if (not real_code) and unused_locals and in_func:
                unused_type = unused_locals[0]["type"]
                r = random.choice(self.language["var_types"][unused_type]["unusers"])

            # Force real code to be used immediately if it is the continuation of an if else block
            # Otherwise there can be code between if and else, causing syntax errors
            elif real_code and re.match("^(elif|else)", real_code[0]):
                r = "real"

            # If the language doesn't allow generating code outside functions, use real code until you're in a function
            elif (not in_func) and (not int(self.language["features"]["gen_code_outside_functions"])):
                r = "real"

            gen_code = {}

            # Handle functions
            if (r == "function") and ("function" in self.language["code_types"]):
                if code_levels <= 0:
                    continue

                # Create the new function signature
                signature = {"name": "", "return": random.choice(self.language["var_types"].keys()), "args": []}
                while (signature["name"] == "") or (signature["name"] in self.used_functions):
                    signature["name"] = "sub_%s" % VarGenerators.random_lower_alphanum(random.randint(5, 32))
                self.used_functions.add(signature["name"])

                # Create random arguments for the function
                for arg_count in range(random.randint(1, 5)):
                    signature["args"].append(self.create_random_variable(random.choice(self.var_types), "avar"))

                # Create the function call
                return_var = self.pick_unused_variable(signature["return"], unused_locals, current_signature["args"]+local_vars)
                fc = self.language["function"]["call_signature"].replace("`n`", signature["name"])
                arg_list = []
                for a in signature["args"]:
                    new_arg = self.pick_unused_variable(a["type"], unused_locals, current_signature["args"]+local_vars)
                    arg_list.append(self.language["function"]["call_arg_signature"].replace("`n`", new_arg))
                fc = fc.replace("`a`", ", ".join(arg_list)).replace("`v`", return_var)

                gen_code = {"code": [], "used_vars": []}
                gen_code["code"].append(fc)
                gen_code["used_vars"] = arg_list

                # Create the function's code
                self.obfuscated_functions.append(self.create_code_function([], signature, [], code_levels, add_return=True))

            # Handle MATH!
            elif (r == "math") and ("math" in self.language["code_types"]):
                gen_code = self.create_code_math(unused_locals, current_signature, local_vars)

            # Handle Memory manipulation
            elif (r == "memory") and ("memory" in self.language["code_types"]):
                gen_code = self.create_code_memory(unused_locals, current_signature, local_vars)

            # Handle API function calls
            elif (r == "api") and ("api" in self.language["code_types"]):
                gen_code = self.create_code_api(unused_locals, current_signature, local_vars)

            # Handle conditionals
            elif (r == "conditional") and ("conditional" in self.language["code_types"]):
                if code_levels <= 0:
                    continue

                gen_code = self.create_code_conditional([], unused_locals, current_signature, local_vars, code_levels, in_func)

            # Handle loops
            elif (r == "loop") and ("loop" in self.language["code_types"]):
                gen_code = self.create_code_loop(unused_locals, current_signature, local_vars)

            # Handle string manipulations
            elif (r == "strings") and ("strings" in self.language["code_types"]):
                gen_code = self.create_code_string_work(unused_locals, current_signature, local_vars)

            # Handle sleep
            elif (r == "sleep") and ("sleep" in self.language["code_types"]):
                gen_code = self.create_code_sleep(unused_locals, current_signature, local_vars)

            # Handle real code
            elif r == "real":
                # If there's no real code left and all the local vars have been used, end the code block
                if (not real_code) and ((self.language["features"]["must_use_vars"] == "0") or (not len(unused_locals)) or (not in_func)):

                    # Add a return value if it says to
                    if add_return:
                        v1 = self.pick_unused_variable(current_signature["return"], unused_locals, current_signature["args"]+local_vars)
                        return_line = self.language["function"]["return_definition"].replace("`r`", v1)
                        ret["code"].append(return_line)
                    break

                # Otherwise, if there's no more real code, keep using up vars
                elif not real_code:
                    continue

                # Get rid of bracket lines and empty lines
                if real_code[0].strip() in ["{", "}", ""]:
                    del real_code[0]
                    continue

                if re.match(self.regex_conditional, real_code[0].strip()) or \
                   re.match(self.regex_loop, real_code[0].strip()) or \
                   re.match(self.regex_function, real_code[0].strip()):
                    block = {"line": real_code[0].strip(), "code_block": []}

                    tab_count = CodeParsers.get_tab_count(real_code[0])

                    end_of_block = getattr(CodeParsers, self.language["features"]["code_blocks"])(index=1,
                                                                                                  code_block=real_code,
                                                                                                  tab_count=tab_count)
                    #end_of_block = self.find_code_block(tab_count, real_code, 1)

                    cb_in_func = in_func
                    if re.match(self.regex_function, real_code[0].strip()):
                        cb_in_func = True

                    # Pass the code no local variables if it's a new function
                    use_locals_vars = local_vars
                    if re.match(self.regex_function, real_code[0].strip()):
                        use_locals_vars = []

                    print real_code[0]
                    new_code_block = self.create_code_block(real_code[1:end_of_block], current_signature,
                                                            use_locals_vars, False, code_levels-1, cb_in_func)
                    block["code_block"] = new_code_block["code"]

                    gen_code = {"code": [block], "used_vars": new_code_block["used_vars"]}

                    real_code = real_code[end_of_block:]

                elif re.match(self.regex_return, real_code[0].strip()):
                    ret["code"].append("%s" % real_code[0].strip())
                    print real_code[0]
                    del real_code[0]
                    break

                else:
                    ret["code"].append("%s" % real_code[0].strip())
                    print real_code[0]
                    del real_code[0]

            if gen_code:
                ret["code"].extend(gen_code["code"])
                for new_arg in gen_code["used_vars"]:
                    ret["used_vars"].append(new_arg)
                    for i in range(len(unused_locals)):
                        if unused_locals[i]["name"] == new_arg:
                            del unused_locals[i]
                            break

        ret["used_vars"] = list(set(ret["used_vars"]))
        return ret

    def create_random_variable(self, var_type, prefix):
        """
        Description:
            Generate a randomized variable
        :param var_type: string
        :param prefix: string
        :return: dict
        """

        v = {"type": var_type, "name": "", "size": 0, "init_value": ""}

        # Create a variable name
        while (v["name"] == "") or (v["name"] in self.used_variables):
            v["name"] = "%s_%s" % (prefix, VarGenerators.random_lower_alphanum(8))
        self.used_variables.add(v["name"])

        # Create the variable init_value
        type_info = self.language["var_types"][var_type]

        # If the variable definition has a temporary name in it, create one and use it
        temp_name = ""
        if "`nt`" in type_info["line"]:
            while (temp_name == "") or (temp_name in self.used_variables):
                temp_name = "%s_%s" % (prefix, VarGenerators.random_lower_alphanum(8))
            self.used_variables.add(temp_name)

        # Fill in the size of the variable
        v["size"] = type_info["size"]
        if "rand" in v["size"]:
            m = re.match("randint\((\d+),(\d+)\)", v["size"])
            v["size"] = str(random.randint(int(m.group(1)), int(m.group(2))))

        # Or it's an expression of its type and size
        if "`" in type_info["init_value"]:
            v["init_value"] = type_info["init_value"].replace("`t`", var_type).replace("`l`", v["size"])
        # The value is a CSV
        elif "," in type_info["init_value"]:
            v["init_value"] = random.choice(type_info["init_value"].split(","))
        # Otherwise it is a function reference
        else:
            i = getattr(VarGenerators, type_info["init_value"])()
            v["init_value"] = i["value"]
            v["size"] = i["size"]

        if type_info["size"] == "len+1":
            v["size"] += 1

        v["line"] = type_info["line"].replace("`n`", v["name"]).replace("`v`", str(v["init_value"]))
        v["line"] = v["line"].replace("`t`", var_type).replace("`l`", str(v["size"])).replace("`nt`", temp_name)

        return v

    def create_code_function(self, real_code, signature, local_vars, code_levels, add_return=False):
        func = {"line": "", "code_block": []}

        sig_args = []
        for arg in signature["args"]:
            a = self.language["function"]["arg_definition"].replace("`n`", arg["name"]).replace("`t`", arg["type"])
            sig_args.append(a)

        func["line"] = self.language["function"]["definition"].replace("`n`", signature["name"])
        func["line"] = func["line"].replace("`a`", ", ".join(sig_args))
        func["line"] = func["line"].replace("`r`", signature["return"])

        # Create the function code block
        code_block = self.create_code_block(real_code, signature, local_vars,
                                            add_return=add_return, code_levels=(code_levels-1), in_func=True)

        # If this language has function prologues, include that at the beginning of the function
        if ("prologue" in self.language["function"]) and self.language["function"]["prologue"]:
            arg_list = []
            for a in signature["args"]:
                arg_list.append(self.language["function"]["arg_definition"].replace("`n`", a["name"]))

            prologue = self.language["function"]["prologue"].replace("`a`", ", ".join(arg_list))

            code_block["code"].insert(0, prologue)

        func["code_block"] = code_block["code"]

        return func

    def create_code_conditional(self, real_code, unused_locals, current_signature, local_vars, code_levels, in_func=False):
        ret = []
        used_vars = []

        passed_local_vars = local_vars

        cond_op = self.language["conditional"]["operations"][random.choice(self.language["conditional"]["operations"].keys())]
        var_types = random.choice(cond_op["var_types"])

        args = []
        for v in var_types:
            args.append(self.pick_unused_variable(v, unused_locals, current_signature["args"]+local_vars))

        # Create the if code block
        if_lines = []
        for line in cond_op["if_lines"]:
            new_line = line
            for i in range(len(args)):
                new_line = new_line.replace("`v{}`".format(i+1), args[i])
            if_lines.append(new_line)
        if_code = self.create_abstracted_code_block(cond_op["if_code"], real_code, current_signature, passed_local_vars, code_levels-1, in_func)
        ret.append({"lines": if_lines, "code_block": if_code["code"]})

        # Create the else if code blocks
        for e in cond_op["else_ifs"]:
            if e["line"]:
                else_if_line = e["line"]
                for i in range(len(args)):
                    else_if_line = else_if_line.replace("`v{}`".format(i+1), args[i])
                else_if_code = self.create_abstracted_code_block(e["code"], real_code, current_signature, passed_local_vars, code_levels-1, in_func)
                ret.append({"line": [else_if_line], "code_block": else_if_code["code"]})

        # Create the else code block
        if cond_op["else_line"]:
            else_line = cond_op["else_line"]
            for i in range(len(args)):
                else_line = else_line.replace("`v{}`".format(i+1), args[i])

            else_code = self.create_abstracted_code_block(cond_op["else_code"], real_code, current_signature, passed_local_vars, code_levels-1, in_func)
            ret.append({"line": else_line, "code_block": else_code["code"]})

        for used in cond_op["used_vars"]:
            used_vars.append(args[int(used.replace("`", "").replace("v", "")) - 1])

        return {"code": ret, "used_vars": used_vars}

    def create_code_math(self, unused_locals, current_signature, local_vars):
        ret = []
        used_vars = []

        math_op = self.language["math"]["operations"][random.choice(self.language["math"]["operations"].keys())]
        var_types = random.choice(math_op["var_types"])

        args = []
        for v in var_types:
            args.append(self.pick_unused_variable(v, unused_locals, current_signature["args"]+local_vars))

        for line in math_op["lines"]:
            for i in range(len(args)):
                line = line.replace("`v{}`".format(i+1), args[i])
            line = line.replace("`o`", random.choice(math_op["operands"]))
            ret.append(line)

        for used in math_op["used_vars"]:
            used_vars.append(args[int(used.replace("`", "").replace("v", "")) - 1])

        return {"code": ret, "used_vars": used_vars}

    def create_code_memory(self, unused_locals, current_signature, local_vars):
        ret = []
        used_vars = []

        mem_op = self.language["memory"]["operations"][random.choice(self.language["memory"]["operations"].keys())]
        var_types = random.choice(mem_op["var_types"])

        args = []
        for v in var_types:
            args.append(self.pick_unused_variable(v, unused_locals, current_signature["args"]+local_vars))

        for line in mem_op["lines"]:
            for i in range(len(args)):
                line = line.replace("`v{}`".format(i+1), args[i])
            ret.append(line)

        for used in mem_op["used_vars"]:
            used_vars.append(args[int(used.replace("`", "").replace("v", "")) - 1])

        return {"code": ret, "used_vars": used_vars}

    def create_code_api(self, unused_locals, current_signature, local_vars):
        ret = {"code": [], "used_vars": []}

        op = random.choice(["WriteFile", "CreateReg", "CreateMutex"])

        v1 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
        v2 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
        v3 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)

        if op == "WriteFile":
            pass
        elif op == "CreateReg":
            pass
        elif op == "CreateMutex":
            pass

        return ret

    def create_code_loop(self, unused_locals, current_signature, local_vars):
        return {"code": [], "used_vars": []}

    def create_code_string_work(self, unused_locals, current_signature, local_vars):
        ret = []

        used_vars = []

        string_op = self.language["strings"]["operations"][random.choice(self.language["strings"]["operations"].keys())]
        var_types = random.choice(string_op["var_types"])

        args = []
        for v in var_types:
            args.append(self.pick_unused_variable(v, unused_locals, current_signature["args"]+local_vars))

        for line in string_op["lines"]:
            for i in range(len(args)):
                line = line.replace("`v{}`".format(i+1), args[i])
            ret.append(line)

        for used in string_op["used_vars"]:
            used_vars.append(args[int(used.replace("`", "").replace("v", "")) - 1])

        return {"code": ret, "used_vars": used_vars}

    def create_code_sleep(self, unused_locals, current_signature, local_vars):
        return {"code": [], "used_vars": []}

    def pick_unused_variable(self, var_type, unused, backup):
        """
        Description:
            Pick a randomized variable to use

        :param var_type: the type of variable you want to use
        :param args: list of currently available function parameters
        :param local_vars: list of currently available local variables
        :return: string: the variable name to use
        """

        for arg in unused:
            if arg["type"] == var_type:
                return arg["name"]

        c = []
        for arg in backup:
            if arg["type"] == var_type:
                c.append(arg["name"])

        try:
            return random.choice(c)
        except:
            return random.choice(c)

    def get_tab_count(self, line):
        tab_count = 0
        pos = 0
        while ((pos+4) < len(line)) and (line[pos:pos+4] == "    "):
            tab_count += 1
            pos += 4
        return tab_count

    def byteify_json(self, json_object):
        if isinstance(json_object, dict):
            return {self.byteify_json(key): self.byteify_json(value)
                    for key, value in json_object.iteritems()}
        elif isinstance(json_object, list):
            return [self.byteify_json(element) for element in json_object]
        elif isinstance(json_object, unicode):
            return json_object.encode('utf-8')
        else:
            return json_object

    def clean_code(self):
        pass

    def fill_obfuscated_code(self, code_block):
        self.obfuscated_code = []
        self.obfuscated_code.extend(self.obfuscated_prefix)
        self.obfuscated_code.extend(self.obfuscated_functions)
        self.obfuscated_code.extend(code_block)

    def fill_code_string(self, code_block, tab_count):
        ret = ""
        current_tab = self.tab_size*tab_count
        for l in code_block:
            if type(l) is str:
                ret += "%s%s\n" % (current_tab, l)
            elif type(l) is dict:
                if "line" in l:
                    ret += "%s%s\n" % (current_tab, l["line"])
                elif "lines" in l:
                    for line in l["lines"]:
                        ret += "%s%s\n" % (current_tab, line)
                ret += self.fill_code_string(l["code_block"], tab_count+1)
                ret += "\n"
        return ret

    def post_process_code_string(self):
        """
        Description:
            Handle any post processing of the code string that's necessary here

        :return:
        """

        pass


