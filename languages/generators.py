import math
import random
import string


class VarGenerators:
    def __init__(self):
        pass

    @staticmethod
    def init_pythonic_int32():
        val = random.choice([1, -1]) * random.randint(0, math.pow(2, 16))
        return {"value": val, "size": 4}

    @staticmethod
    def init_pythonic_float():
        val = random.choice([1, -1]) * random.uniform(float(0), float(math.pow(2, 16)))
        return {"value": val, "size": 4}

    @staticmethod
    def init_pythonic_ascii_char():
        val = random.randint(0, 255)

        val_str = chr(val)
        if (val <= 0x20) or (val >= 0x7F) or (val_str in ["\\", "\"", "\'"]):
            val_str = "\'\\x{:02X}\'".format(val)
        else:
            val_str = "\'{}\'".format(val_str)

        return {"value": val_str, "size": 1}

    @staticmethod
    def init_pythonic_ascii_string():
        val = "\"{}\"".format(VarGenerators.random_alphanum(random.randint(5, 25)))
        return {"value": val, "size": len(val)}

    @staticmethod
    def init_pythonic_list_int():
        s = random.randint(1, 10)
        v = [VarGenerators.init_pythonic_int32()["value"] for _ in range(s)]
        val = "[{}]".format(", ".join(map(str, v)))
        return {"value": val, "size": 0}

    @staticmethod
    def init_pythonic_list_string():
        s = random.randint(1, 10)
        v = [VarGenerators.random_alphanum(random.randint(5, 25)) for _ in range(s)]
        val = "[\"{}\"]".format("\", \"".join(v))
        return {"value": val, "size": 0}

    @staticmethod
    def init_pythonic_dict_string_int():
        val = "{}"
        return {"value": val, "size": 0}

    @staticmethod
    def init_pythonic_dict_string_string():
        val = "{}"
        return {"value": val, "size": 0}

    @staticmethod
    def init_c_stack_string():
        str_val = VarGenerators.random_alphanum(random.randint(5, 25))
        val = "{{\'{}\', \'\\x0\'}}".format("\', \'".join(list(str_val)))
        return {"value": val, "size": len(str_val)}

    @staticmethod
    # Generate a random alphanumeric string
    def random_alphanum(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)).replace("\\", "\\\\")

    @staticmethod
    def random_lower_alphanum(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)).replace("\\", "\\\\").lower()