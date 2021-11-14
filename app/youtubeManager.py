import re
import pytube

def isYoutubeVideo(url):
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    if re.match(regex, url):
        print('Youtube link: {}'.format(url))
        return True
    else:
        print('No youtube link: {}'.format(url))
        return False
    # try:
    #     video_id=pytube.extract.video_id(url)
    #     print(f'ID: {video_id}')
    #     return True
    # except:
    #     print(url, "is not a youtube video")
    #     return False

def getVideo(url):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    return video

def downloadYoutubeVideo(url, dest):
    video = getVideo(url)
    print(f'Title: {video.title}')
    video.download(dest)
    return video.title

if __name__ == "__main__":
    youtube_urls_test = [
        'http://www.youtube.com/watch?v=5Y6HSHwhVlY',
        'http://youtu.be/5Y6HSHwhVlY', 
        'http://www.youtube.com/embed/5Y6HSHwhVlY?rel=0" frameborder="0"',
        'https://www.youtube-nocookie.com/v/5Y6HSHwhVlY?version=3&amp;hl=en_US',
        'http://www.youtube.com/',
        'http://www.youtube.com/?feature=ytca']
    for url in youtube_urls_test:
        m = isYoutubeVideo(url)
        if m:
            print('OK {}'.format(url))
        else:
            print('FAIL {}'.format(url))