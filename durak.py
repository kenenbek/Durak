import random
from emoji import emojize
import heapq
from typing import Union


class Game:
    def __init__(self, large=False, players_amount=2):
        random.seed(123456)
        self.cards = {}
        self.players = {}
        self.prikup = []
        self.pile = []
        self.trump = None
        self.players_amount = players_amount
        self.round = []
        
        # create cards
        deck = Deck()
        random.shuffle(deck)
        
        self.prikup = deck
        self.trump_suit = self.prikup[0].suit
        self.nominal_weights = {n: w for w, n in enumerate(deck.nominals)}
        
        # create bot with id=0
        bot = BotPlayer(id=0, nominal_weights=self.nominal_weights)
        self.players[0] = bot
        # create players
        for i in range(1, self.players_amount):
            player = UserPlayer(id=i, nominal_weights=self.nominal_weights)
            self.players[i] = player
        
        # give away cards to players
        for player_id in self.players:
            cards = self.get_cards(amount=6)
            self.players[player_id].take_cards(cards, self.trump)
    
    def determine_first_player(self):
        min_trump_weight = float('inf')
        first_player = None
        
        # determine first player to move
        for _, player in self.players.items():
            trump = player.show_minimum_trump_card()
            if trump is not None:
                trump_weight = self.nominal_weights[trump.nominal]
                if trump_weight < min_trump_weight:
                    min_trump_weight = trump_weight
                    first_player = player
        
        if first_player is None:
            random_id = random.randint(0, len(self.players) - 1)
            first_player = self.players[random_id]
        
        # TODO always return user
        first_player = self.players[0]
        return first_player
    
    def get_cards(self, amount):
        # return self.prikup.pop()
        cards = self.prikup[-amount:]
        self.prikup = self.prikup[:-amount]
        return cards
    
    def is_valid(self, attacking_card: str, defending_card: str, trump_suit: str):
        attacking_weight = self.nominal_weights[attacking_card[1:]]
        defending_weight = self.nominal_weights[defending_card[1:]]
        if attacking_weight < defending_weight and attacking_card[0] == defending_card[0] or \
            attacking_card[0] == trump_suit and defending_card[0] != trump_suit:
            return True
        else:
            return False
    
    # def run(self):
    #     player = self.determine_first_player()
    #
    #     while True:
    #         table_cards = []
    #         while player.can_attack()


class Deck:
    def __init__(self, large=False):
        """
        `self.prikup` has a reverse order
        :param large:
        """
        self.cards_dict = {}
        self.cards_list = []
        suits = ["spades", "hearts", "diamonds", "clubs"]
        self.suits = [self.to_emoji(suit) for suit in suits]
        self.nominals = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        
        if large:
            self.nominals = ["2", "3", "4", "5"] + self.nominals
        
        # create game cards
        for suit in self.suits:
            for nominal in self.nominals:
                card_id = (suit, nominal)
                card = Card(suit=suit, nominal=nominal)
                
                self.cards_dict[card_id] = card
                self.cards_list.append(card)
    
    def __getitem__(self, item):
        return self.cards_list[item]
    
    def __len__(self):
        return len(self.cards_list)
    
    def __setitem__(self, key, value):
        self.cards_list[key] = value
    
    def to_emoji(self, suit):
        return emojize(':{}:'.format(suit), use_aliases=True)


class Card:
    def __init__(self, suit, nominal):
        self.suit = suit
        self.nominal = nominal
    
    def __str__(self):
        return '{}{}'.format(self.suit, self.nominal)
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other):
        return self.nominal < other.nominal
    
    def __eq__(self, other):
        return self.nominal == other.nominal and self.suit == other.suit


class Cards:
    def __init__(self):
        self.cards = []
    
    def insert(self, new_card: Card):
        self.cards.append(new_card)
        self.cards.sort(key=lambda x: x.nominal)
    
    def to_string(self):
        res = []
        for card in self.cards:
            res.append(card.__str__())
        return res
    
    def remove(self, card: Card):
        self.cards.remove(card)
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, item):
        return self.cards[item]


class Player:
    def __init__(self, id, nominal_weights):
        self.id = id
        self.nominal_weights = nominal_weights
        self.cards = Cards()
        self.trumps = Cards()
    
    def take_cards(self, new_cards, trump):
        for new_card in new_cards:
            if type(new_card) == str:
                new_card = Card(new_card[0], new_card[1:])
            if new_card.suit == trump:
                self.trumps.insert(new_card)
            else:
                self.cards.insert(new_card)
    
    def remove_card(self, card: str):
        suit = card[0]
        nominal = card[1:]
        
        temp_card = Card(suit, nominal)
        
        try:
            self.cards.remove(temp_card)
        except ValueError:
            pass
        try:
            self.trumps.remove(temp_card)
        except ValueError:
            pass
    
    def take_cards_heap(self, new_cards, trump):
        for card in new_cards:
            if card.suit == trump:
                heapq.heappush(self.trumps, card)
            else:
                heapq.heappush(self.cards, card)
    
    def show_minimum_trump_card(self) -> Union[Card, None]:
        if len(self.trumps) > 0:
            return self.trumps[0]
        else:
            return None
    
    def attack(self, round_cards):
        if len(round_cards) == 0:
            if len(self.cards) > 0:
                card = self.cards[0]
                self.cards.remove(card)
                return card
            elif len(self.trumps) > 0:
                card = self.trumps[0]
                self.trumps.remove(card)
                return card
            else:
                raise ValueError
        else:
            for own_card in self.cards:
                for round_card in round_cards:
                    if own_card.nominal == round_card[1:]:
                        self.cards.remove(own_card)
                        return own_card
                    
            for own_trump in self.trumps:
                for round_card in round_cards:
                    if own_trump.nominal == round_card[1:]:
                        self.trumps.remove(own_trump)
                        return own_trump
        
        return None
        
    def defend(self, attack_card_name: str):
        attack_suit = attack_card_name[0]
        attack_nominal_weight = self.nominal_weights[attack_card_name[1:]]
        
        reply_card = None
        
        # search in cards
        for defend_card in self.cards:
            defend_card_weight = self.nominal_weights[defend_card.nominal]
            if defend_card.suit == attack_suit and defend_card_weight > attack_nominal_weight:
                reply_card = Card(suit=defend_card.suit, nominal=defend_card.nominal)
                self.cards.remove(reply_card)
                break
        # search in trumps
        if not reply_card:
            if len(self.trumps) > 0:
                reply_card = self.trumps[0]
                self.trumps.remove(reply_card)
        
        return reply_card
    
    def __str__(self):
        if self.id == 0:
            return "bot's"
        elif self.id == 1:
            return "your"
        else:
            raise ValueError


class BotPlayer(Player):
    def __init__(self, *args, **kwargs):
        super(BotPlayer, self).__init__(*args, **kwargs)


class UserPlayer(Player):
    def __init__(self, *args, **kwargs):
        super(UserPlayer, self).__init__(*args, **kwargs)


def create_game():
    game = Game()
    
    game.players[0]


if __name__ == '__main__':
    game = Game()
