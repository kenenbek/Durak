from telegram import Update
from telegram.ext import CallbackContext
from keyboard_markup import create_card_keyboard_markup, USER_DEFEND, START


def start_round(update: Update, context: CallbackContext):
    user_data = context.user_data
    
    if "bot_continue_attack" in user_data:
        msg = "Bot thinks about continuing attack"
        del user_data["bot_continue_attack"]
    else:
        msg = "A new round is started"
    
    update.message.reply_text(
        msg
    )
    return


def finish_round(update: Update, context: CallbackContext):
    user_data = context.user_data
    
    player = user_data['player']
    bot = user_data['bot']
    user = user_data['user']
    game = user_data['game']
    
    if "bot_pickup" in user_data:
        del user_data['bot_pickup']
        pickup_cards = " ".join([str(card) for card in game.round])
        bot.take_cards(game.round, game.trump_suit)
        
        update.message.reply_text(
            "Bot's pick up " + pickup_cards + "!"
        )
        game.round = []
    else:
        bot_card_amount = len(bot.cards) + len(bot.trumps)
        
        if bot_card_amount < 6:
            new_bot_cards = game.get_cards(6 - bot_card_amount)
            bot.take_cards(new_bot_cards, game.trump_suit)
    
    if "user_pickup" in user_data:
        del user_data["user_pickup"]
        
        pickup_cards = " ".join([str(card) for card in game.round])
        user.take_cards(game.round, game.trump_suit)
        
        markup = create_card_keyboard_markup(user, USER_DEFEND, game.round, game.trump_suit)
        update.message.reply_text(
            "You've pick up the cards {}".format(pickup_cards),
            reply_markup=markup,
        )

        game.round = []
    
    else:
        player_card_amount = len(player.cards) + len(player.trumps)
        
        if player_card_amount < 6:
            new_cards = game.get_cards(6 - player_card_amount)
            cards_str = [str(new_card) for new_card in new_cards]
            player.take_cards(new_cards, game.trump_suit)
            
            update.message.reply_text(
                "These are your new cards: \n{}".format(" ".join(cards_str)),
                reply_markup=create_card_keyboard_markup(user_data['user'], START, game.round, game.trump_suit)
            )

    update.message.reply_text(
        "The round is finished"
    )
    
    return
