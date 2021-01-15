#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Dict

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
CallbackQueryHandler
)

from durak import Game, BotPlayer, UserPlayer
from keyboard_markup import create_card_keyboard_markup
from defend import bot_attack_move, user_defend_move
from attack import user_attack_move
from finish_round import start_round, finish_round
from emoji import emojize

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

START, USER_ATTACK, USER_DEFEND = range(3)


def start_conv(update: Update, context: CallbackContext) -> int:
    from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
    start_keyboard = [['Play with a bot', 'Results']]
    
    start_markup = ReplyKeyboardMarkup(start_keyboard)
    
    update.message.reply_text(
        "Hi! Welcome to Durak game!",
        reply_markup=start_markup,
    )
    
    return START


def start_game(update: Update, context: CallbackContext) -> int:
    game = Game()
    
    bot = game.players[0]
    user = game.players[1]
    TURN = None
    
    markup = create_card_keyboard_markup(user, START, game.round, game.trump_suit)
    
    text = update.message.text
    context.user_data['game'] = game
    context.user_data['user'] = user
    context.user_data['bot'] = bot
    context.user_data['choice'] = text
    
    first_move_player = game.determine_first_player()
    
    if type(first_move_player) == BotPlayer:
        context.user_data['player'] = bot
        msg = "It's {} turn\n".format(context.user_data['player'])
        
        update.message.reply_text(
            msg, reply_markup=markup,
        )
        bot_attack_move(update, context)
        
        return USER_DEFEND
    
    elif type(first_move_player) == UserPlayer:
        context.user_data['player'] = user
        return USER_ATTACK
    else:
        raise TypeError("Player type Error")


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    
    update.message.reply_text(
        "I learned these facts about you:" "{}" "Until next time!".format(facts_to_str(user_data))
    )
    
    user_data.clear()
    return ConversationHandler.END


from conversationbot2 import regular_choice


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    import os
    updater = Updater(os.getenv("vduraka_token"), use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_conv)],
        states={
            START: [
                MessageHandler(
                    Filters.regex('^Play with'), start_game
                )
            ],
            USER_ATTACK: [
                MessageHandler(
                    Filters.regex('^Finish round'), finish_round
                ),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    user_attack_move,
                ),
            ],
            USER_DEFEND: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    user_defend_move,
                )
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )
    
    dispatcher.add_handler(conv_handler)
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
