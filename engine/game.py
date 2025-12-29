from card import Card
from player import Player
import random



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
        #create all 58 basic cards: 5 organ, 4 virus, 4 vaccine per color + rainbow: 1 organ, 1 virus, 4 vaccine
        for color in ["red", "green", "blue", "yellow"]:
            for _ in range(5): self.cards.append(Card(color=color, value=0))
            for _ in range(4): self.cards.append(Card(color=color, value=-1))
            for _ in range(4): self.cards.append(Card(color=color, value=1))
        #rainbow cards   
        self.cards.append(Card(color="rainbow", value=0))
        self.cards.append(Card(color="rainbow", value=-1))
        for _ in range(4): self.cards.append(Card(color="rainbow", value=1))
        #append special cards later TOBEDONE
        #shuffle the deck at the end
        random.shuffle(self.cards)
        print(len(self.cards)) #for testing purposes

class Game:

    deck = Deck() #list of all 68 cards but in random order 

    def __init__(self):
        self.players = []
        self.index_of_current_player = 0
        self.players_number = 0
        self.winner = None
    
    # players handling
    def add_player(self, player: Player):
        if player in self.players:
            raise ValueError("Player already in the game!")
        if len(self.players) >= 8:
            raise ValueError("Maximum number of players reached!")
        self.players.append(player)
        self.players_number = len(self.players)
    
    def remove_player(self, player: Player):
        self.players.remove(player)
        self.players_number = len(self.players)
    
    def get_current_player(self) -> Player:
        return self.players[self.index_of_current_player]
    
    # card handling
    def draw_card_for_player(self, player: Player):
        card = self.deck.draw_card()
        player.on_hand.append(card)

    def discard_card_from_player(self, player: Player, card: Card):
        player.on_hand.remove(card)
        self.deck.discard_card(card)

    # game flow
    def check_if_winner(self):
        if self.players[self.index_of_current_player].check_win_condition():
            self.winner = self.players[self.index_of_current_player]
            return self.players[self.index_of_current_player]
        return None

    def move(self, player: Player, attempt):
        pass #to be implemented later

    def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Not enough players to start the game!")
        self.deck.initialize_deck()
        #deal 3 cards to each player
        for player in self.players:
            for _ in range(3):
                self.draw_card_for_player(player)
        #game starts
        while True:
            current_player = self.players[self.index_of_current_player]
            attempt = current_player.attempt_move()
            # Check for a winner after the turn
            winner = self.check_if_winner()
            # For now, we just move to the next player
            self.index_of_current_player = (self.index_of_current_player + 1) % self.players_number
            # This is just a placeholder to prevent an infinite loop in this example
            break




#main function for testing
if __name__ == "__main__":
    game = Game()
    player1 = Player("Alice")
    player2 = Player("Bob")
    game.add_player(player1)
    game.add_player(player2)
    game.start_game()
    for player in game.players:
        print(f"{player.name}'s hand: {[f'{card.color}({card.value})' for card in player.on_hand]}")