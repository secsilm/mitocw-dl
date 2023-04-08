from __future__ import annotations

import random
import re
import sys
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm


def download(course_url, folder="./"):
    """Main function."""
    folder = Path(folder) / course_url.strip("/").split("/")[-1]
    folder.mkdir(exist_ok=True, parents=True)
    lecture_video_url = urljoin(course_url, "video_galleries/lecture-videos/")
    lecture_note_url = urljoin(course_url, "pages/lecture-notes/")

    for video_page in list_lecture_videos(lecture_video_url):
        download_lecture_video(video_page, folder / "videos/")
        sleep(1 + 2 * random.random())

    for lecture_note, recitation_note in list_lecture_notes(lecture_note_url):
        if lecture_note:
            download_note(lecture_note, folder / "notes/")
            sleep(1 + 2 * random.random())
        if recitation_note:
            download_note(recitation_note, folder / "notes/")
            sleep(1 + 2 * random.random())


def list_lecture_videos(url) -> list:
    """Extract video links."""
    soup = get_soup(url)
    video_tags = soup.find_all("a", {"class": "video-link"})
    video_links = [urljoin(url, tag["href"]) for tag in video_tags]
    return video_links


def list_lecture_notes(url) -> list:
    """Extract note links."""
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
    """Download lecture video. subfolder defaults to lecture name."""
    soup = get_soup(url)
    folder = Path(folder) / soup.h2.text.strip()
    folder.mkdir(exist_ok=True, parents=True)
    video_tag = soup.find("video", {"data-downloadlink": True})
    video_link = video_tag["data-downloadlink"]
    filepath = download_handler(video_link, folder)
    logger.info(f"Downloaded {video_link} to {filepath}.")
    if subtitle:
        subtitle_link = video_tag.find("track", {"kind": "captions", "src": True})[
            "src"
        ]
        subtitle_link = urljoin(url, subtitle_link)
        filepath = download_handler(subtitle_link, folder)
        logger.info(f"Downloaded {subtitle_link} to {filepath}.")


def download_note(url, folder) -> str:
    """Download lecture note or recitation note."""
    soup = get_soup(url)
    download_tag = soup.find("a", {"class": "download-file"})
    download_link = urljoin(url, download_tag["href"])
    filepath = download_handler(download_link, folder)
    logger.info(f"Downloaded {download_link} to {filepath}.")
    return filepath


def get_soup(url):
    """Get soup from url."""
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def download_handler(url, folder) -> str:
    """The actual downloader."""
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
            desc=f"Downloading {local_filepath.name}",
            total=size,
        ) as pbar:
            r.raise_for_status()
            chunk_size = 8192
            with open(local_filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    pbar.update(len(chunk))

    return local_filepath


if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    # https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/
    if len(sys.argv) < 2:
        raise ValueError(f"You must provide the course url you want to download.")
    course_url = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) >= 3 else "./"
    download(course_url, folder)
