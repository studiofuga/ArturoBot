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
        self.dispatcher.add_handler(telegram.ext.CommandHandler('connect', self.connect))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('timeline', self.timeline))

        self.twitter_avail = False

    def _check_twitter(self,update : telegram.Update, context : telegram.ext.CallbackContext):
        if not self.twitter_avail or self.twitter is None:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Twitter non è connesso. Provo a connettermi.")
            self.connect(update, context)
            return False
        return True

    def start(self,update : telegram.Update, context : telegram.ext.CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao sono Arturito, in che modo posso aiutarti?")

    def connect(self,update : telegram.Update, context : telegram.ext.CallbackContext):
        self.twitter_auth = tweepy.OAuthHandler(arturo_conf.TWITTER_API_KEY, arturo_conf.TWITTER_SEC_KEY)
        self.twitter_auth.set_access_token(arturo_conf.TWITTER_USR_KEY, arturo_conf.TWITTER_USR_TOKEN)
        self.twitter = tweepy.API(self.twitter_auth)

        try:
            self.twitter.verify_credentials()
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ok, sono autenticato su twitter")
            self.twitter_avail=True
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Autenticazione su twitter fallita")

    def timeline(self,update : telegram.Update, context : telegram.ext.CallbackContext):
        if not self._check_twitter(update, context):
            return
        tweets = self.twitter.home_timeline(count=5)
        for tweet in tweets:
            context.bot.send_message(chat_id=update.effective_chat.id, text="From {}: {}".format(tweet.user.name, tweet.text))


    def run(self):
        self.updater.start_polling()


if __name__ == "__main__":
    bot = Arturo()
    bot.run()

