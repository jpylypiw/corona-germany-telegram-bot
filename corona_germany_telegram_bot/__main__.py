"""
this is the inofficial corona germany telegram news bot
"""
from logging import error, info

from corona_germany_telegram_bot.bot import Bot
from corona_germany_telegram_bot.log import Log
from corona_germany_telegram_bot.news import News
from corona_germany_telegram_bot.utility import get_abs_path_of_filepath
from corona_germany_telegram_bot.config import Config


def run_bot():
    """
    run_bot is the main function of the program
    """
    configpath = get_abs_path_of_filepath(__file__) + "/../config/config.ini"
    userspath = get_abs_path_of_filepath(__file__) + "/../config/users.ini"
    newspath = get_abs_path_of_filepath(__file__) + "/../config/news.ini"

    config = Config(configpath)
    usersconfig = Config(userspath)
    newsconfig = Config(newspath)

    loglevel = config.get_value("LOG", "level")
    to_stdout = config.get_value("LOG", "to_stdout")
    to_files = config.get_value("LOG", "to_files")
    logpath = config.get_value("LOG", "filepath")
    logfile = config.get_value("LOG", "filename")
    Log(loglevel, to_stdout, to_files, logpath, logfile)

    info("starting telegram bot")

    bot = Bot(config, usersconfig)
    try:
        dispatcher = bot.init_updater()
        news = News(config, newsconfig, usersconfig, dispatcher)
        bot.init_handler()
        bot.start_bot()
        info("telegram bot started")
        news.start_thread()
    except KeyboardInterrupt:
        news.stopflag = True
    except Exception as exc:
        error("Unhandled Exception: {}".format(exc))


if __name__ == "__main__":
    run_bot()
