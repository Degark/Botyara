from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import schedule
from threading import Thread
import time
from time import sleep
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from os import getenv
from dotenv import load_dotenv

load_dotenv()
import os
os.environ['NO_PROXY'] = 'www.kw.ac.kr'


BOT_TOKEN = getenv("TOKEN")
MY_URL = "https://www.kw.ac.kr/ko/life/notice.jsp?srCategoryId=&mode=list&searchKey=1&searchVal="

bot = TeleBot(token = BOT_TOKEN)
translator = GoogleTranslator(target = "ru")

@bot.message_handler(commands = ["start"])
def cmd_start(message):
    with open("users.txt", "a") as file:
        user_id = message.from_user.id
        user_name = f"{message.from_user.first_name} {message.from_user.last_name}"
        file.write(f"{user_id},{user_name}\n")

@bot.message_handler(commands = ["send"])
def send_info(message):
    with open("users.txt", "r") as file:
        for line in file.readlines():
            id, name = line.split(",")
            data = fetch_data(MY_URL)
            bot.send_message(id, f"Hello, {name}!")

def fetch_data(url):
    response = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0", "sec-ch-ua-platform": "Windows"})
    soup = BeautifulSoup(response.text, "html.parser")
    list_elements = soup.find_all("div", class_ = "board-text")

    data = []

    for elements in list_elements:
        text = (elements.find("a").get_text().strip().replace("Attachment", "").replace(" ", "").replace("\n", ""))

        link = elements.find("a").get("href")

        data.append((text, "https://www.kw.ac.kr" + link))
    return data

def main():
    data = fetch_data(MY_URL)
    print(len(data))

    for news_for_me in data:
        if "외국인" in news_for_me[0]:
            translated_data = translator.translate(news_for_me[0])

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Click", url = data[0][1]))
            with open("users.txt", "r") as file:
                for line in file.readlines():
                    id, name = line.split(",")
                    bot.send_message(id, translated_data, reply_markup=kb)
    
def run_schedule():
    schedule.every(1).day.at("08:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


Thread(target=run_schedule).start()
bot.infinity_polling()
