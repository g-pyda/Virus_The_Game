from card import Card, Stack, SpecialCard
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
        #append special cards
        for _ in range(3): self.cards.append(SpecialCard(card_type="organ swap"))
        self.cards.append(SpecialCard(card_type="body swap"))
        for _ in range(3): self.cards.append(SpecialCard(card_type="thieft"))
        self.cards.append(SpecialCard(card_type="latex glove"))
        for _ in range(2): self.cards.append(SpecialCard(card_type="epidemy"))

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
        self.turn_number = 0
    
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
            return True
        return False

    def resolve_attempt(self, player: Player, attempt):
        match attempt.action:
            case "attack":
                if attempt.target_player is None or attempt.target_stack is None:
                    raise ValueError("No target player or stack specified for attack!")
                if (attempt.target_stack.color != "rainbow" and attempt.card.color != "rainbow"):
                    if attempt.target_stack.color != attempt.card.color:
                        raise ValueError("Card color does not match stack color!")
                if attempt.target_stack.status == "immune":
                    raise ValueError("Cannot attack this stack!")
                isdead = attempt.target_player.add_card_to_stack(attempt.target_stack, attempt.card)
                player.on_hand.remove(attempt.card)
                if isdead:
                    #move the stack's cards to discard pile
                    attempt.target_player.remove_stack(attempt.target_stack)
                    for card in attempt.target_stack.cards:
                        self.deck.discard_card(card)

            case "heal": #handles rainbow
                if attempt.target_stack is None:
                    raise ValueError("No target stack specified for healing/vaccinating!")
                if (attempt.target_stack.color != "rainbow" and attempt.card.color != "rainbow"):
                    if attempt.target_stack.color != attempt.card.color:
                        raise ValueError("Card color does not match stack color!")
                if attempt.target_stack.status == "immune":
                    raise ValueError("Stack is already immune!")
                player.add_card_to_stack(attempt.target_stack, attempt.card)
                if attempt.target_stack.status == "healthy": # it means the virus was removed by vaccine - both go to discard
                    attempt.target_stack.cards.remove(attempt.card) # remove vaccine from stack
                    virus_card = next(card for card in attempt.target_stack.cards if card.value == -1)
                    attempt.target_stack.cards.remove(virus_card)
                    self.deck.discard_card(virus_card)
                else:
                    self.deck.discard_card(attempt.card) # discard vaccine card
                player.on_hand.remove(attempt.card) # remove from hand, NOT handled in add_card_to_stack


            case "organ":
                if attempt.card.color != "rainbow":
                    if any(stack.color == attempt.card.color for stack in player.laid_out):
                        raise ValueError("You already have an organ of this color laid out!")
                else:
                    player.lay_out_organ(attempt.card)
                    
            case "discard":
                for card in attempt.discard_cards:
                    self.discard_card_from_player(player, card)
            case "special":
                #check if possible
                match attempt.card.card_type:
                    case "organ swap":
                        if attempt.target_stack.color != attempt.stack.color and attempt.target_stack.color != "rainbow" and attempt.stack.color != "rainbow" and (attempt.target_stack.color in [stack.color for stack in player.laid_out] or attempt.stack.color in [stack.color for stack in attempt.target_player.laid_out]):
                            raise ValueError("Cannot swap these organs!")
                        attempt.stack, attempt.target_stack = attempt.target_stack, attempt.stack
                        #swap stacks between players but im not sure if it works like i want it to do

                    case "thieft":
                        if attempt.target_stack.status == "immune":
                            raise ValueError("Cannot steal from an immune stack!")
                        if len(attempt.target_stack.cards) == 0:
                            raise ValueError("Target stack has no cards to steal!")
                        if attempt.target_stack.color in [stack.color for stack in player.laid_out]:
                            raise ValueError("You already have an organ of this color laid out!")
                        stolen_card = attempt.target_stack
                        attempt.target_player.remove_stack(attempt.target_stack)
                        player.laid_out.append(stolen_card)
                        #chyba jest git, ale wszystkie karty specjalne pisałam z gorączką więc do sprawdzenia
                        
                    case "body swap": #there are no restrictions on body swap 
                        attempt.player.laid_out, attempt.target_player.laid_out = attempt.target_player.laid_out, attempt.player.laid_out
                        #swap all stacks between players
                        
                    case "latex glove":
                        for player in self.players:
                            for card in player.on_hand:
                                self.discard_card_from_player(player, card)
                    case "epidemy":
                        for i in range(len(attempt.virus_cards)):
                            virus_card = attempt.virus_cards[i]
                            #target_player = attempt.target_players[i] #not used but i think it should be used ? TOBEDONE
                            target_stack = attempt.target_stacks[i]
                            if virus_card.value != -1:
                                raise ValueError("Only virus cards can be given away in an epidemy!")
                            if target_stack.status != "healthy":
                                raise ValueError("You can only give a virus to a healthy stack!")
                            if target_stack.color != "rainbow":
                                if virus_card.color != "rainbow":
                                    if target_stack.color != virus_card.color:
                                        raise ValueError("Virus card color does not match target stack color!")
                            attempt.player.remove_card_from_stack(attempt.player_stacks[i], virus_card)
                            target_stack.add_card(virus_card)
                    case _:
                        raise ValueError("Invalid special card type!")
                self.deck.discard_card(attempt.card)
                player.on_hand.remove(attempt.card)
            case _:
                raise ValueError("Invalid action in attempt!")

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
            self.turn_number += 1
            current_player = self.players[self.index_of_current_player]
            if current_player.on_hand != 0:
                attempt = current_player.attempt_move()
                self.resolve_attempt(current_player, attempt)

                is_there_winner = self.check_if_winner()
                if is_there_winner: 
                    #current_player is the winner
                    break

            while current_player.cards.on_hand < current_player.max_cards_on_hand:
                self.draw_card_for_player(current_player)

            self.index_of_current_player = (self.index_of_current_player + 1) % self.players_number
            break #remove later, currently to not end up in infinite loop




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
