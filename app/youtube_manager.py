import re
import pytube

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

def get_video(url):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    return video

def download_youtube_video(url, dest):
    video = get_video(url)
    video.download(dest)
    return video.title
