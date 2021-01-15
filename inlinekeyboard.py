#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards.
"""
import logging
import emoji

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton(emoji.emojize(":spades:", use_aliases=True), callback_data='1'),
            InlineKeyboardButton(emoji.emojize(":hearts:", use_aliases=True), callback_data='2'),
            InlineKeyboardButton(emoji.emojize(":diamonds:", use_aliases=True), callback_data='2'),
            InlineKeyboardButton(emoji.emojize(":clubs:", use_aliases=True), callback_data='2'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_reply_markup(reply_markup=reply_markup)


def button2(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton(emoji.emojize(":kg:", use_aliases=True), callback_data='1'),
            InlineKeyboardButton(emoji.emojize(":ru:", use_aliases=True), callback_data='2'),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_reply_markup(reply_markup=reply_markup)
    #query.edit_message_text(text=f"Selected option: {query.data}")




def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    import os
    token = os.getenv("vduraka_token")
    updater = Updater(token=token, use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))

    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()