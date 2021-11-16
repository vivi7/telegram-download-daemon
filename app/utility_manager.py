import os, subprocess, string, random
from datetime import datetime

def get_current_time():
    return datetime.now()

def get_current_string_time(format = "%Y%m%d%H%M%S"):
    return get_current_time().strftime(format)

def get_current_timestamp():
    return datetime.timestamp(get_current_time())

def get_random_id(len):
    chars=string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for x in range(len))

def exec_subprocess_cmd(cmd_arr, decode = False):
    cmds = ';'.join(cmd_arr)
    print(cmds)
    if decode:
        return subprocess.run(cmds, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.decode('utf-8')
    else:
        return subprocess.run(cmds, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
