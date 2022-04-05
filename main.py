import requests
from telebot import TeleBot, types
from googlesearch import search
from bs4 import BeautifulSoup
from time import sleep
from random import randint
from config import TOKEN


def main():
    bot = TeleBot(TOKEN)

    bot.polling()


if __name__ == "__main__":
    main()
