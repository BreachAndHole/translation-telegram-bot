# Song Translation Telegram Bot

## Краткое описание
Этот телеграм бот сделан для поиска переводов песен с английского языка на русский.
На данный момент бот поддерживает поиск по сайту [Lyrsense.com](https://gb.lyrsense.com/)

Используемая при написании версия Python - 3.10.

## Используемые библиотеки

Основные:
 - `pyTelegramBotAPI` - [API Telegram](https://github.com/eternnoir/pyTelegramBotAPI), основа функционала бота
 - `googlesearch-python` - [библиотека для google поиска](https://github.com/Nv7-GitHub/googlesearch) по запросу пользователя
 - `beautifulsoup4` - реализация парсинга данных о переводе и самого перевода

Все использованные библиотеки описаны в файл `requirements.tx`

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
    - Создать файл с названием `.env` в корневом каталоге
    - В созданном файле добавить строку `API_TOKEN=` и вписать своей токен.
   [Как получить токен?](https://core.telegram.org/bots#6-botfather)
 
 - Запустить бота
```
$ python3.10 main.py
```


