__author__ = 'Wartortell'

import os
import sys
import random
import logging
import argparse

from languages import obfusion_classes


class ObfusionConfiguration:
    def __init__(self, arch):

        self.arch = arch

        self.logger = logging.getLogger("Obfusion Configuration")
        self.logger.setLevel(logging.INFO)

        self.weights = {"function": 1,
                        "conditional": 1,
                        #"loop": 1,
                        "math": 10,
                        "string": 10,
                        #"api": 1,
                        #"anti_vm": 1,
                        #"anti_dis": 1,
                        #"anti_debug": 1,
                        #"sleep": 0,
                        "sleep_math": 1,
                        "real": 1}

        # The list used by Obfusion when determining which code block will be used
        self.weighted_list = []
        self.weighted_lookup = []

        # The list of values used for random code type choice
        self.code_types = []

        # Initiate the lists
        self.create_weighted_list()
        self.create_code_types()

    def set_weight(self, name, weight):
        """
        Description:
            Set a code type's weight
        :param name: string
        :param weight: int
        :return: None
        """

        if not (name in self.weights.keys()):
            self.logger.error("The code type %s is not known/implemented!" % name)
            return

        if not (type(weight) == int):
            self.logger.error("Weight values must be provided as integers: %s" % str(weight))
            return

        self.weights[name] = weight

        self.create_weighted_list()
        self.create_code_types()

    def set_all_weights(self, new_weights):
        """
        Description:
            Set all the weights to new values, useful for using predefined weight lists

        :param new_weights: dict: string->int
        :return: None
        """

        self.weights = new_weights

        self.create_weighted_list()
        self.create_code_types()

    def create_weighted_list(self):
        """
        Description:
            Create the weighted list based on the current weights

        :return: None
        """

        self.weighted_list = self.weights.keys()
        self.weighted_lookup = []

        for i in range(len(self.weighted_list)):
            for j in range(self.weights[self.weighted_list[i]]):
                self.weighted_lookup.append(i)

    def create_code_types(self):
        """
        Description:
            Fill the code_types array with all code types that have any weight

        :return: None
        """

        self.code_types = []
        for key in self.weights.keys():
            if self.weights[key]:
                self.code_types.append(key)

    def show_weights(self):
        """
        Description:
            Prints the percentage weight of each code type

        :return: None
        """

        print("\nCurrent Weights:\n---------------------")
        for key in sorted(self.weights.keys()):
            print("%s: %2.2f%%" % (key, 100.0*float(self.weights[key])/float(len(self.weighted_lookup))))

    def choose_weighted(self):
        """
        Description:
            Select a weighted choice from the list of code types

        :return: string
        """
        return self.weighted_list[random.choice(self.weighted_lookup)]

    def choose_random(self):
        """
        Description:
            Choose a random code type (do not use weights)
            NOTE: code types with weight 0 will still be ignored by this function

        :return: string
        """

        return random.choice(self.code_types)


class Obfusion:
    def __init__(self, arch, language, real_code_path, obf_code_path, run=False):
        # Up the maximum recursion limit
        sys.setrecursionlimit(50000)

        # Initializations
        self.arch = arch
        self.language = language
        self.real_code_path = real_code_path
        self.obf_code_path = obf_code_path
        self.real_code = {}
        self.fake_globals = []
        self.obfuscated_functions = []

        # Create the configuration
        self.config = ObfusionConfiguration(self.arch)

        # Create the Obfuser Class
        self.obfuser = obfusion_classes[language](real_code_path, self.config)

        if run:
            # Show the current weights being used
            self.config.show_weights()

            # Create the obfuscated code
            self.obfuser.create_code()

            # Output the obfuscated code
            with open(obf_code_path, "w") as f:
                f.write(self.obfuser.obfuscated_code_string)

    def output_code(self, file_pointer, code, tab_count):
        for l in code:
            if type(l) is str:
                file_pointer.write("%s%s\n" % (self.obfuser.tab_size*tab_count, l))
            elif type(l) is dict:
                file_pointer.write("%s%s\n" % (self.obfuser.tab_size*tab_count, l["line"]))
                self.output_code(file_pointer, l["code_block"], tab_count+1)

    def parse_code(self, code_path):

        # Get a list of the real code lines
        with open(code_path, "r") as real_code_file:
            real_code_lines = real_code_file.readlines()

        # Create the fake global variables
        self.real_code, self.fake_globals = languages.code_parsers[self.language](real_code_lines)

    def create_obf_functions(self):

        # Created the obfuscated code base
        self.obfuscated_functions = languages.code_generators[self.language](self.config, self.real_code, self.fake_globals)

    def output_obfuscated_code(self, output_path):

        # Create the list of all globals
        full_globals = self.real_code["globals"]
        for i in range(len(self.fake_globals)):
            full_globals.append(self.fake_globals[i]["line"])
        #random.shuffle(full_globals)

        with open(output_path, "w") as f:
            f.write("%s\n\n" % "\n".join(self.real_code["imports"]))
            f.write("%s\n\n" % "\n".join(full_globals))
            f.write("%s\n\n" % "\n".join(self.obfuscated_functions))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Create an obfuscated piece of code")
    parser.add_argument('-l', '--language', dest='language', default="cpp",
                        choices=['ansi_c', 'asm_32', 'asm_64', 'cpp', 'delphi', 'golang', 'python'],
                        help='the language you want to generate obfuscated code in')
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='the filename you want to output to')
    parser.add_argument('-c', '--code', dest='code', required=True,
                        help='the path to the file containing your real code')
    parser.add_argument('-a', '--arch', dest='arch', default="Win_x86",
                        choices=['Win_x86', 'Win_x64', 'POSIX_x86', 'POSIX_x64'], help='the architecture to target')
    return parser.parse_args()


def main():

    args = parse_arguments()

    obf = Obfusion(args.arch, args.language, args.code, args.output, run=True)

    del obf
"""
    # Get a list of the real code lines
    with open(args.code, "r") as real_code_file:
        real_code_lines = real_code_file.readlines()

    # Create the fake global variables
    real_code, fake_globals = languages.code_parsers[args.language](real_code_lines)

    # Created the obfuscated code base
    obfuscated_functions = languages.code_generators[args.language](real_code, fake_globals)

    # Create the list of all globals
    full_globals = real_code["globals"]
    for i in range(len(fake_globals)):
        full_globals.append(fake_globals[i]["line"])
    #random.shuffle(full_globals)

    with open("temp.c", "w") as code_file:

        for i in range(len(real_code["imports"])):
            code_file.write("%s\n" % real_code["imports"][i])
        code_file.write("\n")

        for i in range(len(full_globals)):
            code_file.write("%s\n" % full_globals[i])
        code_file.write("\n")

        for i in range(len(obfuscated_functions)):
            code_file.write("%s\n" % obfuscated_functions[i])
        code_file.write("\n")

    if args.type == "code":
        if os.path.isfile(args.filename):
            os.remove(args.filename)
        os.rename("temp.c", args.filename)
    elif args.type == "binary":
        if args.language == "cpp":
            os.system("tcc.exe temp.c -o %s" % args.filename)
"""

if __name__ == "__main__":
    main()