import os
import argparse


class ParserAdapter:


    def __init__(self):
        TELEGRAM_DAEMON_API_ID = os.getenv("TELEGRAM_DAEMON_API_ID")
        TELEGRAM_DAEMON_API_HASH = os.getenv("TELEGRAM_DAEMON_API_HASH")
        TELEGRAM_DAEMON_CHANNEL = os.getenv("TELEGRAM_DAEMON_CHANNEL")
        TELEGRAM_DAEMON_BOT_TOKEN = os.getenv("TELEGRAM_DAEMON_BOT_TOKEN")
        TELEGRAM_DAEMON_SESSION = os.getenv("TELEGRAM_DAEMON_SESSION", "/telegram-downloads/TEMP")
        TELEGRAM_DAEMON_DEST = os.getenv("TELEGRAM_DAEMON_DEST", "/telegram-downloads")
        TELEGRAM_DAEMON_TEMP = os.getenv("TELEGRAM_DAEMON_TEMP", "/telegram-downloads/TEMP")
        TELEGRAM_DAEMON_DUPLICATES = os.getenv("TELEGRAM_DAEMON_DUPLICATES", "rename")

        self.parser = argparse.ArgumentParser(
            description="Script to download files from a Telegram Channel."
        )
        self.parser.add_argument(
            "--api-id",
            required=TELEGRAM_DAEMON_API_ID == None,
            type=int,
            default=TELEGRAM_DAEMON_API_ID,
            help="api_id from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_ID env var)",
        )
        self.parser.add_argument(
            "--api-hash",
            required=TELEGRAM_DAEMON_API_HASH == None,
            type=str,
            default=TELEGRAM_DAEMON_API_HASH,
            help="api_hash from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_HASH env var)",
        )
        self.parser.add_argument(
            "--session",
            type=str,
            default=TELEGRAM_DAEMON_SESSION,
            help="Session path for store telegram session (default is /telegram-downloads/TEMP).",
        )
        self.parser.add_argument(
            "--dest",
            type=str,
            default=TELEGRAM_DAEMON_DEST,
            help="Destination path for downloaded files (default is /telegram-downloads).",
        )
        self.parser.add_argument(
            "--temp",
            type=str,
            default=TELEGRAM_DAEMON_TEMP,
            help="Destination path for temporary files (default is /telegram-downloads/TEMP).",
        )
        self.parser.add_argument(
            "--channel",
            required=TELEGRAM_DAEMON_CHANNEL == None,
            type=int,
            default=TELEGRAM_DAEMON_CHANNEL,
            help="Channel id to download from it (default is TELEGRAM_DAEMON_CHANNEL env var",
        )
        self.parser.add_argument(
            "--bot_token",
            required=TELEGRAM_DAEMON_BOT_TOKEN == None,
            type=str,
            default=TELEGRAM_DAEMON_BOT_TOKEN,
            help="Bot token added in the channel to allow it to download files (default is TELEGRAM_DAEMON_BOT_TOKEN env var",
        )
        self.parser.add_argument(
            "--duplicates",
            choices=["ignore", "rename", "overwrite"],
            type=str,
            default=TELEGRAM_DAEMON_DUPLICATES,
            help='"ignore"=do not download duplicated files, "rename"=add a random suffix, "overwrite"=redownload and overwrite.',
        )


    def get_args(self):
        return self.parser.parse_args()

