"""
TODO: Doku
"""
from datetime import datetime
from html.parser import HTMLParser
from json import loads
from threading import Thread
from time import sleep

import requests

from corona_germany_telegram_bot.bot import Bot
from corona_germany_telegram_bot.config import Config
from corona_germany_telegram_bot.users import Users


class News(object):
    """
    TODO: Doku
    """

    def __init__(self, configpath, newspath, userspath, dispatcher):
        self.newsconfig = Config(newspath)
        self.users = Users(userspath)
        self.bot = Bot(configpath, userspath)
        self.stopflag = False
        self.dispatcher = dispatcher

    def get_json_content(self) -> dict:
        """
        TODO: Doku
        """
        url = self.newsconfig.get_value("NEWS", "url")
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Sec-Fetch-Dest": "document",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7"
        }
        return loads(requests.get(url, headers=headers).text)

    def check_for_news(self):
        """
        TODO: Doku
        """
        news = self.get_json_content()["countrynewsitems"]
        last_news_id = self.newsconfig.get_value("NEWS", "last_id")
        if last_news_id == "":
            last_news_id = news[len(news) - 2]["newsid"]
            self.newsconfig.set_value("NEWS", "last_id", last_news_id)
        if news[len(news) - 2]["newsid"] != last_news_id:
            self.send_news(news, last_news_id)
            self.newsconfig.set_value("NEWS", "last_id", news[len(news) - 2]["newsid"])

    def send_news(self, newsdict, last_news_id):
        """
        TODO: Doku
        """
        for news in newsdict:
            if news["newsid"] == last_news_id:
                break
            else:
                for chat_id in self.users.get_user_list():
                    title = news["title"]
                    published = datetime.strptime(news["time"], "%-d %B %Y %H:%M")
                    published = "{0:%d.%m.%Y %H:%M}".format(published)
                    url_article = "[To Article](" + news["url"] + ")"
                    url_image = "[To Image](" + news["image"] + ")"
                    text = "*" + title + "*\n" + published + "\n\n" + url_image + " - " + url_article
                    self.bot.send_message(
                        chat_id, text, self.dispatcher.bot.send_message, "Markdown", False)

    def send_stats(self) -> None:
        """
        TODO: Doku
        """
        for chat_id in self.users.get_user_list():
            data = self.get_json_content()["countrydata"]
            text = """
Statistics for Germany:
Total cases: {}
Total recovered: {}
Total unresolved: {}
Total Deaths: {}
Total new cases today: {}
Total new deaths today: {}
Total active cases: {}
Total serious cases: {}
"""
            text = text.format(
                data["total_cases"],
                data["total_recovered"],
                data["total_unresolved"],
                data["total_deaths"],
                data["total_new_cases_today"],
                data["total_new_deaths_today"],
                data["total_active_cases"],
                data["total_serious_cases"]
            )

            self.bot.send_message(
                chat_id, text, self.dispatcher.bot.send_message, "Markdown", False)

    def start_thread(self):
        """
        TODO: Doku
        """
        thread = Thread(target=self.run_thread, args=("news"))
        thread.start()
        thread = Thread(target=self.run_thread, args=("stats"))
        thread.start()

    def run_thread(self, thread_type: str) -> None:
        """
        TODO: Doku
        """
        if thread_type == "news":
            interval = self.newsconfig.get_value("NEWS", "interval_news") * 60
        else:
            interval = self.newsconfig.get_value("NEWS", "interval_stats") * 60
        slept = interval
        while True:
            if not self.stopflag:
                sleep(1)
                slept = slept + 1
                if slept >= interval:
                    if thread_type == "news":
                        self.check_for_news()
                    else:
                        self.send_stats()
                    slept = 0
            else:
                break


class ImgParse(HTMLParser):
    """
    TODO: Doku
    """
    img_src = ""

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.img_src = dict(attrs)["src"]

    def error(self, message):
        raise message
