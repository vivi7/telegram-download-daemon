#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

from os import getenv, path
from shutil import move
import math
import os.path
from mimetypes import guess_extension

from utility_manager import get_random_id, get_current_timestamp, exec_subprocess_cmd
from session_manager import get_session, save_session
from youtube_manager import is_youtube_url, download_youtube_video
from mega_manager import is_mega_url, download_mega_url
from scrubber_manager import contains_url, extract_urls, download_file_from_url

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, DocumentAttributeFilename, DocumentAttributeVideo
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',
                    level=logging.WARNING)

import multiprocessing
import argparse
import asyncio

TDD_VERSION="2.0"

TELEGRAM_DAEMON_API_ID = getenv("TELEGRAM_DAEMON_API_ID")
TELEGRAM_DAEMON_API_HASH = getenv("TELEGRAM_DAEMON_API_HASH")
TELEGRAM_DAEMON_CHANNEL = getenv("TELEGRAM_DAEMON_CHANNEL")
TELEGRAM_DAEMON_BOT_TOKEN = getenv("TELEGRAM_DAEMON_BOT_TOKEN")

TELEGRAM_DAEMON_SESSION_PATH = getenv("TELEGRAM_DAEMON_SESSION_PATH")

TELEGRAM_DAEMON_DEST=getenv("TELEGRAM_DAEMON_DEST", "/telegram-downloads")
TELEGRAM_DAEMON_TEMP=getenv("TELEGRAM_DAEMON_TEMP", "")
TELEGRAM_DAEMON_DUPLICATES=getenv("TELEGRAM_DAEMON_DUPLICATES", "rename")

TELEGRAM_DAEMON_TEMP_SUFFIX="tdd"

parser = argparse.ArgumentParser(
    description="Script to download files from a Telegram Channel.")
parser.add_argument(
    "--api-id",
    required=TELEGRAM_DAEMON_API_ID == None,
    type=int,
    default=TELEGRAM_DAEMON_API_ID,
    help=
    'api_id from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_ID env var)'
)
parser.add_argument(
    "--api-hash",
    required=TELEGRAM_DAEMON_API_HASH == None,
    type=str,
    default=TELEGRAM_DAEMON_API_HASH,
    help=
    'api_hash from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_HASH env var)'
)
parser.add_argument(
    "--dest",
    type=str,
    default=TELEGRAM_DAEMON_DEST,
    help=
    'Destination path for downloaded files (default is /telegram-downloads).')
parser.add_argument(
    "--temp",
    type=str,
    default=TELEGRAM_DAEMON_TEMP,
    help=
    'Destination path for temporary files (default is using the same downloaded files directory).')
parser.add_argument(
    "--channel",
    required=TELEGRAM_DAEMON_CHANNEL == None,
    type=int,
    default=TELEGRAM_DAEMON_CHANNEL,
    help=
    'Channel id to download from it (default is TELEGRAM_DAEMON_CHANNEL env var'
)
parser.add_argument(
    "--bot_token",
    required=TELEGRAM_DAEMON_BOT_TOKEN == None,
    type=str,
    default=TELEGRAM_DAEMON_BOT_TOKEN,
    help=
    'Bot token added in the channel to allow it to download files (default is TELEGRAM_DAEMON_BOT_TOKEN env var'
)
parser.add_argument(
    "--duplicates",
    choices=["ignore", "rename", "overwrite"],
    type=str,
    default=TELEGRAM_DAEMON_DUPLICATES,
    help=
    '"ignore"=do not download duplicated files, "rename"=add a random suffix, "overwrite"=redownload and overwrite.'
)
args = parser.parse_args()

api_id = args.api_id
api_hash = args.api_hash
channel_id = args.channel
bot_token = args.bot_token
download_folder = args.dest
temp_folder = args.temp
duplicates=args.duplicates
worker_count = multiprocessing.cpu_count()
update_frequency = 10
last_update = 0
#multiprocessing.Value('f', 0)

if not temp_folder:
    temp_folder = download_folder + "/TEMP"

# Edit these lines:
proxy = None

# End of interesting parameters

async def send_hello_message(client, peer_channel):
    # dialogs = await client.get_dialogs()
    entity = await client.get_entity(peer_channel)
    print("Telegram Download Daemon "+TDD_VERSION)
    await client.send_message(entity, "Telegram Download Daemon "+TDD_VERSION)
    await client.send_message(entity, 'You can download:\nFiles\nYoutube Video\nMega.nz\nDirect file urls')
    await client.send_message(entity, "Remember: Urls can be contained in text and merged in a single message")
    await client.send_message(entity, "Hi! I'm Ready!!!")
 

async def log_reply(message, reply):
    print(reply)
    await message.edit(reply)
    # await message.reply(reply)

def get_filename(event: events.NewMessage.Event):
    media_file_name = "unknown"

    if hasattr(event.media, 'photo'):
        media_file_name = str(event.media.photo.id)+".jpeg"
    elif hasattr(event.media, 'webpage'):
        media_file_name = str(event.media.webpage.id)+".web"
    elif hasattr(event.media, 'document'):
        for attribute in event.media.document.attributes:
            if isinstance(attribute, DocumentAttributeFilename): 
              media_file_name=attribute.file_name
              break     
            if isinstance(attribute, DocumentAttributeVideo):
              if event.original_update.message.message != '': 
                  media_file_name = event.original_update.message.message
              else:    
                  media_file_name = str(event.message.media.document.id)
              media_file_name+=guess_extension(event.message.media.document.mime_type)    
     
    media_file_name="".join(c for c in media_file_name if c.isalnum() or c in "()._- ")
      
    return media_file_name


in_progress={}

async def set_progress(filename, message, received, total):
    global last_update
    global update_frequency

    if received >= total:
        try: in_progress.pop(filename)
        except: pass
        return
    percentage = math.trunc(received / total * 10000) / 100

    progress_message= "{0}\n{1} % ({2} / {3})".format(filename, percentage, received, total)
    in_progress[filename] = progress_message

    current_time=get_current_timestamp()
    if (current_time - last_update) > update_frequency:
        await log_reply(message, progress_message)
        last_update=current_time

def exec_command(command):
    output = "Unknown command"
    if command == "list":
        output = exec_subprocess_cmd(["ls -l "+download_folder], True)
    elif command == "clean":
        output = "Cleaning "+temp_folder+"\n"
        output+=exec_subprocess_cmd(["rm "+temp_folder+"/*."+TELEGRAM_DAEMON_TEMP_SUFFIX])
    elif command == "status":
        try:
            output = "".join([ "{0}: {1}\n".format(key,value) for (key, value) in in_progress.items()])
            if output: 
                output = "Active downloads:\n\n" + output
            else: 
                output = "No active downloads"
        except:
            output = "Some error occured while checking the status. Retry."
    else:
        output = "Available commands: statusdebug, debug, list, clean, status"
    
    return output


with TelegramClient(get_session(), api_id, api_hash, proxy=proxy).start(bot_token=bot_token) as client:

    save_session(client.session)

    queue = asyncio.Queue()
    peer_channel = PeerChannel(channel_id)

    @client.on(events.NewMessage())
    async def handler(event):

        if event.to_id != peer_channel:
            return

        print(event)
        print('\n\n')
        
        try:
            if hasattr(event.media, 'document') or hasattr(event.media,'photo'):
                filename=get_filename(event)
                if ( path.exists("{0}/{1}.{2}".format(temp_folder,filename,TELEGRAM_DAEMON_TEMP_SUFFIX)) or path.exists("{0}/{1}".format(download_folder,filename)) ) and duplicates == "ignore":
                    message=await event.reply("{0} already exists. Ignoring it.".format(filename))
                else:
                    message=await event.reply("{0} added to queue".format(filename))
                    await queue.put([event, message])
            elif hasattr(event.media, 'webpage') or contains_url(event.message.message):
                urls = extract_urls(event.message.message)
                for url in urls:
                    message=await event.reply("{0} is downloading".format(url))
                    await queue.put([event, message, url])
                if len(urls) > 1:
                    message=await event.reply("{0}\nARE DOWNLOADED!".format(event.message.message))
            else:
                command = event.message.message.lower()
                output = exec_command(command)
                
                await log_reply(event, output)
                message=await event.reply("That is not downloadable. {0}".format(output))

        except Exception as e:
                print('Events handler error: ', e)

    async def worker():
        while True:
            try:
                element = await queue.get()
                event=element[0]
                message=element[1]

                if hasattr(event.media, 'document') or hasattr(event.media,'photo'):
                    filename = await download_file(event, message)
                elif hasattr(event.media, 'webpage') or contains_url(element[2]):
                    filename = await donload_file_from_url(event, message, element[2])
                else:
                    print("This is not possible to happen, check elements:")
                    print(element)

                await log_reply(message, "{0} ready".format(filename))
                queue.task_done()
            except Exception as e:
                try: await log_reply(message, "Error: {}".format(str(e))) # If it failed, inform the user about it.
                except: pass
                print('Queue worker error: ', e)
 
    async def download_file(event, message):
        full_file_name=get_filename(event)
        file_name, file_ext = os.path.splitext(full_file_name)
        tempfilename=file_name+"-"+get_random_id(8)+file_ext

        if path.exists("{0}/{1}.{2}".format(temp_folder,tempfilename,TELEGRAM_DAEMON_TEMP_SUFFIX)) or path.exists("{0}/{1}".format(download_folder,full_file_name)):
            if duplicates == "rename":
                full_file_name=tempfilename

        if hasattr(event.media, 'photo'):
            size = 0
        else: 
            size=event.media.document.size

        await log_reply(message, "Downloading file {0} ({1} bytes)".format(full_file_name,size))
        download_callback = lambda received, total: set_progress(full_file_name, message, received, total)
        await client.download_media(event.message, "{0}/{1}.{2}".format(temp_folder,full_file_name,TELEGRAM_DAEMON_TEMP_SUFFIX), progress_callback = download_callback)
        set_progress(full_file_name, message, 100, 100)
        move("{0}/{1}.{2}".format(temp_folder,full_file_name,TELEGRAM_DAEMON_TEMP_SUFFIX), "{0}/{1}".format(download_folder,full_file_name))
        return full_file_name

    async def donload_file_from_url(event, message, url):
        if is_youtube_url(url):
            return download_youtube_video(url, download_folder)
        elif is_mega_url(url):
            return download_mega_url(url, download_folder)
        else:
            return download_file_from_url(url, download_folder)
        return url

    async def start():
        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(worker_count):
            task = loop.create_task(worker())
            tasks.append(task)
        await send_hello_message(client, peer_channel)
        await client.run_until_disconnected()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    client.loop.run_until_complete(start())

# if __name__ == "__main__":
#     text = """
#         test message for urls:
#         http://www.youtube.com/watch?v=5Y6HSHwhVlY
#         http://youtu.be/5Y6HSHwhVlY
#         http://www.youtube.com/embed/5Y6HSHwhVlY?rel=0" frameborder="0"
#         https://www.youtube-nocookie.com/v/5Y6HSHwhVlY?version=3&amp;hl=en_US
#         http://www.youtube.com/
#         http://www.youtube.com/?feature=ytca
#         https://www.youtube.com/watch?v=r6lCasz0NxE
#         https://mega.nz/folder/so90RCjC#klbDDyn-jJZm2rlW4fk5yA #myfolder 
#         https://mega.nz/file/x88wiYzS#HU2QOY081aS00ceWdAFTe9FjwRAi0fChuK3azfe9vuE #myfile
#         https://megatools.megous.com/builds/experimental/megatools-1.11.0-git-20200503-linux-x86_64.tar.gz 
#     """
    # if contains_url(text):
    #     urls = extract_urls(text)
    #     for url in urls:
    #         if is_youtube_url(url):
    #             print("YOUTUBE " + url)
    #         elif is_mega_url(url):
    #             print("MEGA " + url)
    #         else:
    #             print("LINK " + url)
