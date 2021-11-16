from os import getenv, path
from telethon.sessions import StringSession

TELEGRAM_DAEMON_SESSION_PATH = getenv("TELEGRAM_DAEMON_SESSION_PATH")
session_name = "DownloadDaemon"
string_session_file_name = "{0}.session".format(session_name)


def should_get_string_session():
    sessio_path = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                            string_session_file_name)
    if path.isfile(sessio_path):
        with open(sessio_path, 'r') as file:
            session = file.read()
            print("Session loaded from {0}".format(sessio_path))
            return session
    return None


def get_session():
    if TELEGRAM_DAEMON_SESSION_PATH == None:
        return session_name

    return StringSession(should_get_string_session())


def save_session(session):
    if TELEGRAM_DAEMON_SESSION_PATH != None:
        sessio_path = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                                string_session_file_name)
        with open(sessio_path, 'w') as file:
            file.write(StringSession.save(session))
        print("Session saved in {0}".format(sessio_path))
