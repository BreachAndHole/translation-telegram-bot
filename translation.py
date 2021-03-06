from enum import Enum
from typing import NamedTuple

import googlesearch
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from exceptions import *


class SongTextTag(Enum):
    """ HTML class for finding needed text lines in translation table """
    ENGLISH = "fr_text"  # Yes, on the website it's French for some reasons
    RUSSIAN = "ru_text"


class TranslationInfo(NamedTuple):
    """ Tuple representing all song info needed to be parsed"""
    artist: str
    album_name: str
    song_name: str
    song_translated_name: str
    translator: str
    album_cover: str


class TranslationText(NamedTuple):
    """ Tuple representing one line of eng and rus text """
    english: str
    russian: str


class TranslationResult(NamedTuple):
    """ Tuple representing overall result of translation parsing function """
    information: TranslationInfo
    translation: list[TranslationText]


def get_translation(song_name: str, links_limit=10) -> TranslationResult:
    """
    Searching for the translation on lyrsense website
    and returns the song information and translation.
    """
    # Getting the translation link
    try:
        song_url = _get_translation_link(song_name, links_limit)
    except SearchEngineHTTPError:
        raise SearchEngineHTTPError('Bot got timed out by google')
    except TranslationSearchError:
        raise CantGetTranslationError('No translation link found')

    # Getting the translation page
    try:
        html_text = _get_page_html(song_url)
    except TranslationConnectionError:
        raise CantGetTranslationError('Could not connect to translation url')

    soup = BeautifulSoup(html_text, "lxml")

    # Extracting original text and translation
    english_text = _get_song_text(soup, SongTextTag.ENGLISH)
    russian_text = _get_song_text(soup, SongTextTag.RUSSIAN)

    # Extracting translation information
    translation_info = _get_translation_information(soup)
    translation = _get_formatted_translation(english_text, russian_text)

    return TranslationResult(translation_info, translation)


def _get_translation_link(song_name: str, links_limit=10) -> str:
    """ Search for the translation link of the song."""
    try:
        searched_links = googlesearch.search(
            f'{song_name} ?????????????? lyrsense',
            num_results=links_limit
        )
    except requests.exceptions.HTTPError:
        raise SearchEngineHTTPError
    except Exception:
        raise TranslationSearchError('Error during translation searching')

    # Searching for the translation link on lyrsense website
    for link in searched_links:
        if 'lyrsense.' in link:
            return link
    raise TranslationSearchError('No translation link found')


def _get_page_html(translation_url: str) -> str:
    """ Getting raw html text from the translation page. """
    header = Headers(browser="chrome", os="win", headers=True)
    try:
        return requests.get(translation_url, headers=header.generate()).text
    except requests.exceptions.ConnectionError:
        raise TranslationConnectionError


def _get_song_text(page_soup: BeautifulSoup, lang: SongTextTag) -> list[str]:
    """ Returns the song text as a list of lines."""
    translation_table = page_soup.find("table", class_="content_texts")
    lines = translation_table.find('p', id=lang.value)
    parsed_text = []
    for line in lines:
        line = line.text.strip()
        if line:
            parsed_text.append(line)

    return parsed_text


def _get_translation_information(page_soup: BeautifulSoup) -> TranslationInfo:
    """ Get all the translation info"""
    names_line = page_soup.find(
        'div',
        class_='breadcrumbs songBreads'
    ).find_all("span", itemprop='itemListElement')
    artist, album, song = [item.text.strip() for item in names_line]
    song_translated_name = page_soup.find('h2', id='ru_title').text.strip()

    # album cover
    album_cover_url = page_soup.find(
        'img',
        alt=album
    ).get('src').replace('/./', 'https://gb.lyrsense.com/')

    translator = page_soup.find(
        'div',
        id='author_var1'
    ).text.strip().replace(
        '?????????? ???????????????? ??? ',
        ''
    ).replace('???????????????? ????????????', '')

    translation_info = TranslationInfo(
        artist,
        album,
        song,
        song_translated_name,
        translator,
        album_cover_url,
    )
    return translation_info


def _get_formatted_translation(
        eng_text: list[str],
        rus_text: list[str]
) -> list[TranslationText]:
    return [TranslationText(eng, rus) for eng, rus in zip(eng_text, rus_text)]
