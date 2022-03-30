from util.command_utility import CommandUtility
from util.date_utility import DateUtility
from util.string_utility import StringUtility

class MegaService:


    def match(self, url):
        regex = r"(?P<url>https?://mega.nz/(folder|file)/[^\s]+)"
        return StringUtility().match_text(regex, url)


    def download(self, url, dest):
        cmds = []
        if "folder" in url:
            dest = dest + "/MegaFolder" + DateUtility.get_current_string_time() + "/"
            mkdir_cmd = "mkdir -m 777 -p " + dest
            cmds.append(mkdir_cmd)
        dl_cmd = "megadl --path " + dest + " " + url
        cmds.append(dl_cmd)
        return CommandUtility.exec_subprocess_cmd(cmds, True)
