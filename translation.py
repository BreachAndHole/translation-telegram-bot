import requests
import time
import config
from bs4 import BeautifulSoup
from random import randint
import googlesearch


def google_search_link(song_request: str):
    time.sleep(randint(1, 2))
    try:
        searched_links = googlesearch.search(
            f"{song_request} перевод",
            num_results=4
        )
    except Exception as ex:
        print(f'exeption {ex} in google search function')
        return None

    for link in searched_links:
        if "en.lyrsense.com" in link:
            song_url = link
            return song_url
    return None


# return translation from url
def get_translation(song_name: str):
    song_url = google_search_link(song_name)
    if song_url is None:
        return None

    # getting the translation page
    try:
        html_text = requests.get(song_url, headers=config.HEADER).text
    except Exception:
        print(f'Error. Can\'t connect to {song_url}')
        return None

    soup = BeautifulSoup(html_text, "lxml")
    translation_table = soup.find("table", class_="content_texts")

    # Parsing english text
    english_text = []
    for item in translation_table.find("p", id="fr_text"):
        if item.text.strip():
            english_text.append(item.text.strip("0123456789 \n\t"))

    # Parsing russian text
    russian_text = []
    for item in translation_table.find("p", id="ru_text"):
        if item.text.strip():
            russian_text.append(item.text.strip("0123456789 \n\t"))

    # Parsing song information
    names_line = soup.find(
        "div",
        class_="breadcrumbs songBreads"
    ).find_all(
        "span",
        itemprop="itemListElement"
    )

    artist_name, album_name, song_original_name = [item.text.strip() for item in names_line]
    song_translated_name = soup.find("h2", id="ru_title").text.strip()

    # parsing album cover
    album_cover_url = soup.find(
        "img",
        alt=album_name
    ).get(
        "src"
    ).replace(
        "/./",
        "https://en.lyrsense.com/"
    )

    # parsing translator information
    translation_author_name = soup.find(
        "div",
        id="author_var1"
    ).text.strip(
    ).replace(
        "Автор перевода — ",
        ""
    ).replace(
        "Страница автора",
        ""
    )

    translation_info = {
        "artist_name": artist_name,
        "album_name": album_name,
        "song_original_name": song_original_name,
        "song_translated_name": song_translated_name,
        "translation_author_name": translation_author_name,
        "album_cover_url": album_cover_url,
        "translation_url": song_url}

    return translation_info, tuple(zip(english_text, russian_text))

