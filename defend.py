from telegram import Update
from telegram.ext import CallbackContext
from keyboard_markup import create_card_keyboard_markup, START, USER_DEFEND, USER_ATTACK
from finish_round import start_round, finish_round


def bot_attack_move(update: Update, context: CallbackContext):
    start_round(update, context)
    
    user_data = context.user_data
    bot = user_data['bot']
    game = user_data['game']
    user = user_data['user']
    
    attacking_card = str(bot.attack(game.round))
    user_data['attacking_card'] = attacking_card

    if attacking_card != "None":
        game.round.append(attacking_card)
        
        markup = create_card_keyboard_markup(user, USER_DEFEND, game.round, game.trump_suit)
        update.message.reply_text("Bot is attacking with {}".format(attacking_card),
                                  reply_markup=markup)
        return USER_DEFEND
    else:
        update.message.reply_text(
                "Bot has no card to continue attacking"
            )
        finish_round(update, context)

        markup = create_card_keyboard_markup(user, START, game.round, game.trump_suit)
        update.message.reply_text(
            "Now it's your turn", reply_markup=markup
        )
        return USER_ATTACK


def user_defend_move(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    defend_card = update.message.text
    
    user = user_data['user']
    game = user_data['game']
    attacking_card = user_data['attacking_card']
    
    if defend_card == "Pick up":
        user_data["user_pickup"] = True
        finish_round(update, context)
        # bot attack again
        bot_attack_move(update, context)
        return USER_DEFEND
    
    elif game.is_valid(attacking_card, defend_card, game.trump_suit):
        markup = create_card_keyboard_markup(user, USER_DEFEND, game.round, game.trump_suit)
        update.message.reply_text(
            "You've defended with {}".format(defend_card),
            reply_markup=markup
        )
        game.round.append(defend_card)
        user_data["bot_continue_attack"] = True
        
        TURN = bot_attack_move(update, context)
        
        return TURN
    
    elif not game.is_valid(attacking_card, defend_card, game.trump_suit):
        update.message.reply_text(
            "Please, defend with a valid card \n {} doesn't beat {}".format(defend_card, attacking_card),
        )
        return USER_DEFEND
    else:
        raise ValueError("Err")
    
    return USER_DEFEND
