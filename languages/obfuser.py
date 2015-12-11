import string
import random


class Obfuser:
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

        # The size of tabs in the code
        self.tab_size = "    "

        # The difficulty of the obfuscator, can be ramped up and down for more red herring code
        self.difficulty = 5

    def create_code(self):
        pass

    def fill_obfuscated_code(self, code_block):
        pass

    def fill_code_string(self, code_block, tab_count):
        pass

    # Generate a random alphanumeric string
    def random_alphanum(self, length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)).replace("\\", "\\\\")

    def random_lower_alphanum(self, length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)).replace("\\", "\\\\").lower()

