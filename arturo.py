"""
Bot Arturo - A Telegram bot to control Social Networks bots
"""
import telegram.ext
from telegram.ext import Updater
import logging
import arturo_conf
import tweepy


class Arturo:
    def __init__(self):
        self.updater = Updater(token=arturo_conf.TG_TOKEN, use_context=True)
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start))

    def start(self,update : telegram.Update, context : telegram.ext.CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao sono Arturito, in che modo posso aiutarti?")

    def run(self):
        self.updater.start_polling()


if __name__ == "__main__":
    bot = Arturo()
    bot.run()

