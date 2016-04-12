import os
import re
import copy
import json
import random
import string

from fishier import Fishier


class FishierJava(Fishier):
    def __init__(self, real_code, config):
        Fishier.__init__(self, real_code, config)
        with open(os.path.join("languages", "ansi_c.json"), "r") as f:
            self.language = self.byteify_json(json.load(f))

        self.regex_function = "[\w\*\[\]]+\s\w+\\(([\w\*\[\]]+\s\w+(\s*),(\s*))*([\w\*\[\]]+\s\w+){0,1}\\)"
        self.regex_conditional = "^(if|else if|else)"
        self.regex_loop = "^(for|while|do)"
        self.regex_return = "^return"
        self.regex_assignment = "^({})\s\w\s=".format("|".join(self.language["var_types"].keys())).replace("*", "\\*")

    def clean_code(self):
        self.code_clean = self.code_original.replace(";", ";\n").replace("{", "\n{\n").replace("}", "\n}\n").replace("\n\n", "\n").replace("\n\n", "\n").split("\n")

        while True:
            if self.code_clean[0].strip().startswith("package") or self.code_clean[0].strip().startswith("import"):
                self.obfuscated_prefix.append(self.code_clean[0])
                del self.code_clean[0]
            elif self.code_clean[0].strip() == "":
                del self.code_clean[0]
            else:
                break

    def create_code_fake_globals(self):
        for i in range(len(self.code_types)):
            for j in range(random.randint(5, 15)):
                g = self.create_random_variable(self.code_types_dict[i], "gvar")
                self.code_fake_globals.append(g)

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

