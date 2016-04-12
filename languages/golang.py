import os
import re
import copy
import json
import string
import random

from fishier import Fishier


class FishierGolang(Fishier):
    def __init__(self, real_code, config):
        Fishier.__init__(self, real_code, config)
        with open(os.path.join("languages", "golang.json"), "r") as f:
            self.language = self.byteify_json(json.load(f))

        self.regex_function = "^func"
        self.regex_conditional = "^(if|else if|else)"
        self.regex_loop = "^(for|while)"
        self.regex_return = "^return"
        self.regex_assignment = "^var\s\w"

    """
    def create_code_math(self, unused_locals, current_signature, local_vars):
        ret = []
        used_vars = []

        op = random.choice(["+", "-", "*", "^", "&", "|", "assign slice", "assign map", "check value"])

        operators = {"int": ["+", "-", "*", "^", "&", "|"],
                     "float32": ["+", "-", "*"],
                     "bool": ["&&", "||"]}

        if op in operators["int"]:
            math_type = random.choice(["int", "float32", "bool"])
            operator = random.choice(operators[math_type])

            v1 = self.pick_unused_variable(math_type, unused_locals, current_signature["args"]+local_vars)
            v2 = self.pick_unused_variable(math_type, unused_locals, current_signature["args"]+local_vars)
            v3 = self.pick_unused_variable(math_type, unused_locals, current_signature["args"]+local_vars)

            ret.append("%s = %s %s %s" % (v1, v2, operator, v3))
            used_vars.extend([v2, v3])

        elif op == "assign slice":
            s1 = self.pick_unused_variable("[]int", unused_locals, current_signature["args"]+local_vars)
            v1 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
            v2 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
            v3 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)

            ret.append("%s = append(%s, %s)" % (s1, s1, v1))
            ret.append("%s = append(%s, %s)" % (s1, s1, v2))
            ret.append("%s = %s[len(%s)-1] %s %s[len(%s)-2]" % (v3, s1, s1, random.choice(operators["int"]), s1, s1))
            ret.append("%s = append(%s, %s)" % (s1, s1, v3))
            used_vars.extend([s1, v1, v2, v3])

        elif op == "assign map":
            m1 = self.pick_unused_variable("map[string]int", unused_locals, current_signature["args"]+local_vars)
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            v1 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)

            ret.append("%s[%s] = %s" % (m1, s1, v1))
            used_vars.extend([m1, s1, v1])

        elif op == "check value":
            b1 = self.pick_unused_variable("bool", unused_locals, current_signature["args"]+local_vars)
            v1 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
            v2 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)

            ret.append("%s = (%s == %s)" % (b1, v1, v2))
            used_vars.extend([v1, v2])

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

    def create_code_conditional(self, real_code, unused_locals, current_signature, local_vars, code_levels, in_func=False):
        ret = []

        v = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)

        passed_local_vars = local_vars
        legit_code = self.create_code_block(real_code, current_signature, passed_local_vars, False, code_levels-1, in_func)
        if not legit_code:
            legit_code = ["pass"]

        passed_local_vars = local_vars
        fake_code = self.create_code_block([], current_signature, passed_local_vars, False, code_levels-1, in_func)
        if not fake_code:
            fake_code = ["pass"]

        b1 = self.pick_unused_variable("bool", unused_locals, current_signature["args"]+local_vars)

        r = random.randint(0, 1)
        if r == 0:
            ret.append("%s = ((%s * 0) != 0)" % (b1, v))
            ret.append({"line": "if %s" % b1, "code_block": fake_code["code"]})
            ret.append({"line": "else", "code_block": legit_code["code"]})
        elif r == 1:
            ret.append("%s = ((%s * 1) != %s)" % (b1, v, v))
            ret.append({"line": "if %s" % b1, "code_block": fake_code["code"]})
            ret.append({"line": "else", "code_block": legit_code["code"]})

        return {"code": ret, "used_vars": [b1, v]}

    def create_code_loop(self, unused_locals, current_signature, local_vars):
        return {"code": [], "used_vars": []}

    def create_code_string_work(self, unused_locals, current_signature, local_vars):
        ret = []
        op = random.choice(["length", "copy", "compare",
                            "copy byte", "copy last byte", "append byte",
                            "map string", "append 1 string", "append 2 strings"])

        used_vars = []

        if op == "length":
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            i1 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = len(%s)" % (i1, s1))
            used_vars.extend([s1])

        elif op == "copy":
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s2 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = %s" % (s1, s2))
            used_vars.extend([s1, s2])

        elif op == "compare":
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s2 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            b1 = self.pick_unused_variable("bool", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = (%s == %s)" % (b1, s1, s2))
            used_vars.extend([s1, s2])

        elif op == "copy first byte":
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            c1 = self.pick_unused_variable("byte", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = byte(%s[0])" % (c1, s1))
            used_vars.extend([c1, s1])

        elif op == "copy last byte":
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            i1 = self.pick_unused_variable("int", unused_locals, current_signature["args"]+local_vars)
            c1 = self.pick_unused_variable("byte", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = len(%s)" % (i1, s1))
            ret.append("%s = byte(%s[%s-1])" % (c1, s1, i1))
            used_vars.extend([i1, s1])

        elif op == "append byte":
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s2 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            c1 = self.pick_unused_variable("byte", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = %s + string(%s)" % (s1, s2, c1))
            used_vars.extend([c1, s2])

        elif op == "map string":
            m1 = self.pick_unused_variable("map[string]string", unused_locals, current_signature["args"]+local_vars)
            m2 = self.pick_unused_variable("map[string]string", unused_locals, current_signature["args"]+local_vars)
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s2 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s3 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s4 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s[%s] = %s" % (m1, s1, s2))
            ret.append("%s[%s] = %s" % (m1, s3, s4))
            ret.append("%s[%s] = %s[%s] + %s[%s]" % (m2, s1, m1, s1, m1, s3))
            #ret.append("%s[%s] = %s[%s]" % (m2, s1, m1, s1))
            used_vars.extend([m1, s1, s2, s3, s4])

        elif op == "append 1 string":
            sl1 = self.pick_unused_variable("[]string", unused_locals, current_signature["args"]+local_vars)
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = append(%s, %s)" % (sl1, sl1, s1))
            used_vars.extend([sl1, s1])

        elif op == "append 2 strings":
            sl1 = self.pick_unused_variable("[]string", unused_locals, current_signature["args"]+local_vars)
            s1 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            s2 = self.pick_unused_variable("string", unused_locals, current_signature["args"]+local_vars)
            ret.append("%s = append(%s, %s, %s)" % (sl1, sl1, s1, s2))
            used_vars.extend([sl1, s1, s2])

        return {"code": ret, "used_vars": used_vars}

    def create_code_sleep(self, unused_locals, current_signature, local_vars):
        return {"code": [], "used_vars": []}


    def pick_unused_variable(self, var_type, unused, backup):


        for arg in unused:
            if arg["type"] == var_type:
                return arg["name"]

        c = []
        for arg in backup:
            if arg["type"] == var_type:
                c.append(arg["name"])

        return random.choice(c)

    def pick_random_variable(self, var_type, args, local_vars):


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
                random.shuffle(self.code_fake_globals)
                for c in self.code_fake_globals:
                    if c["type"] == var_type:
                        return c["name"]
                use_me = 1
"

    def create_random_variable(self, var_type, prefix):

        v = {"type": var_type, "name": ""}
        while (v["name"] == "") or (v["name"] in self.used_variables):
            v["name"] = "%s_%s" % (prefix, self.random_lower_alphanum(8))

        if v["type"] == "bool":
            v["init_value"] = random.choice(["true", "false"])
            v["line"] = "var %s %s = %s" % (v["name"], v["type"], v["init_value"])
        elif v["type"] == "int":
            v["init_value"] = str(random.randint(0, pow(2, 32)))
            v["line"] = "var %s %s = %s" % (v["name"], v["type"], v["init_value"])
        elif v["type"] == "float32":
            v["init_value"] = str(float(random.randint(0, pow(2, 32))) / float(random.randint(0, pow(2, 32))))
            v["line"] = "var %s %s = %s" % (v["name"], v["type"], v["init_value"])
        elif v["type"] == "byte":
            v["init_value"] = random.choice(string.ascii_letters + string.digits)
            if v["init_value"] == '\\':
                v["init_value"] = '$'
            v["line"] = "var %s %s = \'%c\'" % (v["name"], v["type"], v["init_value"])
        elif v["type"] == "string":
            v["init_value"] = self.random_alphanum(random.randint(4, 32))
            v["line"] = "var %s %s = \"%s\"" % (v["name"], v["type"], v["init_value"])
        elif v["type"].startswith("[]"):
            v["length"] = random.randint(1, 10)
            v["init_value"] = "make(%s, %d)" % (v["type"], v["length"])
            v["line"] = "var %s %s = %s" % (v["name"], v["type"], v["init_value"])
        elif v["type"].startswith("map"):
            v["init_value"] = "make(%s)" % v["type"]
            v["line"] = "var %s %s = %s" % (v["name"], v["type"], v["init_value"])

        # The variable starts unused
        v["used"] = False

        self.used_variables.add(v["name"])

        return v
    """
    def find_code_block(self, code_block, index):
        brackets = 1

        if not (code_block[index] == "{"):
            print "Code block did not start with brackets..."
            return None

        line_index = index+1

        while line_index < len(code_block):
            if code_block[line_index] == "{":
                brackets += 1
            elif code_block[line_index] == "}":
                brackets -= 1

            if not brackets:
                break

            line_index += 1

        return line_index

    def clean_code(self):
        self.code_clean = self.code_original.replace("{", "\n{\n").replace("}", "\n}\n").replace("\n\n", "\n").replace("\n\n", "\n").split("\n")

        while True:
            if self.code_clean[0].strip().startswith("package") or self.code_clean[0].strip().startswith("import"):
                self.obfuscated_prefix.append(self.code_clean[0])
                del self.code_clean[0]
            elif self.code_clean[0].strip() == "":
                del self.code_clean[0]
            else:
                break

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
                    ret += "%s%s {\n" % (current_tab, l["line"])
                elif "lines" in l:
                    for line in l["lines"]:
                        ret += "%s%s\n" % (current_tab, line)
                    ret = ret[:-1] + " {\n"
                ret += self.fill_code_string(l["code_block"], tab_count+1)
                ret += "%s} \n\n" % current_tab

        return ret

    def post_process_code_string(self):
        self.obfuscated_code_string = re.sub("}(\s+)else(\s+){", "} else {", self.obfuscated_code_string)
