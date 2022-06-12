from unittest import TestCase, main
import translation
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

    def test_get_translation_link_invalid(self):
        song = 'ZZ Ward - Storm'
        self.assertRaises(
            errors.CantGetTranslationError,
            translation._get_translation_link,
            song
        )

    def test_not_enough_links_taken(self):
        song = 'Slipknot - Devil in I'
        self.assertRaises(
            errors.CantGetTranslationError,
            translation._get_translation_link,
            song,
            1
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
            requests.ConnectionError,
            translation._get_page_html,
            self.incorrect_url
        )


if __name__ == '__main__':
    main()
