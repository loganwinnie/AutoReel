from Utils import navigate_to_url
from pytube import YouTube
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup # type: ignore



def grab_videos(driver):
    video_area = driver.find_element(By.ID, "contents")
    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    video_soup = page_soup.find(id="contents")
    videos = video_soup.find_all(id="video-title")

    videos = [{"title": video.get("title"), "link": video.get("href")} for video in videos]


    # videos = video_area.find_elements(By.ID, "video-title")
    return videos

def download_videos(videos):
    for video in videos:
         vid = YouTube(video.link)
         print(vid)
         print(vid.streams())











def main():
    browser = webdriver.Chrome()

    navigate_to_url(driver=browser, url="https://www.youtube.com/results?search_query=gameplay++no+copyright")
    videos = grab_videos(driver=browser)
    download_videos(videos=videos)

main()

