import re
import pytube

def extractUrl(text):
    return re.search("(?P<url>https?://[^\s]+)", text).group("url")

def isYoutubeVideo(url):
    try:
        video_id=pytube.extract.video_id(url)
        print(f'ID: {video_id}')
        return True
    except:
        print(url, "is not a youtube video")
        return False

def getVideo(url):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    return video

def downloadYoutubeVideo(url, dest):
    if isYoutubeVideo(url):
        video = getVideo(url)
        print(f'Title: {video.title}')
        video.download(dest)
        