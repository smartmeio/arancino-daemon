import serialasyncmod3 as mod

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

datastore = mod.connectDatastore()
datastore.flushdb()

def test_set():

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: SET" + bcolors.ENDC)

    test_cmd = "SET" + mod.CHR_SEP + "set-key" + mod.CHR_SEP + "set-key"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_get_1():

    datastore.set("set-key","set-value")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: GET 1" + bcolors.ENDC)

    test_cmd = "GET" + mod.CHR_SEP + "set-key"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    val = datastore.get("set-key")

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_SEP + val + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_get_2():
    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: GET 2" + bcolors.ENDC)

    test_cmd = "GET" + mod.CHR_SEP + "not-existing-key"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP,"#").replace(mod.CHR_EOT,"@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP,"#").replace(mod.CHR_EOT,"@"))

    if test_response == mod.ERR_NULL + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_del_1():

    datastore.set("del-key-1", "del-value-1")
    datastore.set("del-key-2", "del-value-2")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: DEL 1" + bcolors.ENDC)

    test_cmd = "DEL" + mod.CHR_SEP + "del-key-1" + mod.CHR_SEP + "del-key-2"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP,"#").replace(mod.CHR_EOT,"@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP,"#").replace(mod.CHR_EOT,"@"))

    if test_response == mod.RSP_OK + mod.CHR_SEP + "2" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_del_2():

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: DEL 2" + bcolors.ENDC)

    test_cmd = "DEL" + mod.CHR_SEP + "not-existing-key"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    if test_response == mod.RSP_OK + mod.CHR_SEP + "0" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_keys_1():

    datastore.set("key-1", "value-1")
    datastore.set("key-2", "value-2")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: KEYS 1" + bcolors.ENDC)

    test_cmd = "KEYS"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()
    #datastore.delete(*["key-1","key-2"])

    if test_response == mod.RSP_OK + mod.CHR_SEP + "key-2" + mod.CHR_SEP + "key-1" + mod.CHR_EOT or \
            test_response == mod.RSP_OK + mod.CHR_SEP + "key-1" + mod.CHR_SEP + "key-2" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_keys_2():

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: KEYS 2" + bcolors.ENDC)

    datastore.set("key-1", "value-1")
    datastore.set("key-2", "value-2")
    datastore.set("other-key", "other-value")

    test_cmd = "KEYS" + mod.CHR_SEP + "key*"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_SEP + "key-2" + mod.CHR_SEP + "key-1" + mod.CHR_EOT or \
            test_response == mod.RSP_OK + mod.CHR_SEP + "key-1" + mod.CHR_SEP + "key-2" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)

def test_keys_3():

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: KEYS 3" + bcolors.ENDC)

    test_cmd = "KEYS" + mod.CHR_SEP + "non-existing-key"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    if test_response == mod.RSP_OK + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hset_1():
    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HSET 1" + bcolors.ENDC)

    test_cmd = "HSET" + mod.CHR_SEP + "hkey-1" + mod.CHR_SEP + "hfield-1" + mod.CHR_SEP + 'hvalue-1'
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_HSET_NEW + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hset_2():

    datastore.hset("hkey-1", "hfield-1", "hvalue-1")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HSET 2" + bcolors.ENDC)

    test_cmd = "HSET" + mod.CHR_SEP + "hkey-1" + mod.CHR_SEP + "hfield-1" + mod.CHR_SEP + "hvalue-1"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_HSET_UPD + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hget():

    datastore.hset("hkey-1", "hfield-1", "hvalue-1")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HGET" + bcolors.ENDC)

    test_cmd = "HGET" + mod.CHR_SEP + "hkey-1" + mod.CHR_SEP + "hfield-1"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_SEP + "hvalue-1" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hgetall():

    datastore.hset("hkey-1", "hfield-1", "hvalue-1")
    datastore.hset("hkey-1", "hfield-2", "hvalue-2")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HGETALL" + bcolors.ENDC)

    test_cmd = "HGETALL" + mod.CHR_SEP + "hkey-1"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_SEP + "hfield-1" + mod.CHR_SEP + "hvalue-1" + mod.CHR_SEP + "hfield-2" + mod.CHR_SEP + "hvalue-2" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hkeys():

    datastore.hset("hkey-1", "hfield-1", "hvalue-1")
    datastore.hset("hkey-1", "hfield-2", "hvalue-2")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HKEYS" + bcolors.ENDC)

    test_cmd = "HGETALL" + mod.CHR_SEP + "hkey-1"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_SEP + "hfield-1" + mod.CHR_SEP + "hvalue-1" + mod.CHR_SEP + "hfield-2" + mod.CHR_SEP + "hvalue-2" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hdel_1():
    datastore.hset("hkey-1", "hfield-1", "hvalue-1")

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HDEL 1" + bcolors.ENDC)

    test_cmd = "HDEL" + mod.CHR_SEP + "hkey-1" + mod.CHR_SEP + "hfield-1"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    datastore.flushdb()

    if test_response == mod.RSP_OK + mod.CHR_SEP + "1" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


def test_hdel_2():

    print("-----------------------------------------------------------------")
    print(bcolors.BOLD + "TEST: HDEL 2" + bcolors.ENDC)

    test_cmd = "HDEL" + mod.CHR_SEP + "hkey-1" + mod.CHR_SEP + "hfield-1"
    cmd = mod.__parseCommands(test_cmd)
    test_response = mod.__execCommand(cmd)

    print("MCU CMD: " + test_cmd.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))
    print("LR RSP: " + test_response.replace(mod.CHR_SEP, "#").replace(mod.CHR_EOT, "@"))

    if test_response == mod.RSP_OK + mod.CHR_SEP + "0" + mod.CHR_EOT:
        print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "FAILED" + bcolors.ENDC)
        exit(1)


test_set()
test_get_1()
test_get_2()
test_del_1()
test_del_2()
test_keys_1()
test_keys_2()
test_keys_3()
test_hset_1()
test_hset_2()
test_hget()
test_hgetall()
test_hkeys()
test_hdel_1()