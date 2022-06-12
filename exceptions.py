class SearchEngineHTTPError(Exception):
    """ Error due to many requests for google url """


class TranslationSearchError(Exception):
    """ Error during translation link searching"""


class TranslationConnectionError(Exception):
    """ Error during connection """


class CantGetTranslationError(Exception):
    """ Error during translation extracting """
