import os

from realness import RedFishRealness


def test_perl():
    print "Testing Perl..."

    test_path = os.path.join("tests", "Perl")
    old_code = os.path.join(test_path, "test.pl")
    new_code = os.path.join(test_path, "did_eet.pl")

    RedFishRealness("x86", "perl", old_code, new_code, 2, True)

    test_output = os.path.join(test_path, "output.txt")

    old_test = "perl {} > {}".format(old_code, test_output)
    print "Original Test:   {}".format(old_test)

    os.system(old_test)
    with open(test_output, "r") as f:
        old = f.read().strip()

    new_test = "perl {} > {}".format(new_code, test_output)
    print "Obfuscated Test: {}".format(new_test)

    os.system(new_test)
    with open(test_output, "r") as f:
        new = f.read().strip()

    if not (old == new):
        print "Test Failed!"
        print "Old:\n{}\nNew:\n{}".format(old, new)
        return 0
    else:
        print "Test success!"
        print "Output:\n{}\n".format(old)
        return 1


def test_python27():
    print "Testing Python27..."

    test_path = os.path.join("tests", "Python27")
    old_code = os.path.join(test_path, "do_eet.py")
    new_code = os.path.join(test_path, "did_eet.py")

    RedFishRealness("x86", "python27", old_code, new_code, 3, True)

    test_binary = os.path.join(test_path, "MpSvc.dll")
    test_output = os.path.join(test_path, "output.txt")

    old_test = "python {} {} > {}".format(old_code, test_binary, test_output)
    print "Original Test:   {}".format(old_test)

    os.system(old_test)
    with open(test_output, "r") as f:
        old = f.read().strip()

    new_test = "python {} {} > {}".format(new_code, test_binary, test_output)
    print "Obfuscated Test: {}".format(new_test)

    os.system(new_test)
    with open(test_output, "r") as f:
        new = f.read().strip()

    if not (old == new):
        print "Test Failed!"
        print "Old:\n{}\nNew:\n{}".format(old, new)
        return 0
    else:
        print "Test success!"
        print "Output:\n{}\n".format(old)
        return 1


def test_ansi_c():
    print "Testing Ansi_C..."

    test_path = os.path.join("tests", "Ansi_C")
    old_code = os.path.join(test_path, "test.c")
    old_executable = os.path.join(test_path, "test.exe")
    new_code = os.path.join(test_path, "did_eet.c")
    new_executable = os.path.join(test_path, "did_eet.exe")

    RedFishRealness("x86", "ansi_c", old_code, new_code, 3, True)

    test_output = os.path.join(test_path, "output.txt")

    old_test_compile = "{} {} -o {}".format(os.path.join("tests", "tcc", "tcc.exe"), old_code, old_executable)
    old_test_execute = "{} > {}".format(old_executable, test_output)

    print old_test_compile

    os.system(old_test_compile)
    os.system(old_test_execute)
    with open(test_output, "r") as f:
        old = f.read().strip()

    new_test_compile = "{} {} -o {}".format(os.path.join("tests", "tcc", "tcc.exe"), new_code, new_executable)
    new_test_execute = "{} > {}".format(new_executable, test_output)

    os.system(new_test_compile)
    os.system(new_test_execute)

    with open(test_output, "r") as f:
        new = f.read().strip()

    if not (old == new):
        print "Test Failed!"
        print "Old:\n{}\nNew:\n{}".format(old, new)
        return 0
    else:
        print "Test success!"
        print "Output:\n{}\n".format(old)
        return 1


def test_go():
    print "Testing GoLang..."

    test_path = os.path.join("tests", "Golang")
    old_code = os.path.join(test_path, "test.go")
    old_executable = os.path.join(test_path, "test.exe")
    new_code = os.path.join(test_path, "did_eet.go")
    new_executable = os.path.join(test_path, "did_eet.exe")

    RedFishRealness("x86", "golang", old_code, new_code, 3, True)

    test_output = os.path.join(test_path, "output.txt")

    old_test_compile = "go build -o {} {}".format(old_executable, old_code)
    old_test_execute = "{} > {}".format(old_executable, test_output)

    os.system(old_test_compile)
    os.system(old_test_execute)
    with open(test_output, "r") as f:
        old = f.read().strip()

    new_test_compile = "go build -o {} {}".format(new_executable, new_code)
    new_test_execute = "{} > {}".format(new_executable, test_output)

    os.system(new_test_compile)
    os.system(new_test_execute)

    with open(test_output, "r") as f:
        new = f.read().strip()

    if not (old == new):
        print "Test Failed!"
        print "Old:\n{}\nNew:\n{}".format(old, new)
        return 0
    else:
        print "Test success!"
        print "Output:\n{}\n".format(old)
        return 1


tests = [test_go, test_python27, test_ansi_c, test_perl]

bad_tests = []
success = 0
for i in range(len(tests)):
    s = tests[i]()
    success += s
    if not s:
        bad_tests.append(tests[i].__name__)

print "{}/{} tests succeeded!".format(success, len(tests))
print "Bad Tests: {}".format(bad_tests)
