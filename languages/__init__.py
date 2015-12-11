__author__ = 'wartortell'

from ansi_c import ObfuserAnsiC
from asm_32 import ObfuserAsm32
from asm_64 import ObfuserAsm64
from cpp import ObfuserCPP
from delphi import ObfuserDelphi
from golang import ObfuserGolang
from python import ObfuserPython

obfusion_classes = {"ansi_c": ObfuserAnsiC,
                    "asm_32": ObfuserAsm32,
                    "asm_64": ObfuserAsm64,
                    "cpp": ObfuserCPP,
                    "delphi": ObfuserDelphi,
                    "golang": ObfuserGolang,
                    "python": ObfuserPython}

#code_parsers = {"cpp": cpp.parse_real_code,
#                "delphi": delphi.parse_real_code}

#code_generators = {"cpp": cpp.create_code,
#                   "delphi": delphi.create_code}
