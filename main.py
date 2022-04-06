import config
from translation import get_translation
from telebot import TeleBot, types

TRANSLATE_SONG_BTN_TEXT = "Хочу перевести песню"


# Bot function
def telegram_bot():
    bot = TeleBot(config.TOKEN, parse_mode="HTML")

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
        bot_msg = bot.send_message(message.chat.id, "Напиши мне имя исполнителя и название песни (одним сообщением)")
        bot.register_next_step_handler(bot_msg, callback=send_translation)

    def send_translation(message):
        bot_msg = bot.send_message(message.chat.id, "Секундочку, ищу перевод...")
        song_name = message.text.replace("-", "")

        translation = get_translation(song_name)
        if translation is None:
            text = f"Я не смог найти перевода такой песни 🥺 \n" \
                   f"Возможно вы ввели название неверно, " \
                   f"или перевода этой песни ещё не существует 🧐 \n"
            bot.edit_message_text(chat_id=message.chat.id, message_id=bot_msg.id, text=text)
            return

        song_info, song_text = translation

        # forming a translation info
        formated_info = f'Исполнитель: {song_info["artist_name"]}\n' \
                        f'Песня: {song_info["song_original_name"]}\n' \
                        f'Альбом: {song_info["album_name"].title()}\n' \
                        f'Автор перевода: {song_info["translation_author_name"].title()}\n' \
                        f'Перевод на сайте: {song_info["translation_url"]}'

        # send translation info
        bot.delete_message(message.chat.id, message_id=bot_msg.id)
        bot.send_photo(message.chat.id, caption=formated_info, photo=song_info["album_cover_url"])

        # forming the translation to send
        formated_text = f'<b>{song_info["song_original_name"]}</b> - ' \
                        f'<i>{song_info["song_translated_name"]}</i>\n\n'
        i = 1
        for eng, rus in song_text:
            formated_text += f"<b>{eng}</b>\n" \
                             f"<i>{rus}</i>\n"
            if i % 5 == 0:
                formated_text += "\n"
            i += 1

        messages = message_split(formated_text)

        # sending all the messages
        for msg in messages:
            bot.send_message(message.chat.id, msg)

    bot.polling()


def message_split(message: str, char_num_cap=5000, splitter="\n\n"):
    """
    :param message: message to split
    :param char_num_cap: maximum amount of chars in one sub message
    :param splitter: patter for split place
    :return: iterable of sub messages
    """
    messages = []
    if len(message) - char_num_cap > 1:
        num_of_messages = len(message) // char_num_cap + 1
        size = len(message) // num_of_messages + 1

        # splitting message to smaller messages
        for i in range(num_of_messages):
            submessage = message[size * i:size * (i + 1)]
            index = submessage.rfind(splitter)
            messages.append(submessage[:index + 1].strip())
            message = message.replace(submessage[:index + 1], "")

        # removing empty messages
    messages.append(message.strip())
    return filter(None, messages)


if __name__ == "__main__":
    telegram_bot()
