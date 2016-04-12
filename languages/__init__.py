__author__ = 'wartortell'

from ansi_c import FishierAnsiC
from asm_32 import FishierAsm32
from asm_64 import FishierAsm64
from cpp import FishierCpp
from delphi import FishierDelphi
from golang import FishierGolang
from java import FishierJava
from perl import FishierPerl
from python import FishierPython
from python27 import FishierPython27

fishiers = {"ansi_c": FishierAnsiC,
            "asm_32": FishierAsm32,
            "asm_64": FishierAsm64,
            "cpp": FishierCpp,
            "delphi": FishierDelphi,
            "golang": FishierGolang,
            "java": FishierJava,
            "perl": FishierPerl,
            "python": FishierPython,
            "python27": FishierPython27}
