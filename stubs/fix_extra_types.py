import os
import re
from enum import IntEnum


def fix_types(doc: str):
    pass

root = os.path.dirname(os.path.dirname(__file__))

print("current directory: " + root)
src_path = os.path.join(root, "stubs", "temp.pyi")
out_path = os.path.join(root, "stubs", "temp_fixed.pyi")

# script to read this file line by line and only print first 5 lines:

def read_large_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            yield line.rstrip('\n')

ENUM_CLASS_REGEX = r"^class\s+(\w+)\s*\((GObject\.GEnum|GObject\.GFlags)\):"

STATE_NONE = 0
STATE_INIT = 1
STATE_PROC = 2

class A(IntEnum):
    a = 1
    b = 2
    c = 3

def hello(x: A, b: A):
    pass

hello(A.a, A.b)

class CustomInterpreter:
    def __init__(self):
        self.is_class: int = False
        self.is_enum_class: int = False

        self.indent_level = 0

    def process(self, line: str):
        if self.is_class:
            if self.is_enum_class:
                line = self.handle_enum_class(line)
        else:
            self.check_class(line)

        return line

    def handle_enum_class(self, line: str):
        return line.lower()

    def check_class(self, line: str):
        if line.startswith("class "):
            print("Class found: " + line)
            self.is_class = True

            if re.match(ENUM_CLASS_REGEX, line):
                self.is_enum_class = True
                print("Enum class found: " + line)
            #
            # if "Enum" in line:
            #     self.is_enum_class = True
            # else:
            #     self.is_enum_class = False
        else:
            self.is_class = False
            self.is_enum_class = False

def process():
    count = 0
    interpreter = CustomInterpreter()

    with open(out_path, 'w', encoding='utf-8') as out_file:
        for line in read_large_file(src_path):
            modified_line = interpreter.process(line)
            # modified_line = process_line(line)
            # print(modified_line)
            out_file.write(modified_line + '\n')

            count += 1
            if count > 50:
                break


process()
