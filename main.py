import os
import telegram
from telegram.ext import Updater, CommandHandler


def start(update, context):
    custom_keyboard = [['top-left', 'top-right'],
                       ['bottom-left', 'bottom-right']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Custom Keyboard Test",
                             reply_markup=reply_markup)


if __name__ == '__main__':
    token = os.getenv("vduraka_token")
    updater = Updater(token=token, use_context=True)
    
    start_handler = CommandHandler('start', start)
    updater.dispatcher.add_handler(start_handler)
    
    updater.start_polling()
