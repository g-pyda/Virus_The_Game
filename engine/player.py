from typing import Optional
from dataclasses import dataclass
from card import Card, Stack

@dataclass
class Attempt:
    action: str                # "attack", "heal", "organ", "discard", "vaccinate"
    card: Optional['Card'] = None      # Card to play
    target_player: Optional['Player'] = None  # Needed for attack/steal
    target_stack: Optional['Stack'] = None    # Which stack to affect
    discard_cards: Optional[list['Card']] = None  # For discard action

@dataclass
class SwapThiefAttempt:
    action: str                # "organ swap", "body swap" , "thieft"
    player: 'Player'
    stack: Optional['Stack'] = None
    target_player: 'Player'
    target_stack: Optional['Stack'] = None

@dataclass
class EpidemyAttempt:
    action: str                # "epidemy"
    player: 'Player'
    virus_cards: list['Card']  # List of virus cards to give away 
    player_stacks: list['Stack']  # List of player stacks to remove virus cards from
    target_stacks: list['Stack']  # List of target stacks to receive the virus cards
    target_players: list['Player']  # List of target players to receive the virus cards
    #virus cards index corresponds to target players index and target stacks index

class Player:
    max_on_hand = 3

    def __init__(self, name, id_number):
        self.id = id_number  # unique identifier from database
        self.name = name
        self.on_hand = [] #list of cards on hand
        self.laid_out = [] #list of stacks initiated with organ laid on the table
        self.status = 0 #when status changes to 1 the player wins


    def attempt_move(self, attempt_info: dict): #attempt info will come from frontend
        #information to choose what to do
        action = attempt_info.get("action")
        match action:

            case "attack":
                #implement attack which card which player + check if possible
                card_to_play = attempt_info.get("card_to_play") #virus card; altrnatively: self.choose_card_from_hand(-1)
                target_player = attempt_info.get("target_player")
                target_stack = attempt_info.get("target_stack") 
                return Attempt(action="attack", card=card_to_play, target_player=target_player, target_stack=target_stack)

            case "vaccinate": #add vaccine to a healthy card
                card_to_play = attempt_info.get("card_to_play") #vaccine card; altrnatively: self.choose_card_from_hand(1)
                return Attempt(action="vaccinate", card=card_to_play)
            
            case "heal": #heal a virus
                card_to_play = attempt_info.get("card_to_play") #vaccine card; altrnatively: self.choose_card_from_hand(1)
                return Attempt(action="heal", card=card_to_play)

            case "organ": #put out an organ
                card_to_play = attempt_info.get("card_to_play") #organ card; altrnatively: self.choose_card_from_hand(0)
                return Attempt(action="organ", card=card_to_play)

            case "discard":
                discard_cards = attempt_info.get("discard_cards") #list of cards to discard
                return Attempt(action="discard", discard_cards=discard_cards)
            
            case "special":
                card_to_play = attempt_info.get("card_to_play") #special card; altrnatively: self.choose_card_from_hand(100)
                if card_to_play is None:
                    raise ValueError("No special cards on hand!")
                
                if card_to_play.card_type in ["organ swap", "body swap"]:
                    stack = attempt_info.get("stack") 
                    target_player = attempt_info.get("target_player") 
                    target_stack = attempt_info.get("target_stack") 
                    return SwapThiefAttempt(action=card_to_play.card_type, player=self, stack=stack, target_player=target_player, target_stack=target_stack)
                
                elif card_to_play.card_type == "thieft":
                    target_player = attempt_info.get("target_player") 
                    target_stack = attempt_info.get("target_stack") 
                    return SwapThiefAttempt(action="thieft", player=self, target_player=target_player, target_stack=target_stack)
                
                elif card_to_play.card_type == "latex glove":
                    return Attempt(action="special", card=card_to_play)
                
                elif card_to_play.card_type == "epidemy":
                    # player can choose 0 - 4 viruses from their stacks to give them to other players - TOBEDONE
                    # they have to choose how many and which ones and to whom to give them (FRONTEND)
                    virus_cards = attempt_info.get("virus_cards") #list of virus cards to give away 
                    target_stacks = attempt_info.get("target_stacks") #list of target stacks to receive the virus cards 
                    target_players = attempt_info.get("target_players") #list of target players to receive the virus cards 
                    player_stacks = attempt_info.get("player_stacks") #list of player's stacks to remove virus cards from 
                    return EpidemyAttempt(action="epidemy", player=self, virus_cards=virus_cards, target_stacks=target_stacks, player_stacks=player_stacks, target_players=target_players)
            case _:
                raise ValueError("Invalid action chosen!")

    # ------- probably redundant but left FOR NOW -------

    #def choose_card_from_hand(self, filter_value: int):
    #    #filter: 1 = vaccine, -1 = virus, 0 = organ
    #    filtered_cards = [card for card in self.on_hand if card.value == filter_value]
    #    if len(filtered_cards) == 0:
    #        raise ValueError("No cards of the requested type on hand!")
    #    elif len(filtered_cards) == 1:
    #        return filtered_cards[0]
    #    else:
    #        #for now , TOBEDONE FRONTEND
    #        card_choice = input(f"Multiple cards available. Choose one: {filtered_cards}")
    #        for card in filtered_cards:
    #            if str(card) == card_choice:
    #                return card #return the chosen card but im not sure how to implement it properly TOBEDONE
    #        raise ValueError("Invalid card choice!")

    #actions on stacks/cards laid out
    def add_card_to_stack(self, stack: Stack, card: Card):
        #self.on_hand.remove(card)
        stack.add_card(card)
    # if organ dies, remove the stack, move to discard pile handled in game.py
        if stack.status == "dead":
            self.laid_out.remove(stack)
            return True
        return False
    
    def remove_card_from_stack(self, stack: Stack, card: Card):
        stack.remove_card(card)

    def remove_stack(self, stack: Stack):
        self.laid_out.remove(stack)

    def lay_out_organ(self, card: Card):
        new_stack = Stack(card)
        self.laid_out.append(new_stack)
        self.on_hand.remove(card)
    
    def check_win_condition(self):
        if len(self.laid_out) < 4:
            return False
        for stack in self.laid_out:
            if stack.status not in ["healthy", "immune", "vaccinated"]:
                return False
        self.status = 1
        return True