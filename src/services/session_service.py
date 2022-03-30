import os
from telethon.sessions import StringSession


class SessionService:


    def __init__(self, path):
        self.location_path = path
        self.name = "TDD"
        self.string_file_name = "{0}.session".format(self.name)


    def _should_get_string_session(self):
        session_path = os.path.join(self.location_path, self.string_file_name)
        if os.path.isfile(session_path):
            with open(session_path, "r") as file:
                session = file.read()
                print("Session loaded from {0}".format(session_path))
                return session
        return None


    def get(self):
        if self.location_path == None:
            return self.name

        return StringSession(self._should_get_string_session())


    def save(self, session):
        if self.location_path != None:
            session_path = os.path.join(self.location_path, self.string_file_name)
            os.makedirs(self.location_path, exist_ok=True)
            with open(session_path, "w") as file:
                file.write(StringSession.save(session))
            print("Session saved in {0}".format(session_path))
