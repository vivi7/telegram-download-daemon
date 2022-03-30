import os, re
import requests
from clint.textui import progress
from lxml import html, etree

# import BeautifulSoup


class ScrubberService:


    # def get_links(page_url):
    #     r = requests.get(page_url)
    #     soup = BeautifulSoup(r.content,'html.parser')
    #     links = soup.findAll('a')  # find all links on web-page
    #     file_links = [page_url + link['href'] for link in links if link['href'].endswith('mp4')] # filter the link sending with .mp4
    #     print("Links found: %s"%file_links)

    #     print(r)

    #     data = r.read()  # Download context url
    #     data = data.decode("utf-8")  # Bytes to str
    #     pattern = r"video_url=(.*?\.flv)"  # Pattern url video
    #     result = re.search(pattern, data)  # Search link to video :)
    #     url_video = result.group(1)  # Get one group -- url video

    #     print("Links found: %s"%result)
    #     return file_links


    def download_file_from_url(self, file_url, download_folder):
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)  # create folder if it does not exist
        filename = file_url.rstrip("/").split("/")[-1].rstrip("\\")
        # print("Downloading file:%s"%filename)
        r = requests.get(file_url, stream=True)
        filePath = os.path.join(download_folder, filename)
        with open(filePath, "wb") as fd:
            total_length = int(r.headers.get("content-length") or 0)
            for chunk in progress.bar(
                r.iter_content(chunk_size=1024 * 1024),
                expected_size=(total_length / 1024) + 1,
            ):
                if chunk:
                    fd.write(chunk)
        # print("%s downloaded!\n"%filePath)
        return filename
