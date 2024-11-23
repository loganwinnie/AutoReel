from bucket_upload import upload_downloaded_files
from Utils import navigate_to_url, read_file_and_select
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By 
from bs4 import BeautifulSoup # type: ignore
from yt_dlp import YoutubeDL
from random import choice


def grab_videos(driver):
    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    video_soup = page_soup.find(id="contents")
    videos = video_soup.find_all(id="video-title")

    videos = [{"title": video.get("title", None), "link": f"https://www.youtube.com/{video.get("href")}"} 
              for video in videos 
              if "gameplay" in video.get("title", None).lower()]
    if len(videos) > 5:
        return videos[:5]
    return videos

def search_videos(query):
    search = Search(query)
    search.results[0].streams.filter(file_extension='mp4')


def download_videos(videos):
    yt_opts = {
        "paths": {"home": "./video_downloads"},
        "restrictfilenames": True,

    }
    ydl = YoutubeDL(yt_opts)

    for video in videos:
        try:
            ydl.download(video["link"])
            print("Downloaded", video["title"])
        except Exception as err:
            print(f"Failed to download {video["link"]}")


browser = webdriver.Chrome()
game = read_file_and_select("./search_terms.txt")
print(game)
navigate_to_url(driver=browser, url=f"https://www.youtube.com/results?search_query={game}+gameplay++no+copyright")
videos = grab_videos(driver=browser)
download_videos(videos=videos)
upload_downloaded_files()




