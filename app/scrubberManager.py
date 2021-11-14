import os, re
import requests
from clint.textui import progress
from lxml import html, etree
import requests 
from bs4 import BeautifulSoup

def extractUrls(text):
    return re.findall("(?P<url>https?://[^\s]+)", text)


def containsUrl(text):
    return len(extractUrls(text)) > 0

def extractUrl(text):
    urls = extractUrls(text)
    if len(urls) > 0:
        return urls[0]
    else:
        return ""

def getLinks(pageUrl): 
    r = requests.get(pageUrl) 
    soup = BeautifulSoup(r.content,'html.parser') 
    links = soup.findAll('a')  # find all links on web-page 
    fileLinks = [pageUrl + link['href'] for link in links if link['href'].endswith('mp4')] # filter the link sending with .mp4 
    print("Links found: %s"%fileLinks)

    print(r)

    data = r.read()  # Download context url
    data = data.decode("utf-8")  # Bytes to str
    pattern = r"video_url=(.*?\.flv)"  # Pattern url video
    result = re.search(pattern, data)  # Search link to video :)
    url_video = result.group(1)  # Get one group -- url video

    print("Links found: %s"%result)
    return fileLinks 

def downloadFileFromUrl(fileUrl, downloadFolder):
    if not os.path.exists(downloadFolder):
        os.makedirs(downloadFolder)  # create folder if it does not exist
    filename = fileUrl.rstrip('/').split("/")[-1].rstrip('\\')
    print("Downloading file:%s"%filename)
    r = requests.get(fileUrl, stream=True)
    filePath = os.path.join(downloadFolder, filename)
    with open(filePath, "wb") as fd:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size = 1024*1024), expected_size=(total_length/1024) + 1):
            if chunk:
                fd.write(chunk)
    print("%s downloaded!\n"%filePath)
    return filename

def downloadFiles(fileUrls, downloadFolder):
    for fileUrl in fileUrls: 
        downloadFileFromUrl(fileUrl, downloadFolder)
    print ("All videos downloaded!")
    return

if __name__ == "__main__":
    fileUrl = "https://github.com/transmission/transmission/releases/download/3.00/Transmission-3.00-dsym.zip////"
    filename = fileUrl.rstrip('/').split("/")[-1]
    print(filename)