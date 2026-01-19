from card import Card, Stack, SpecialCard
from player import Player
import random



class Deck:
    def __init__(self):
        self.cards: dict[int, Card] = {} #list of all cards in the deck
        self.discard_pile: dict[int, Card] = {} #list of all discarded cards
        self._next_id = 0

    def draw_card(self):
        if not self.cards:
            self.reshuffle_cards() #reshuffle if no cards left

        card_id = random.choice(list(self.cards.keys()))
        return self.cards.pop(card_id)

    def _add_card(self, card):
        self.cards[card.id] = card

    def discard_card(self, card: Card):
        self.discard_pile[card.id] = card

    def reshuffle_cards(self):
        self.cards.update(self.discard_pile)
        self.discard_pile.clear()
    
    def _add_special(self, card_type):
        card = SpecialCard(id=self._next_id, card_type=card_type)
        self._next_id += 1
        self.cards[card.id] = card

    
    def initialize_deck(self):
        def new_card(color, value):
            card = Card(id=self._next_id, color=color, value=value)
            self._next_id += 1
            self.cards[card.id] = card
        #create all 58 basic cards: 5 organ, 4 virus, 4 vaccine per color + rainbow: 1 organ, 1 virus, 4 vaccine
        for color in ["red", "green", "blue", "yellow"]:
            for _ in range(5): new_card(color, 0)
            for _ in range(4): new_card(color, -1)
            for _ in range(4): new_card(color, 1)
        #rainbow cards   
        new_card("rainbow", 0)
        new_card("rainbow", -1)
        for _ in range(4): new_card("rainbow", 1)
        
        #append special cards
        for _ in range(3): 
            self._add_special("organ swap")
            self._add_special("thieft")
        self._add_special("body swap")
        self._add_special("latex glove")
        for _ in range(2): self._add_special("epidemy")

        print(len(self.cards)) #for testing purposes

class Game:

    def __init__(self):
        self.deck = Deck() #list of all 68 cards

        self.players: dict[int, Player] = {}
        self.player_order: list[int] = []
        self.index_of_current_player = 0
        
        self.players_number = 0
        self.winner = None
        self.turn_number = 0
    
    # players handling
    def add_player(self, name: str, player_id: int):
        if player_id in self.players:
            raise ValueError("Player already in the game!")
        if len(self.players) >= 8:
            raise ValueError("Maximum number of players reached!")
        
        player = Player(name, player_id)
        self.players[player_id] = player
        self.players_number = len(self.players)
        self.player_order.append(player_id)

        return {"id": player_id, "name": name}

    def remove_player(self, player_id: int):
        if player_id not in self.players:
            return None
        del self.players[player_id]
        self.player_order.remove(player_id)
        self.players_number = len(self.players)

        return player_id
    
    # card handling
    def draw_card_for_player(self, player_id: int):
        card = self.deck.draw_card()
        self.players[player_id].on_hand.append(card)
        return {"player_id": player_id, "card_id": card.id}

    def discard_card_from_player(self, player_id: int, card_id: int):
        card = next(card for card in self.players[player_id].on_hand if card.id == card_id)
        self.players[player_id].on_hand.remove(card)
        self.deck.discard_card(card)
        return {"player_id": player_id, "card_id": card.id}
    
        
    def get_stack_by_id(self, stack_id: int):
            # find a stack and its owner by stack_id
            if stack_id is None: return None, None
            for p_id in self.player_order:
                player = self.players[p_id]
                for stack in player.laid_out:
                    if stack.id == stack_id:
                        return stack, player
            return None, None

  

    # game flow
    def check_if_winner(self) -> bool:
        p_id = self.player_order[self.current_player_index]
        if self.players[p_id].check_win_condition():
            self.winner_id = p_id
            return True
        return False

    def resolve_attempt(self, player: Player, attempt):
        result = {"player_id": player.id, "action": attempt.action, "success": True}

        # retrieving objects from ids
        target_player = self.players.get(getattr(attempt, 'target_player_id', None))
        target_stack, stack_owner = self.get_stack_by_id(getattr(attempt, 'target_stack_id', None))
        my_stack, _ = self.get_stack_by_id(getattr(attempt, 'stack_id', None))

        # which special card to remove from hand later
        special_card_to_discard = None
        if attempt.action in ["organ swap", "body swap", "thieft", "epidemy"]:
            special_card_to_discard = next((c for c in player.on_hand if isinstance(c, SpecialCard) and c.card_type == attempt.action), None)
        elif attempt.action == "special": 
            special_card_to_discard = attempt.card
        
        match attempt.action:
            case "attack":
                #check failures
                if target_stack is None: raise ValueError("No target stack specified!")
                if (target_stack.color != "rainbow" and attempt.card.color != "rainbow") and target_stack.color != attempt.card.color:
                    raise ValueError("Card color does not match stack color!")
                if target_stack.status == "immune": raise ValueError("Cannot attack this stack!")
                
                #resolve; delete dead stack
                isdead = stack_owner.add_card_to_stack(target_stack, attempt.card)
                player.on_hand.remove(attempt.card)
                if isdead:
                    stack_owner.remove_stack(target_stack)
                    for card in target_stack.cards: self.deck.discard_card(card)
                result["card_id"] = attempt.card.id

            case "heal" | "vaccinate": #they do almost the same so we can merge them
                if target_stack is None: raise ValueError("No target stack specified!")
                stack_owner.add_card_to_stack(target_stack, attempt.card)

                # if its healthy it means there was virus
                if target_stack.status == "healthy":
                    target_stack.cards.remove(attempt.card)
                    virus_card = next(card for card in target_stack.cards if card.value == -1)
                    target_stack.cards.remove(virus_card)
                    self.deck.discard_card(virus_card)
                    self.deck.discard_card(attempt.card)
                else:
                    self.deck.discard_card(attempt.card)
                player.on_hand.remove(attempt.card)
                result["card_id"] = attempt.card.id

            case "organ":
                if attempt.card.color != "rainbow" and any(stack.color == attempt.card.color for stack in player.laid_out):
                    raise ValueError("You already have an organ of this color!")
                player.lay_out_organ(attempt.card)
                result["card_id"] = attempt.card.id

            case "discard":
                discarded = []
                for card_id in attempt.discard_cards_ids:
                    self.discard_card_from_player(player.id, card_id)
                    discarded.append(card_id) 
                result["discarded_cards"] = discarded

            case "organ swap":
                if target_stack.color != my_stack.color and target_stack.color != "rainbow" and my_stack.color != "rainbow" and (target_stack.color in [s.color for s in player.laid_out] or my_stack.color in [s.color for s in stack_owner.laid_out]):
                    raise ValueError("Cannot swap these organs!")
                idx_me, idx_target = player.laid_out.index(my_stack), stack_owner.laid_out.index(target_stack)
                player.laid_out[idx_me], stack_owner.laid_out[idx_target] = stack_owner.laid_out[idx_target], player.laid_out[idx_me]

            case "thieft":
                # stealing stack but it cant be immune nor in the color we already have
                if target_stack.status == "immune" or target_stack.color in [s.color for s in player.laid_out]:
                    raise ValueError("Cannot steal this organ!")
                stack_owner.laid_out.remove(target_stack)
                player.laid_out.append(target_stack)
                result["stolen_stack_color"] = target_stack.color

            case "body swap":
                #there are no restrictions on body swap
                player.laid_out, target_player.laid_out = target_player.laid_out, player.laid_out

            case "special": # latex glove
                for p in self.players.values():
                    if p.id != player.id:
                        for c in list(p.on_hand): self.discard_card_from_player(p.id, c.id)

            case "epidemy":
                for i in range(len(attempt.virus_cards_ids)):
                    v_card = next(c for s in player.laid_out for c in s.cards if c.id == attempt.virus_cards_ids[i])
                    p_stack, _ = self.get_stack_by_id(attempt.player_stacks_ids[i])
                    t_stack, _ = self.get_stack_by_id(attempt.target_stacks_ids[i])
                    p_stack.remove_card(v_card)
                    t_stack.add_card(v_card)

            case _:
                raise ValueError("Invalid action!")

        #remove special cards from hand
        if special_card_to_discard:
            player.on_hand.remove(special_card_to_discard)
            self.deck.discard_card(special_card_to_discard)
            result["card_id"] = special_card_to_discard.id
            
        return result

    def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Not enough players to start the game!")
        self.deck.initialize_deck()
        #deal 3 cards to each player
        for player in self.players:
            for _ in range(3):
                self.draw_card_for_player(player)
        #game starts

    def next_player(self):
        self.index_of_current_player = (self.index_of_current_player + 1) % self.players_number
        return self.player_order[self.current_player_index]
    
    




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
