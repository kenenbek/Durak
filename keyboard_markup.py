from telegram import ReplyKeyboardMarkup

from durak import Player

START, USER_ATTACK, USER_DEFEND = range(3)


def create_card_keyboard_markup(player: Player, ROUND_TYPE, round_cards, trump_suit):
    cards = player.cards.to_string()  # list of str, where 0 -- is a suit
    trumps = player.trumps.to_string()
    cards_to_attack = set()
    other_cards = set()
    other_trumps = set()
    
    for i, card in enumerate(cards):
        for round_card in round_cards:
            if card[1:] == round_card[1:]:
                cards_to_attack.add(card)
            else:
                other_cards.add(card)
    
    for i, card in enumerate(trumps):
        for round_card in round_cards:
            if card[1:] == round_card[1:]:
                cards_to_attack.add(card)
            else:
                other_trumps.add(card)
    
    cards_to_attack = list(cards_to_attack)
    other_cards = build_menu(list(other_cards), 6)
    other_trumps = build_menu(list(other_trumps), 6)
    
    _keyboard = [*other_cards,
                 ["Your trumps:  " + trump_suit],
                 *other_trumps]
    
    if ROUND_TYPE == START or ROUND_TYPE == USER_ATTACK and len(round_cards) == 0:
        keyboard = [["Your cards:"]] + _keyboard
    elif ROUND_TYPE == USER_ATTACK and len(cards_to_attack) > 0:
        keyboard = [
                       ["Finish the round"],
                       ["Cards to attack:"] + cards_to_attack,
                       ["Other cards:"]
                   ] + _keyboard
    elif ROUND_TYPE == USER_ATTACK and len(cards_to_attack) == 0:
        keyboard = [
                       ["Finish round"],
                   ] + _keyboard
    # =====================================================
    # Defense user markup
    # =====================================================
    elif ROUND_TYPE == USER_DEFEND:
        keyboard = [
                       ["Pick up", "Your cards:"],
                   ] + _keyboard
    # =====================================================
    # User pickup cards
    # =====================================================
    else:
        raise ValueError("No such type")
    
    markup = ReplyKeyboardMarkup(keyboard)
    
    return markup


def build_menu(buttons,
               n_cols
               ):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
 
    return menu
