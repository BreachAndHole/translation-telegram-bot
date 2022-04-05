import requests
import os
import config
import string
from telebot import TeleBot, types
from googlesearch import search
from bs4 import BeautifulSoup
from time import sleep
from random import randint

TRANSLATE_SONG_BTN_TEXT = "Хочу перевести песню"


# Bot function
def telegram_bot():
    bot = TeleBot(config.TOKEN)

    @bot.message_handler(commands=['start'])
    def start_command(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        translate_btn = types.KeyboardButton(TRANSLATE_SONG_BTN_TEXT)
        keyboard.add(translate_btn)

        name = message.from_user.first_name
        surname = message.from_user.last_name
        text = f"Привет, {name} {surname if surname else str()}\n" \
               f"Я - бот, занимающийся поиском переводов твоих любимых песен."
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

    @bot.message_handler(content_types='text', func=lambda message: message.text == TRANSLATE_SONG_BTN_TEXT)
    def translate(message):
        bot.delete_message(message.chat.id, message_id=message.id)
        bot_msg = bot.send_message(message.chat.id, "Напиши мне имя исполнителя и название песни")
        bot.register_next_step_handler(bot_msg, callback=send_translation)

    def send_translation(message):
        bot_msg = bot.send_message(message.chat.id, "Секундочку, ищу перевод...")
        song_name = message.text.replace("-", "")
        searched_url = google_search_urls(song_name)[0]
        song_info, *song_text = get_translation(searched_url)
        info = f'Песня: {song_info["artist_name"]} - {song_info["song_original_name"].title()}\n' \
               f'Альбом: {song_info["album_name"].title()}\n' \
               f'Автор перевода: {song_info["translation_author_name"].title()}\n' \
               f'Перевод на сайте: {song_info["translation_url"]}'

        bot.delete_message(message.chat.id, message_id=bot_msg.id)
        bot.send_photo(message.chat.id, caption=info, photo=song_info["album_cover_url"])

        fomated_text = ""
        for n, eng, rus in song_text:
            fomated_text += f"<b>{eng}</b>\n<i>{rus}</i>\n"
            if n % 5 == 0:
                fomated_text += "\n"
        bot.send_message(message.chat.id, fomated_text, parse_mode="HTML")

    bot.polling()


# return translation from url
def get_translation(song_url: str):
    req = requests.get(song_url, headers=config.HEADER)
    if req.status_code != 200:
        print("Error. Can't connect to this url")
        return
    html_text = req.text
    with open(config.LOCAL_FILE_NAME, "w", encoding="utf-8") as file_out:
        file_out.write(html_text)

    # Reading from local file
    # with open(FILE_NAME, "r", encoding="utf-8") as fin:
    #     html_text = fin.read()
    os.remove(config.LOCAL_FILE_NAME)

    soup = BeautifulSoup(html_text, "lxml")
    translation_table = soup.find("table", class_="content_texts")

    # parsing english text
    english_html = translation_table.find("p", id="fr_text")
    english_text = [item.text.strip().strip(string.digits) for item in english_html if item.text.strip()]

    # parsing russian text
    russian_html = translation_table.find("p", id="ru_text")
    russian_text = [item.text.strip().strip(string.digits) for item in russian_html if item.text.strip()]

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
    result = [{
        "artist_name": artist_name,
        "album_name": album_name,
        "song_original_name": song_original_name,
        "song_translated_name": song_translated_name,
        "translation_author_name": translation_author_name,
        "album_cover_url": cover_url,
        "translation_url": song_url}]

    for i in range(min(len(english_text), len(russian_text))):
        result.append((i + 1, english_text[i], russian_text[i]))

    return result


# get list of searched translations
def google_search_urls(song_name: str, num_of_results=3):
    sleep(randint(1, 2))
    return [url for url in search(f"{song_name} перевод", num_results=num_of_results) if "en.lyrsense.com" in url]


if __name__ == "__main__":
    telegram_bot()
