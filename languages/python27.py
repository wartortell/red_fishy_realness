import os
import re
import copy
import json
import string
import random

from fishier import Fishier
from generators import VarGenerators


class FishierPython27(Fishier):
    def __init__(self, real_code, config):
        Fishier.__init__(self, real_code, config)
        with open(os.path.join("languages", "python27.json"), "r") as f:
            self.language = self.byteify_json(json.load(f))

        self.regex_function = "def\s\w+\\((\s\w+(\s*),(\s*))*(\w+){0,1}\\):"
        self.regex_conditional = "^(if|elif|else)"
        self.regex_loop = "^(for|while|with)"
        self.regex_assignment = "^\w(\s+)="
        self.regex_return = "^return"

    def clean_code(self):
        self.code_clean = self.code_original.replace("\t", "    ").replace("\n\n", "\n").replace("\n\n", "\n").split("\n")

        i = 0
        while i < len(self.code_clean):
            if self.code_clean[i].strip().startswith("use"):
                self.obfuscated_prefix.append(self.code_clean[i])
                del self.code_clean[i]
            elif self.code_clean[i].strip() == "":
                del self.code_clean[i]
            else:
                i += 1

    def find_code_block(self, tab_count, code_block, index):
        line_index = index

        while line_index < len(code_block):
            # Ignore empty lines
            if (not (code_block[line_index].strip() == "")) and \
                    (self.get_tab_count(code_block[line_index]) <= tab_count):
                break

            line_index += 1

        return line_index

    def fill_code(self):
        for i in self.code_includes:
            self.obfuscated_code.append(i)
        self.obfuscated_code.append("\n\n")
        for i in self.code_functions:
            self.obfuscated_code.append(i)

    def get_tab_count(self, line):
        tab_count = 0
        pos = 0
        while ((pos+4) < len(line)) and (line[pos:pos+4] == "    "):
            tab_count += 1
            pos += 4
        return tab_count

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
