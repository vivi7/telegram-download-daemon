import logging

import pytube
from pytube import Playlist
from pytube import Channel

from util.string_utility import StringUtility


class YoutubeService:


    def on_progress_callback(self, stream, chunk, bytes_remaining):
        logging.info(f"{0}% in progress...".format(round((1-bytes_remaining/stream.filesize)*100, 3)))
    
    
    def on_complete_callback(self, stream, file_path):
        logging.info(f"{0} 100% done".format(file_path))


    def _get_video(self, url):
        youtube = pytube.YouTube(
            url, 
            on_progress_callback=self.on_progress_callback,
            on_complete_callback=self.on_complete_callback
        )
        video = youtube.streams.get_highest_resolution()
        return video

    
    def match(self, url):
        regex = (
            r"(https?://)?(www\.)?"
            "(youtube|youtu|youtube-nocookie)\.(com|be)/"
            "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
        )
        return StringUtility.match_text(regex, url)


    def download(self, url, dest):
        if "channel" in url:
            return self.download_channel(url, dest)
        elif "list" in url:
            return self.download_playlist(url, dest)
        else:
            return self.download_video(url, dest)


    def download_video(self, url, dest):
        video = self._get_video(url)
        video.download(dest)
        return video.title


    def download_playlist(self, url, dest):
        playlist = Playlist(url)
        titles = []
        for video in playlist:
            title = self.download_video(video, dest)
            titles.append(title)
        return titles


    def download_channel(self, url, dest):
        channel = Channel(url)
        titles = []
        for video in channel:
            title = self.download_video(video, dest)
            titles.append(title)
        return titles
