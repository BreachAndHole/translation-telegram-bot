import os

from dotenv import load_dotenv
from telebot import TeleBot, types

from errors import CantGetTranslationError
from translation import TranslationInfo, TranslationText, get_translation


# Bot function
def telegram_bot():
    bot_token = os.getenv('API_TOKEN')
    bot = TeleBot(bot_token, parse_mode="HTML")

    @bot.message_handler(commands=['start'])
    def start_command(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        translate_btn = types.KeyboardButton('Хочу перевести песню')
        keyboard.add(translate_btn)

        text = 'Привет, я занимаюсь поиском переводов твоих любимых песен. '\
               'Для начала введи /start'
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

    @bot.message_handler(
        content_types='text',
        func=lambda message: message.text == 'Хочу перевести песню'
    )
    def translate(message):
        bot.delete_message(message.chat.id, message_id=message.id)
        bot_msg = bot.send_message(
            message.chat.id,
            'Напиши мне имя исполнителя и название песни (одним сообщением)'
        )
        bot.register_next_step_handler(bot_msg, callback=send_translation)

    def send_translation(message):
        bot_msg = bot.send_message(
            message.chat.id,
            'Секундочку, ищу перевод...'
        )
        try:
            translation_results = get_translation(song_name=message.text)
        except CantGetTranslationError:
            text = 'Я не смог найти перевода такой песни 🥺 \n'\
                   'Возможно вы ввели название неверно, '\
                   'или перевода этой песни ещё не существует 🧐 \n'
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=bot_msg.id,
                text=text
            )
            return

        song_info: TranslationInfo = translation_results.information
        song_text: list[TranslationText] = translation_results.translation

        # forming a translation info
        info_to_send = f'Исполнитель: {song_info.artist}\n'\
                       f'Песня: {song_info.song_name}\n'\
                       f'Альбом: {song_info.album_name.title()}\n'\
                       f'Автор перевода: {song_info.translator.title()}'

        # send translation info
        bot.delete_message(message.chat.id, message_id=bot_msg.id)

        # Checking if album cover url is valid
        try:
            bot.send_photo(
                message.chat.id, caption=info_to_send,
                photo=song_info.album_cover
            )
        except Exception:
            bot.send_message(
                message.chat.id,
                info_to_send
            )

        # forming the translation to send
        translation_to_send = f'<b>{song_info.song_name}</b> - '\
                              f'<i>{song_info.song_translated_name}</i>\n\n'

        for i, (eng, rus) in enumerate(song_text, 1):
            translation_to_send += f"<b>{eng}</b>\n"\
                                   f"<i>{rus}</i>\n"
            # make blank line separation after every five lines
            if i % 5 == 0:
                translation_to_send += "\n"

        messages = split_message_to_even_chunks(translation_to_send)

        # sending all the messages
        for msg in messages:
            bot.send_message(message.chat.id, msg)

    bot.polling()


def split_message_to_even_chunks(message: str, char_num_cap=5000):
    messages = []
    if len(message) - char_num_cap > 1:
        num_of_messages = len(message)//char_num_cap + 1
        size = len(message)//num_of_messages + 1

        # splitting message to smaller messages
        for i in range(num_of_messages):
            submessage = message[size*i:size*(i + 1)]
            index = submessage.rfind('\n\n')
            messages.append(submessage[:index + 1].strip())
            message = message.replace(submessage[:index + 1], "")

    # removing empty messages
    messages.append(message.strip())
    return filter(None, messages)


if __name__ == "__main__":
    load_dotenv()
    telegram_bot()
