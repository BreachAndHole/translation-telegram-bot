import requests
import time
import config
from bs4 import BeautifulSoup
from random import randint
from googlesearch import search


# return translation from url
def get_translation(song_name: str, num_of_results=4, song_url=None):
    """
    :param song_name: artist and song name in free format
    :param num_of_results: number of google search urls requests
    :param song_url: direct translation from sing_url
    :return:
    """
    # Searching for the translation url in google
    if song_url is None or "en.lyrsense.com" not in song_url:
        time.sleep(randint(1, 2))
        song_url = None
        for url in search(f"{song_name} перевод", num_results=num_of_results):
            if "en.lyrsense.com" in url:
                song_url = url
                break

        if song_url is None:
            return None

    # getting the translation page
    req = requests.get(song_url, headers=config.HEADER)
    if req.status_code != 200:
        print("Error. Can't connect to this url")
        return None
    html_text = req.text

    # Saving html with translation to file
    # with open(config.LOCAL_FILE_NAME, "w", encoding="utf-8") as file_out:
    #     file_out.write(html_text)

    # Reading from local file
    # with open(FILE_NAME, "r", encoding="utf-8") as fin:
    #     html_text = fin.read()
    # os.remove(config.LOCAL_FILE_NAME)

    soup = BeautifulSoup(html_text, "lxml")
    translation_table = soup.find("table", class_="content_texts")

    # parsing english text
    english_text = [item.text.strip("0123456789 \n\t")
                    for item in translation_table.find("p", id="fr_text")
                    if item.text.strip()]

    # parsing russian text
    russian_text = [item.text.strip("0123456789 \n\t")
                    for item in translation_table.find("p", id="ru_text")
                    if item.text.strip()]

    # parsing song information
    names_line = soup.find("div", class_="breadcrumbs songBreads").find_all("span", itemprop="itemListElement")
    artist_name, album_name, song_original_name = [item.text.strip() for item in names_line]

    song_translated_name = soup.find("h2", id="ru_title").text.strip()

    # parsing album cover
    cover_url = soup.find("img", alt=album_name).get("src").replace("/./", "https://en.lyrsense.com/")

    # parsing translator information
    translation_author_name = soup.find("div",
                                        id="author_var1").text.strip().replace("Автор перевода — ",
                                                                               "").replace("Страница автора",
                                                                                           "")

    # zipping result
    translation_info = {
        "artist_name": artist_name,
        "album_name": album_name,
        "song_original_name": song_original_name,
        "song_translated_name": song_translated_name,
        "translation_author_name": translation_author_name,
        "album_cover_url": cover_url,
        "translation_url": song_url}

    return translation_info, tuple(zip(english_text, russian_text))
