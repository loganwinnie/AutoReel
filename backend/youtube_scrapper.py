import logging
from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from yt_dlp import YoutubeDL  # type: ignore
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, NoResultFound

from bucket_upload import upload_downloaded_files
from config import engine
from models import Video


def grab_videos(driver: webdriver.Chrome) -> list[dict]:
    """
    Extracts video metadata from the YouTube search results page.
    Filters by videos that contain 'gameplay' in the title.

    :param driver: Selenium WebDriver instance (Chrome).
    :return: A list of dicts with 'title' and 'link'.
    """
    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    video_soup = page_soup.find(id="contents")
    if not video_soup:
        return []

    all_videos = video_soup.find_all(id="video-title")

    # Filter by "gameplay" in the title.
    gameplay_videos = []
    for vid in all_videos:
        title = vid.get("title")
        href = vid.get("href")
        if title and href and "gameplay" in title.lower():
            gameplay_videos.append({
                "title": title,
                "link": f"https://www.youtube.com/{href}"
            })

    # Limit to 5 videos.
    return gameplay_videos[:5]


def download_videos(videos: list[dict]) -> None:
    """
    Downloads videos using yt-dlp.

    :param videos: List of dicts with 'title' and 'link'.
    :return: None
    """
    yt_opts = {
        "paths": {"home": "./video_downloads"},
        "restrictfilenames": True,
    }
    ydl = YoutubeDL(yt_opts)

    for video in videos:
        try:
            ydl.download([video["link"]])
            logging.info("Downloaded: %s", video["title"])
        except Exception:
            logging.error("Failed to download: %s", video["link"])


def scrape_videos(game: str = "") -> list[dict]:
    """
    Uses Selenium to search YouTube for up to 5 gameplay videos,
    downloads them locally, uploads them to GCS, and returns
    a list of dicts with the actual title, link, and gcs_path.
    """
    option = Options()
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-infobars")
    option.add_argument("--start-maximized")
    option.add_argument("--disable-notifications")
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(options=option)
    browser.get(f"https://www.youtube.com/results?search_query={game}+gameplay+no+copyright")

    videos = grab_videos(driver=browser)  # list of {"title", "link"}
    if videos:
        download_videos(videos=videos)
    browser.quit()

    # Upload local files and get list of GCS paths.
    uploads = upload_downloaded_files()

    # Pair each upload path with the corresponding video metadata.
    combined_info = []
    for i, vid in enumerate(videos):
        item = {
            "title": vid["title"],
            "link": vid["link"],
            "gcs_path": uploads[i] if i < len(uploads) else None,
        }
        combined_info.append(item)

    return combined_info


def save_video_to_db(title: str, file_path: str, video_url: str):
    """
    Saves a video record to the database.

    :param title: Title of the video.
    :param file_path: GCS path of the uploaded file.
    :param video_url: Original YouTube link.
    :return: JSON representation of the saved Video object.
    """
    with Session(engine) as session:
        try:
            video_record = Video(
                title=title,
                file_path=file_path,
                video_url=video_url,
            )
            session.add(video_record)
            session.commit()
            session.refresh(video_record)

            return video_record.model_dump_json()
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Cannot save duplicate video.")
        except Exception as ex:
            logging.error("save_video_to_db error: %s", ex)
            raise HTTPException(status_code=500, detail="Failed to save video.")

def get_videos_db(offset: int = 0, limit: int = 15) -> list[Video]:
    """
    Retrieves saved videos from the database with pagination.

    :param offset: Pagination offset.
    :param limit: Number of items to retrieve.
    :return: A list of Video objects.
    """
    with Session(engine) as session:
        statement = select(Video).offset(offset).limit(limit)
        videos = session.exec(statement).all()
        return videos