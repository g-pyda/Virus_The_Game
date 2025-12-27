class Game:

    deck = Deck() #list of all 68 cards but in random order 
    
    def draw_card_for_player(self, player: Player):
        card = self.deck.draw_card()
        player.on_hand.append(card)

    def discard_card_from_player(self, player: Player, card: Card):
        player.on_hand.remove(card)
        self.deck.discard_card(card)



class Deck:
    def __init__(self):
        self.cards = [] #list of all cards in the deck
        self.discard_pile = [] #list of all discarded cards

    def draw_card(self):
        if len(self.cards) == 0:
            self.reshuffle_cards()
        return self.cards.pop()

    def discard_card(self, card: Card):
        self.discard_pile.append(card)

    def reshuffle_cards(self):
        self.cards.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.cards)

    def initialize_deck(self):
        pass
        #create all cards and add to self.cards
        #shuffle the deck at the end