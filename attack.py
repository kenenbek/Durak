from telegram import Update
from telegram.ext import CallbackContext
from keyboard_markup import create_card_keyboard_markup, START, USER_DEFEND, USER_ATTACK
from finish_round import start_round, finish_round



def user_attack_move(update: Update, context: CallbackContext) -> int:
    start_round(update, context)
    
    user_data = context.user_data
    attacking_card = update.message.text
    
    bot = user_data['bot']
    game = user_data["game"]
    user = user_data["user"]
    
    game.round.append(attacking_card)
    user.remove_card(attacking_card)
    
    if attacking_card != "Finish the round":
        markup = create_card_keyboard_markup(user_data['user'], USER_ATTACK, game.round, game.trump_suit)
        update.message.reply_text(
            "You've attacked with {}".format(attacking_card),
            reply_markup=markup,
        )
        
        reply_card = bot.defend(attacking_card)
        
        if reply_card is None:
            update.message.reply_text("Bot is unable to beat your card. Do you want to continue?")
            user_data["bot_pickup"] = True
            
            user_continue_when_bot_pickup(update, context)
            finish_round(update, context)
            
            return USER_ATTACK
        else:
            markup = create_card_keyboard_markup(user_data['user'], USER_ATTACK, game.round, game.trump_suit)
            update.message.reply_text("Bot's replied with {}".format(reply_card),
                                      reply_markup=markup)
            game.round.append(str(reply_card))
    else:
        return USER_DEFEND



def user_continue_when_bot_pickup(update: Update, context: CallbackContext) -> int:
    
    while True:
        user_data = context.user_data
        game = user_data['game']
        attacking_card = update.message.text
        
        if attacking_card == "Finish the round":
            break
        else:
            game.round.append(attacking_card)
    
    return