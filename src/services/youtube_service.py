import pytube
from pytube import Playlist
from pytube import Channel

from util.string_utility import StringUtility


class YoutubeService:


    def _get_video(self, url):
        youtube = pytube.YouTube(url)
        video = youtube.streams.get_highest_resolution()
        return video

    
    def match(self, url):
        regex = (
            r"(https?://)?(www\.)?"
            "(youtube|youtu|youtube-nocookie)\.(com|be)/"
            "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
        )
        return StringUtility().match_text(regex, url)
        # try:
        #     video_id=pytube.extract.video_id(url)
        #     print(f'ID: {video_id}')
        #     return True
        # except:
        #     print(url, "is not a youtube video")
        #     return False


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
        print("DOWNLOADED " + video.title)
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
