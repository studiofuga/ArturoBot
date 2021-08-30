"""
Bot Arturo - A Telegram bot to control Social Networks bots
"""
import os

import telegram.ext
from telegram.ext import Updater
import logging
import arturo_conf
import tweepy
import sys
import requests
import tempfile
from PIL import Image
import pytesseract


class Arturo:
    def __init__(self):
        self.updater = Updater(token=arturo_conf.TG_TOKEN, use_context=True)
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('connect', self.connect))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('timeline', self.timeline))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('get', self.cmd_get))

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
        tweets = self.twitter.home_timeline(count=5, tweet_mode="extended")
        for tweet in tweets:
            context.bot.send_message(chat_id=update.effective_chat.id, text="From {}: {}".format(tweet.user.name, tweet.full_text))

    def _download(self, url, outfile, delete : bool = True):
        logging.log(logging.INFO, "Downloading: {}".format(url))
        r = requests.get(url, allow_redirects=True)
        outfile.write(r.content)
        outfile.close()

    def _download_media(self,update : telegram.Update, context : telegram.ext.CallbackContext, entities, delete : bool = True):
        for media in entities["media"]:
            try:
                type = media["type"]
                if type == "video":
                    for variant in media["video_info"]["variants"]:
                        if variant["content_type"] == "video/mp4":
                            url = variant["url"]
                            break
                elif type == "photo":
                    url = media["media_url"]
                try:
                    outfile = tempfile.NamedTemporaryFile(mode='wb', delete=False)
                    filename = outfile.name
                    self._download(url, outfile, delete=delete)
                    logging.log(logging.INFO, "File Size: {}".format(os.path.getsize(filename)))
                    infile = open(filename, mode='rb')
                    context.bot.send_video(chat_id=update.effective_chat.id,
                                           caption="file: {}".format(filename),
                                           video=infile)
                    if delete:
                        os.remove(filename)
                    else:
                        return (type, filename)
                except Exception as x:
                    logging.log(logging.ERROR, "Failed downloading: {}".format(x))
                    context.bot.send_message(chat_id=update.effective_chat.id, text="video: {}".format(url))
                return (type,url)
            except:
                pass

        return None

    def cmd_get(self,update : telegram.Update, context : telegram.ext.CallbackContext):
        if not self._check_twitter(update, context):
            return
        if len(context.args) !=1 :
            context.bot.send_message(chat_id=update.effective_chat.id, text="Format: /get tweet-id")
            return

        try:
            id = int(context.args[0])
            tweet = self.twitter.get_status(id, tweet_mode="extended")
            logging.log(level=logging.INFO, msg="Tweet: {}".format(tweet._json))
            context.bot.send_message(chat_id=update.effective_chat.id, text="From: {}\n{}"
                                     .format(tweet.user.name, tweet.full_text))

            count = 0
            if hasattr(tweet, 'extended_entities'):
                if "media" in tweet.extended_entities:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="There are: {} native media".format(
                        len(tweet.extended_entities["media"])))
                    info = self._download_media(update, context, tweet.extended_entities, delete = False)
                    if info is not None:
                        count = 1
                        if info[0] == "photo":
                            image = Image.open(info[1])
                            text = pytesseract.image_to_string(image=image)
                            context.bot.send_message(chat_id=update.effective_chat.id, text="Image text: {}"
                                                     .format(text))


            if count == 0:
                if hasattr(tweet, 'entities'):
                    if "media" in tweet.entities:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="There are: {} media".format(
                            len(tweet.entities["media"])))
                        filename = self._download_media(update, context, tweet.entities)
                        if filename is not None:
                            count = 1

        except Exception as x:
            msg = "An error occurred: {}".format(x)
            logging.log(level=logging.ERROR, msg=msg)
            logging.log(level=logging.ERROR, msg='Error on line {} {} {}'.format(sys.exc_info()[-1].tb_lineno, type(x).__name__, x))

            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


    def run(self):
        self.updater.start_polling()


if __name__ == "__main__":
    bot = Arturo()
    bot.run()

