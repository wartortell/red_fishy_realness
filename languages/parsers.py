

class CodeParsers:
    def __init__(self):
        pass

    @staticmethod
    def get_tab_count(line):
        tab_count = 0
        pos = 0
        while ((pos+4) < len(line)) and (line[pos:pos+4] == "    "):
            tab_count += 1
            pos += 4
        return tab_count

    @staticmethod
    def find_tab_code_block(**kwargs):
        line_index = kwargs["index"]
        code_block = kwargs["code_block"]
        tab_count = kwargs["tab_count"]

        while line_index < len(code_block):
            # Ignore empty lines
            if (not (code_block[line_index].strip() == "")) and \
                    (CodeParsers.get_tab_count(code_block[line_index]) <= tab_count):
                break

            line_index += 1

        return line_index

    @staticmethod
    def find_bracket_code_block(**kwargs):
        code_block = kwargs["code_block"]
        index = kwargs["index"]

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