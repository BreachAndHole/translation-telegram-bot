# Song Translation Telegram Bot

This readme is bilingual:
 - [Russian version](#краткое-описание)
 - [English version](#brief-description)
___
## Краткое описание
Этот телеграм бот сделан для поиска переводов песен с английского языка на русский.
На данный момент бот поддерживает поиск по сайту [Lyrsense.com](https://gb.lyrsense.com/)

Используемая при написании версия Python - 3.10.

## Используемые библиотеки

Основные:
 - `pyTelegramBotAPI` - [API Telegram](https://github.com/eternnoir/pyTelegramBotAPI), основа функционала бота
 - `googlesearch-python` - [библиотека для google поиска](https://github.com/Nv7-GitHub/googlesearch) по запросу пользователя
 - `beautifulsoup4` - реализация парсинга данных о переводе и самого перевода

Все использованные библиотеки описаны в файл `requirements.txt`

## Запуск бота
 - Склонировать репозиторий
```
$ git clone https://github.com/BreachAndHole/translation-telegram-bot.git
$ cd translation-telegram-bot
```
 - Установить и активировать виртуальное окружение
```
$ python3.10 -m venv venv
$ source venv/bin/activate
```
 - Установить необходимые библиотеки
```
$ pip install -r requirements.txt
```
 - Прописать ваш Telegram API Token в переменные окружения  
    - Создать файл с названием `.env` в корневом каталоге проекта
    - В созданном файле добавить строку `API_TOKEN=` и вписать своей токен.
   [Как получить токен?](https://core.telegram.org/bots#6-botfather)
 
 - Запустить бота
```
$ python3.10 main.py
```

___
## Brief Description

This telegram bot made to search translations of song from English into Russian.
For now the bot supports search at [Lyrsense.com](https://gb.lyrsense.com/) website.

Python version - 3.10.

## Используемые библиотеки

Core:
 - `pyTelegramBotAPI` - [API Telegram](https://github.com/eternnoir/pyTelegramBotAPI), core bot functionality
 - `googlesearch-python` - [google search package](https://github.com/Nv7-GitHub/googlesearch) for users translation requests
 - `beautifulsoup4` - implementation of parsing data about translation and the translation itself

All required packages are listed in `requirements.txt`

## Bot launching
 - Clone the repository
```
$ git clone https://github.com/BreachAndHole/translation-telegram-bot.git
$ cd translation-telegram-bot
```
 - Install and activate virtual environment
```
$ python3.10 -m venv venv
$ source venv/bin/activate
```
 - Install required packages
```
$ pip install -r requirements.txt
```
 - Write your Telegram API Token in environment variables  
    - Create files named `.env` in project root directory
    - In created file write a line `API_TOKEN=` and paste your token
   [How to get a token?](https://core.telegram.org/bots#6-botfather)
 
 - Launch the bot
```
$ python3.10 main.py
```