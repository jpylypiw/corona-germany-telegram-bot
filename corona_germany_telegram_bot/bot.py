"""
TODO: Doku
"""
from logging import error
from threading import Thread

from telegram.ext import CommandHandler, Updater

from corona_germany_telegram_bot.config import Config
from corona_germany_telegram_bot.users import Users
from corona_germany_telegram_bot.utility import format_exception


class Bot(object):
    """
    TODO: Doku
    """

    def __init__(self, config: Config, userconfig: Config):
        self.config = config
        self.users = Users(userconfig)
        self.updater = None
        self.dispatcher = None

    def init_updater(self):
        """
        TODO: Doku
        """
        try:
            self.updater = Updater(token=self.config.get_value("BOT", "token"), use_context=True)
            self.dispatcher = self.updater.dispatcher
            return self.dispatcher
        except Exception as exc:
            error("Whoops. We failed to set up the updater. Error: {}".format(exc))

    def init_handler(self):
        """
        TODO: Doku
        """
        start_handler = CommandHandler('start', self.start)
        subscribe_handler = CommandHandler('subscribe', self.subscribe)
        unsubscribe_handler = CommandHandler('unsubscribe', self.unsubscribe)
        # TODO: help command
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(subscribe_handler)
        self.dispatcher.add_handler(unsubscribe_handler)

    def start_bot(self):
        """
        TODO: Doku
        """
        thread = Thread(target=self.updater.start_polling, args=())
        thread.start()

    def start(self, update, context):
        """
        TODO: Doku
        """
        text_de = """
Hallo und Herzlich Willkommen beim *Corona Informations Bot* für Deutschland.

Der Bot informiert über zwei Arten von Daten:
- *Statistiken* zu den Patientendaten
- *News* zum Thema Corona

Der Bot ist ein privates Projekt zur Selbstinformation und für die Dateninhalte wird keine Gewähr geleistet!
Der SourceCode des Projekts ist öffentlich einsehbar auf GitHub: https://github.com/jpylypiw/corona-germany-telegram-bot

*Kommandos*, die der Bot ausführen kann:
/subscribe - dieses Kommando startet die News Belieferung
/unsubscribe - dieses Kommando stoppt die News Belieferung

Wenn du den Bot nicht mehr verwenden möchtest, kannst du einfach den Chat löschen.
"""
        text_en = """
Hello and welcome to the *Corona Information Bot* for Germany.

The bot sends two types of data:
- *statistics* about how many people are ill and cured
- *news* about corona in germany

The telegram bot is a private project to inform the developer of the bot himself.
There is not warranty that the information sent here is correct!
You can view the source-code of the Bot on GitHub: https://github.com/jpylypiw/corona-germany-telegram-bot

*Commands* the bot can answer:
/subscribe - start subsctiption of news and statistics
/unsubscribe - stop the subscription to news and statistics

If you don't want to use the bot anymore you can simply delete the chat.
"""

        self.send_message(update.effective_chat.id, text_de, context.bot.send_message)
        self.send_message(update.effective_chat.id, text_en, context.bot.send_message)

    def subscribe(self, update, context):
        """
        TODO: Doku
        """
        succeeded = self.users.add_user(update.effective_chat.id)
        if succeeded:
            text_de = """
Vielen Dank für die Bestellung der News und Statistiken!
Wir senden ab sofort alle News und Statistiken bei der nächsten Generierung an dich.
"""
            text_en = """
Thank you for subscribing to the news!
We will send you the next news when we got some.
"""
        else:
            text_de = """
Whoopsie, du hast die Nachrichten schon aboniert.
"""
            text_en = """
You have already subscribed to the news.
"""
        self.send_message(update.effective_chat.id, text_de, context.bot.send_message)
        self.send_message(update.effective_chat.id, text_en, context.bot.send_message)

    def unsubscribe(self, update, context):
        """
        TODO: Doku
        """
        self.users.remove_user(update.effective_chat.id)
        text_de = """
Du wurdest hast dich erfolgreich von der Datenlieferung abgemeldet.
Vielen Dank für die Nutzung vom *Corona Germany Telegram Bot*!
Du wirst ab sofort keine Nachrichten mehr erhalten.
"""
        text_en = """
You successfully unsubscribed from the list.
Thanks for using *Corona Germany Telegram Bot*!
You will no longer receive any messages.
"""
        self.send_message(update.effective_chat.id, text_de, context.bot.send_message)
        self.send_message(update.effective_chat.id, text_en, context.bot.send_message)

    def send_message(self, chat_id, text, func, parse_mode="Markdown",
                     disable_web_page_preview=True):
        """
        TODO: Doku
        """
        try:
            func(chat_id=chat_id, text=text, parse_mode=parse_mode,
                 disable_web_page_preview=disable_web_page_preview)
        except Exception as exc:
            error("Error sending message: {}".format(format_exception(exc)))
