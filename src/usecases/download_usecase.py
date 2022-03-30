import logging

from services.mega_service import MegaService
from services.scrubber_service import ScrubberService
from services.youtube_service import YoutubeService


class DownloadUsecase:


    def __init__(self):
        self.mega_service = MegaService()
        self.scrubber_service = ScrubberService()
        self.youtube_service = YoutubeService()


    async def donload_file_from_url(self, url, download_folder):
        if self.mega_service.match(url):
            logging.info("{0} is mega url".format(url))
            return self.mega_service.download(url, download_folder)
        elif self.youtube_service.match(url):
            logging.info("{0} is youtube url".format(url))
            return self.youtube_service.download(url, download_folder)
        else:
            logging.info("{0} is other url".format(url))
            return self.scrubber_service.download_file_from_url(url, download_folder)

