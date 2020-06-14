"""
TODO: Doku
"""
from corona_germany_telegram_bot.config import Config


class Users(object):
    """
    TODO: Doku
    """

    def __init__(self, cfg: Config):
        self.usersconfig = cfg

    def add_user(self, chat_id):
        """
        TODO: Doku
        """
        curr_ids = str(self.usersconfig.get_value("USERS", "chat_ids"))
        chat_id = str(chat_id)
        prefix = ";"
        if curr_ids == "":
            prefix = ""
        if chat_id not in curr_ids:
            self.usersconfig.set_value("USERS", "chat_ids", "{}{}{}".format(
                curr_ids, prefix, chat_id))
            return True
        return False

    def remove_user(self, chat_id):
        """
        TODO: Doku
        """
        curr_ids = self.get_user_list()
        curr_ids.remove(str(chat_id))
        self.usersconfig.set_value("USERS", "chat_ids", ';'.join(curr_ids))

    def get_user_list(self):
        """
        TODO: Doku
        """
        curr_ids = str(self.usersconfig.get_value("USERS", "chat_ids"))
        return curr_ids.split(';')
