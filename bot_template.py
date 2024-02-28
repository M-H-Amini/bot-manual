from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import telegram
from time import sleep
from mh_utils import getAlphaData, bollingerBands, visualize, readCSV

mha = '232895376'

bot = telegram.Bot(token=open('bot_token.txt').read().strip())

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello World!')

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)

def sendMessage(text):
    bot.send_message(chat_id=mha, text=text)

def sendPhoto(photo):
    bot.send_photo(chat_id=mha, photo=open(photo, 'rb'))

def main():
    updater = Updater(open('bot_token.txt').read().strip(), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    i = 0
    while True:
        try:
            sendMessage(f'Hello World! {i}')
            sendPhoto('a.png')
            print(i)
            i -=- 1
            sleep(60)

        except Exception as e:
            print(e)
            bot.send_message(chat_id=mha, text=str(e))
            sleep(60)

if __name__ == '__main__':
    main()