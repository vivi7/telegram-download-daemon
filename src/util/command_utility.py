import os, subprocess, multiprocessing, signal, string, random


class CommandUtility:


    @staticmethod
    def exec_subprocess_cmd(cmd_arr, decode=False):
        cmds = ";".join(cmd_arr)
        output_bytes = subprocess.run(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
        if decode:
            return output_bytes.decode("utf-8")
        else:
            return output_bytes

    @staticmethod
    def check_subprocess_cmd(cmd_arr, decode=False):
        cmds = ";".join(cmd_arr)
        output_bytes = subprocess.check_output(cmds, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
        if decode:
            return output_bytes.decode("utf-8")
        else:
            return output_bytes

    @staticmethod
    def exec_custom_list_cmd(folder_path):
        date = CommandUtility.exec_subprocess_cmd(["date"], True)
        data_list = CommandUtility.exec_subprocess_cmd(["ls -lh " + folder_path + " | cut -d ' ' -f 6- "], True)
        data_size = CommandUtility.exec_subprocess_cmd(["du -sh " + folder_path], True)
        return (
            "Now: " + date +
            data_list + "\n" +
            "Total size: " +
            data_size
        )

    @staticmethod
    def get_cpu_count():
        return multiprocessing.cpu_count()