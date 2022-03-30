#!/usr/bin/env python3

import os, traceback
from shutil import move
import math
from mimetypes import guess_extension
import asyncio

from telethon import TelegramClient, events
from telethon.tl.types import (
    PeerChannel,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
)

import logging

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s]\t%(module)s -> %(funcName)s(%(lineno)d)\t\t%(name)s \n\t\t%(message)s\n", 
    level=logging.INFO
)

from util.command_utility import CommandUtility
from util.date_utility import DateUtility
from util.string_utility import StringUtility

from services.session_service import SessionService

from usecases.download_usecase import DownloadUsecase

from adapters.parser_adapter import ParserAdapter

TDD_VERSION = "5.0"
TELEGRAM_DAEMON_TEMP_SUFFIX = "tdd"

print("Telegram Download Daemon " + TDD_VERSION)

parser_adapter = ParserAdapter()
args = parser_adapter.get_args()

api_id = args.api_id
api_hash = args.api_hash
channel_id = args.channel
bot_token = args.bot_token

download_folder = args.dest
temp_folder = args.temp
session_folder = args.session
duplicates = args.duplicates

session_service = SessionService(session_folder)


with TelegramClient(session_service.get(), api_id, api_hash, proxy=None).start(bot_token=bot_token) as client:
    session_service.save(client.session)

    queue = asyncio.Queue()
    peer_channel = PeerChannel(channel_id)

    download_usecase = DownloadUsecase()

    worker_count = CommandUtility.get_cpu_count()

    in_progress = {}
    update_frequency = 10
    last_update = 0


    def hello_message():
        return (
            "Telegram Download Daemon " + TDD_VERSION + "\n" +
            "You can download:" + "\n" +
            "- Files" + "\n" +
            "- Youtube Video" + "\n" +
            "- Mega.nz" + "\n" +
            "- Direct file urls" + "\n" +
            "(Remember: Urls can be contained in text and merged in a single message)\n" + "\n" +
            "READY!"
        )


    async def set_progress(filename, message, received, total):
        global last_update
        global update_frequency

        if received >= total:
            try:
                in_progress.pop(filename)
            except:
                pass
            return
        percentage = math.trunc(received / total * 10000) / 100

        progress_message = "{0}\n{1} % ({2} / {3})".format(
            filename, percentage, received, total
        )
        in_progress[filename] = progress_message

        current_time = DateUtility.get_current_timestamp()
        if (current_time - last_update) > update_frequency:
            await log_reply(message, progress_message)
            last_update = current_time


    async def send_message(client, peer_channel, message):
        # dialogs = await client.get_dialogs()
        entity = await client.get_entity(peer_channel)
        await client.send_message(entity, message)


    async def log_reply(message, reply):
        if len(reply) > 4096:
            for x in range(0, len(reply), 4096):
                await message.reply_text(reply[x:x+4096])
        else:
            await message.edit(reply)


    def get_filename(event: events.NewMessage.Event):
        media_file_name = "unknown"

        if hasattr(event.media, "photo"):
            media_file_name = str(event.media.photo.id) + ".jpeg"
        elif hasattr(event.media, "webpage"):
            media_file_name = str(event.media.webpage.id) + ".web"
        elif hasattr(event.media, "document"):
            for attribute in event.media.document.attributes:
                if isinstance(attribute, DocumentAttributeFilename):
                    media_file_name = attribute.file_name
                    break
                if isinstance(attribute, DocumentAttributeVideo):
                    if event.original_update.message.message != "":
                        media_file_name = event.original_update.message.message
                    else:
                        media_file_name = str(event.message.media.document.id)
                    media_file_name += guess_extension(
                        event.message.media.document.mime_type
                    )

        media_file_name = "".join(
            c for c in media_file_name if c.isalnum() or c in "()._- "
        )

        return media_file_name


    def exec_command(command):
        is_known_command = False
        output = "Unknown command"
        if command == "list":
            is_known_command = True
            output = CommandUtility.exec_custom_list_cmd(download_folder)
        elif command == "clean":
            is_known_command = True
            data_clear = CommandUtility.exec_subprocess_cmd(["rm {0}/*.{1}".format(temp_folder, TELEGRAM_DAEMON_TEMP_SUFFIX)], True)
            output = ("Cleaning " + temp_folder + "\n" + data_clear)
        elif command == "status":
            is_known_command = True
            output = "".join([
                    "{0}: {1}\n".format(key, value)
                    for (key, value) in in_progress.items()
                ])
            if output:
                output = "Active downloads:\n\n" + output
            else:
                output = "No active downloads"
        elif command == "date":
            is_known_command = True
            output = CommandUtility.exec_subprocess_cmd(["date"], True)
        else:
            output = "Available commands: list, clean, status, date"

        return is_known_command, output


    async def download_media(client, event, dest_file_path, download_callback):
        await client.download_media(
            event.message,
            dest_file_path,
            progress_callback=download_callback,
        )


    async def download_file(event, message):
        full_file_name = get_filename(event)
        file_name, file_ext = os.path.splitext(full_file_name)
        tempfilename = file_name + "-" + StringUtility.get_random_id(8) + file_ext

        if os.path.exists(
            "{0}/{1}.{2}".format(temp_folder, tempfilename, TELEGRAM_DAEMON_TEMP_SUFFIX)
        ) or os.path.exists("{0}/{1}".format(download_folder, full_file_name)):
            if duplicates == "rename":
                full_file_name = tempfilename

        if hasattr(event.media, "photo"):
            size = 0
        else:
            size = event.media.document.size

        await log_reply(message, "Downloading file {0} ({1} bytes)".format(full_file_name, size))
        download_callback = lambda received, total: set_progress(
            full_file_name, message, received, total
        )
        await download_media(client, event, "{0}/{1}.{2}".format(temp_folder, full_file_name, TELEGRAM_DAEMON_TEMP_SUFFIX), download_callback)
        set_progress(full_file_name, message, 100, 100)
        move(
            "{0}/{1}.{2}".format(temp_folder, full_file_name, TELEGRAM_DAEMON_TEMP_SUFFIX),
            "{0}/{1}".format(download_folder, full_file_name),
        )
        return full_file_name


    @client.on(events.NewMessage())
    async def handler(event):
        logging.info(event)
        if event.to_id != peer_channel:
            return
        try:
            if hasattr(event.media, "document") or hasattr(event.media, "photo"):
                filename = get_filename(event)
                if (
                    os.path.exists(
                        "{0}/{1}.{2}".format(temp_folder, filename, TELEGRAM_DAEMON_TEMP_SUFFIX)
                    )
                    or os.path.exists("{0}/{1}".format(download_folder, filename))
                ) and duplicates == "ignore":
                    message = await event.reply("{0} already exists. Ignoring it.".format(filename))
                else:
                    message = await event.reply("{0} added to queue".format(filename))
                    await queue.put([event, message])
            elif hasattr(event.media, "webpage") or StringUtility.contains_url(event.message.message):
                urls = StringUtility.extract_urls(event.message.message)
                for url in urls:
                    message = await event.reply("{0} is downloading".format(url))
                    await queue.put([event, message, url])
                if len(urls) > 1:
                    message = await event.reply("{0}\nARE DOWNLOADED!".format(event.message.message))
            else:
                command = event.message.message.lower()
                is_known_command, output = exec_command(command)

                await log_reply(event, output)
                if is_known_command:
                    message = await event.reply(output)
                else:
                    message = await event.reply("That is not downloadable. {0}".format(output))

        except Exception as e:
            print(traceback.format_exc())

    async def worker():
        while True:
            try:
                element = await queue.get()
                event = element[0]
                message = element[1]

                if hasattr(event.media, "document") or hasattr(event.media, "photo"):
                    filename = await download_file(event, message)
                elif hasattr(event.media, "webpage") or StringUtility.contains_url(element[2]):
                    filename = await download_usecase.donload_file_from_url(element[2], download_folder)
                else:
                    print("This is not possible to happen, check elements:", element)

                await log_reply(message, "{0} ready".format(filename))
                queue.task_done()
            except Exception as e:
                try:
                    await log_reply(message, "Error: {}".format(str(e)))
                except:
                    pass
                print(traceback.format_exc())

    async def start():
        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(worker_count):
            task = loop.create_task(worker())
            tasks.append(task)
        await send_message(client, peer_channel, hello_message())
        await client.run_until_disconnected()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    client.loop.run_until_complete(start())

