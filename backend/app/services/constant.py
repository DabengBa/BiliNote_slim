from app.downloaders.bilibili_downloader import BilibiliDownloader
from app.downloaders.local_downloader import LocalDownloader
from app.downloaders.youtube_downloader import YoutubeDownloader

SUPPORT_PLATFORM_MAP = {
    'youtube': YoutubeDownloader(),
    'bilibili': BilibiliDownloader(),
    'local': LocalDownloader()
}