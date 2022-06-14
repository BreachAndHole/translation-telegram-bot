from unittest import TestCase, main
import translation
from bs4 import BeautifulSoup
import exceptions
import requests
from fake_headers import Headers


class TranslationLinkSearchTestCase(TestCase):

    def test_get_translation_link_valid(self):
        song = 'Slipknot - Devil in I'
        result = translation._get_translation_link(song)
        self.assertEqual(
            result,
            'https://gb.lyrsense.com/slipknot/the_devil_in_i'
        )

    def test_get_translation_link_raises_search_exception(self):
        song = 'ZZ Ward - Storm'
        self.assertRaises(
            exceptions.TranslationSearchError,
            translation._get_translation_link,
            song,
            links_limit=1
        )


class HTMLParseTestCase(TestCase):
    def setUp(self) -> None:
        header = Headers(browser="chrome", os="win", headers=True).generate()
        self.correct_url = 'https://gb.lyrsense.com/pvris/winter_p'
        self.incorrect_url = 'https://gb.lyrsense.cm/pvris/winter_p'
        self.correct_html = requests.get(self.correct_url, header).text

    def test_get_page_html_valid_link(self):
        result = translation._get_page_html(self.correct_url)
        self.assertEqual(result, self.correct_html)

    def test_get_page_html_incorrect_link_raises_exception(self):
        self.assertRaises(
            exceptions.TranslationConnectionError,
            translation._get_page_html,
            self.incorrect_url
        )


class GetTranslationTestCase(TestCase):
    def setUp(self) -> None:
        song_url = 'https://lyrsense.com/slipknot/the_devil_in_i'
        self.lines_in_song = 38
        html = translation._get_page_html(song_url)
        self.page_soup = BeautifulSoup(html, 'lxml')

    def test_english_text_is_parsed_correct(self):
        english_text_first_line = 'Undo these chains, my friend,'
        english_text_last_line = 'See the Devil in I.'
        parsed_text = translation._get_song_text(
            self.page_soup,
            translation.SongTextTag.ENGLISH
        )
        self.assertEqual(len(parsed_text), self.lines_in_song)
        self.assertEqual(parsed_text[0], english_text_first_line)
        self.assertEqual(parsed_text[-1], english_text_last_line)

    def test_russian_text_is_parsed_correct(self):
        russian_text_first_line = 'Разбей эти цепи, друг мой,'
        # There is a mistake in translation, so it is "дявола", not "дьявола"
        russian_text_last_line = 'Увидишь дявола во мне.'
        parsed_text = translation._get_song_text(
            self.page_soup,
            translation.SongTextTag.RUSSIAN
        )
        self.assertEqual(len(parsed_text), self.lines_in_song)
        self.assertEqual(parsed_text[0], russian_text_first_line)
        self.assertEqual(parsed_text[-1], russian_text_last_line)

    def test_get_translation_information_parsed_correct(self):
        song_info = translation.TranslationInfo(
            artist='Slipknot',
            album_name='.5: The Gray Chapter',
            song_name='The devil in I',
            song_translated_name='Дьявол во мне',
            translator='Екатерина Б.',
            album_cover='https://gb.lyrsense.com/images/albums/en_album_8650.jpg'
        )
        parsed_info = translation._get_translation_information(self.page_soup)

        self.assertEqual(parsed_info, song_info)

    def test_get_formatted_translation(self):
        eng_text = translation._get_song_text(
            self.page_soup,
            translation.SongTextTag.ENGLISH
        )
        rus_text = translation._get_song_text(
            self.page_soup,
            translation.SongTextTag.RUSSIAN
        )
        first_line = translation.TranslationText(
            english=eng_text[0],
            russian=rus_text[0]
        )
        last_line = translation.TranslationText(
            english=eng_text[-1],
            russian=rus_text[-1]
        )
        result = translation._get_formatted_translation(eng_text, rus_text)

        self.assertEqual(result[0], first_line)
        self.assertEqual(result[-1], last_line)
        self.assertEqual(len(result), self.lines_in_song)

    def test_get_translation_valid(self):
        song_name = 'Slipknot - The devil in I'
        song_info = translation.TranslationInfo(
            artist='Slipknot',
            album_name='.5: The Gray Chapter',
            song_name='The devil in I',
            song_translated_name='Дьявол во мне',
            translator='Екатерина Б.',
            album_cover='https://gb.lyrsense.com/images/albums/en_album_8650.jpg'
        )
        first_eng_line = 'Undo these chains, my friend,'
        last_eng_line = 'See the Devil in I.'
        first_run_line = 'Разбей эти цепи, друг мой,'
        # There is a mistake in translation, so it is "дявола", not "дьявола"
        last_rus_line = 'Увидишь дявола во мне.'
        info, translated_text = translation.get_translation(song_name)

        self.assertEqual(info, song_info)
        self.assertEqual(translated_text[0].english, first_eng_line)
        self.assertEqual(translated_text[-1].english, last_eng_line)
        self.assertEqual(translated_text[0].russian, first_run_line)
        self.assertEqual(translated_text[-1].russian, last_rus_line)


if __name__ == '__main__':
    main()
