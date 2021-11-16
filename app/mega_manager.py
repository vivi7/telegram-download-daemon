import re, os
from utility_manager import exec_subprocess_cmd, get_current_string_time

def is_mega_url(url):
    regex = (r'(?P<url>https?://mega.nz/(folder|file)/[^\s]+)')
    return re.match(regex, url)

def download_mega_url(url, dest):
    cmds=[]
    if 'folder' in url:
        dest = dest + "/MegaFolder" + get_current_string_time() + "/"
        mkdir_cmd = "mkdir -p " + dest
        cmds.append(mkdir_cmd)
    dl_cmd = 'megadl --path ' + dest + ' ' + url
    cmds.append(dl_cmd)
    return exec_subprocess_cmd(cmds, True)
