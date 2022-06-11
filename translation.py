from enum import Enum
from typing import NamedTuple

import bs4.element
import googlesearch
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from errors import *


class SongTextTag(Enum):
    ENGLISH = "fr_text"  # Yes, it's French tag in class name for some reasons
    RUSSIAN = "ru_text"


class TranslationInfo(NamedTuple):
    artist: str
    album_name: str
    song_name: str
    song_translated_name: str
    translator: str
    album_cover: str


class TranslationText(NamedTuple):
    english: str
    russian: str


class TranslationResult(NamedTuple):
    information: TranslationInfo
    translation: list[TranslationText]


def get_translation(song_name: str) -> TranslationResult:
    """
    Searching for the translation on lyrsense website
    and returns the song information and translation.
    """
    try:
        song_url = _get_translation_link(song_name)
    except TranslationSearchError:
        raise CantGetTranslationError('No translation link found')

    # getting the translation page
    try:
        html_text = _get_page_html(song_url)
    except TranslationConnectionError:
        raise CantGetTranslationError('Could not connect to translation url')

    soup = BeautifulSoup(html_text, "lxml")
    translation_table = soup.find("table", class_="content_texts")

    english_text = _get_song_text(translation_table, SongTextTag.ENGLISH)
    russian_text = _get_song_text(translation_table, SongTextTag.RUSSIAN)

    translation_info = _get_translation_information(soup)
    translation = _get_formatted_translation(english_text, russian_text)

    return TranslationResult(translation_info, translation)


def _get_translation_link(song_request: str, number_of_links=10) -> str:
    """ Search for the translation link of the song."""
    try:
        searched_links = googlesearch.search(
            f'{song_request} перевод',
            num_results=number_of_links
        )
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
    except ConnectionError:
        raise TranslationConnectionError


def _get_song_text(bs_table: bs4.element.Tag, lang: SongTextTag) -> list[str]:
    """ Returns the song text as a list of lines."""
    lines = bs_table.find('p', id=lang.value)
    parsed_text = []
    for line in lines:
        line = line.text.strip()
        if line:
            parsed_text.append(line)

    return parsed_text


def _get_translation_information(soup: BeautifulSoup) -> TranslationInfo:
    """ Get all the translation info"""
    names_line = soup.find(
        'div',
        class_='breadcrumbs songBreads'
    ).find_all("span", itemprop='itemListElement')
    artist, album, song = [item.text.strip() for item in names_line]
    song_translated_name = soup.find('h2', id='ru_title').text.strip()

    # album cover
    album_cover_url = soup.find(
        'img',
        alt=album
    ).get('src').replace('/./', 'https://gb.lyrsense.com/')

    translator = soup.find(
        'div',
        id='author_var1'
    ).text.strip().replace(
        'Автор перевода — ',
        ''
    ).replace('Страница автора', '')

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
