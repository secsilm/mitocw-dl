from __future__ import annotations

import random
import re
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm


def list_lecture_videos(url) -> list:
    soup = get_soup(url)
    video_tags = soup.find_all("a", {"class": "video-link"})
    video_urls = [urljoin(url, tag["href"]) for tag in video_tags]
    return video_urls


def list_lecture_notes(url) -> list:
    soup = get_soup(url)
    notes = []
    for tr in soup.find_all("tr")[1:]:
        lecture_note_url = ""
        a_tag = tr.find("a", string=re.compile("Lecture"))
        if a_tag:
            lecture_note_url = urljoin(url, a_tag["href"])
        recitaion_note_url = ""
        a_tag = tr.find("a", string=re.compile("Recitation"))
        if a_tag:
            recitaion_note_url = urljoin(url, a_tag["href"])
        notes.append([lecture_note_url, recitaion_note_url])
    return notes


def download_lecture_video(url, folder, subtitle=True) -> str:
    """return filepath. subfolder defaults to lecture name."""
    soup = get_soup(url)
    folder = Path(folder) / soup.h2.text.strip()
    folder.mkdir(exist_ok=True, parents=True)
    video_tag = soup.find("video", {"data-downloadlink": True})
    video_link = video_tag["data-downloadlink"]
    filepath = download_handler(video_link, folder)
    logger.info(f"Downloaded {video_link} to {filepath}.")
    subtitle_link = video_tag.find("track", {"kind": "captions", "src": True})["src"]
    subtitle_link = urljoin(url, subtitle_link)
    filepath = download_handler(subtitle_link, folder)
    logger.info(f"Downloaded {subtitle_link} to {filepath}.")


def download_lecture_note(url, folder) -> str:
    """return notes filepath. subfolder defaults to ./notes."""
    soup = get_soup(url)
    download_tag = soup.find("a", {"class": "download-file"})
    download_link = urljoin(url, download_tag["href"])
    filepath = download_handler(download_link, folder)
    logger.info(f"Downloaded {download_link} to {filepath}.")
    return filepath


def download_recitaion_note(url, folder) -> str:
    soup = get_soup(url)
    download_tag = soup.find("a", {"class": "download-file"})
    download_link = urljoin(url, download_tag["href"])
    filepath = download_handler(download_link, folder)
    logger.info(f"Downloaded {download_link} to {filepath}.")
    return filepath


# def download_handler(url, folder) -> str:
#     """real download func, download file from url."""
#     Path(folder).mkdir(exist_ok=True, parents=True)
#     local_filepath = Path(folder) / url.split("/")[-1]
#     if local_filepath.exists():
#         logger.warning(f"{local_filepath} exists, skip.")
#         return local_filepath
#     with requests.get(url, stream=True, headers=headers) as r:
#         r.raise_for_status()
#         size = int(r.headers["Content-Length"])
#         chunk_size = 8192
#         n_chunks = (size + chunk_size - 1) // chunk_size
#         with open(local_filepath, "wb") as f:
#             for chunk in tqdm(
#                 r.iter_content(chunk_size=chunk_size),
#                 total=n_chunks,
#                 unit="KB",
#                 unit_scale=chunk_size / 1024,
#             ):
#                 f.write(chunk)
#     return local_filepath


def download_handler(url, folder) -> str:
    """下载文件并显示进度和速度。"""
    Path(folder).mkdir(exist_ok=True, parents=True)
    local_filepath = Path(folder) / url.split("/")[-1]
    if local_filepath.exists():
        logger.warning(f"{local_filepath} exists, skip.")
        return local_filepath
    with requests.get(url, stream=True, headers=headers) as r:
        size = int(r.headers["Content-Length"])
        with tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            miniters=1,
            desc="downloading",
            total=size,
        ) as pbar:
            r.raise_for_status()
            chunk_size = 8192
            with open(local_filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    pbar.update(len(chunk))

    return local_filepath


def get_soup(url):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def download(course_url, folder="./"):
    folder = Path(folder) / course_url.strip("/").split("/")[-1]
    folder.mkdir(exist_ok=True, parents=True)
    lecture_video_url = urljoin(course_url, "video_galleries/lecture-videos/")
    lecture_note_url = urljoin(course_url, "pages/lecture-notes/")

    for video_page in list_lecture_videos(lecture_video_url):
        download_lecture_video(video_page, folder / "videos/")
        sleep(1 + 2 * random.random())

    for lecture_note, recitation_note in list_lecture_notes(lecture_note_url):
        if lecture_note:
            download_lecture_note(lecture_note, folder / "notes/")
            sleep(1 + 2 * random.random())
        if recitation_note:
            download_recitaion_note(recitation_note, folder / "notes/")
            sleep(1 + 2 * random.random())


if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    download(
        "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
        "./",
    )
