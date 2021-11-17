import re
import pytube
from pytube import Playlist
from pytube import Channel

def is_youtube_url(url):
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return re.match(regex, url)
    # try:
    #     video_id=pytube.extract.video_id(url)
    #     print(f'ID: {video_id}')
    #     return True
    # except:
    #     print(url, "is not a youtube video")
    #     return False

def download_youtube_url(url, dest):
    if 'channel' in url:
        return download_youtube_channel(url, dest)
    elif 'list' in url:
        return download_youtube_playlist(url, dest)
    else:
        return download_youtube_video(url, dest)

def get_video(url):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    return video

def download_youtube_video(url, dest):
    video = get_video(url)
    video.download(dest)
    print('DOWNLOADED ' + video.title)
    return video.title

def download_youtube_playlist(url, dest):
    playlist = Playlist(url)
    titles = []
    for video in playlist:
        title = download_youtube_video(video, dest)
        titles.append(title)
    return titles

def download_youtube_channel(url, dest):
    channel = Channel(url)
    titles = []
    for video in channel:
        title = download_youtube_video(video, dest)
        titles.append(title)
    return titles
