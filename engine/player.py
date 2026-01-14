from typing import Optional
from dataclasses import dataclass
from .card import Card, Stack

@dataclass
class Attempt:
    action: str                # "attack", "heal", "organ", "discard", "vaccinate"
    card: Optional['Card'] = None      # Card to play
    target_player_id: Optional[int] = None  # Needed for attack/steal
    target_stack_id: Optional[int] = None    # Which stack to affect
    # target_stack_index: Optional[int] = None  #do stacks have incides?
    discard_cards_ids: Optional[list[int]] = None  # For discard action
    
@dataclass
class SwapThiefAttempt:
    action: str                # "organ swap", "body swap" , "thieft"
    player_id: int
    target_player_id: int
    stack_id: Optional[int] = None
    target_stack_id: Optional[int] = None

@dataclass
class EpidemyAttempt:
    action: str                # "epidemy"
    player_id: int
    virus_cards_ids: list[int]  # List of virus cards to give away 
    player_stacks_ids: list[int]  # List of player stacks to remove virus cards from
    target_stacks_ids: list[int]  # List of target stacks to receive the virus cards
    target_players_ids: list[int]  # List of target players to receive the virus cards
    #virus cards index corresponds to target players index and target stacks index

class Player:
    max_on_hand = 3

    def __init__(self, name: str, id_number: int):
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
                #implement attack which card which player
                return Attempt(
                    action="attack",
                    card=self.get_card_from_hand(attempt_info["card_id"]),
                    target_player_id=attempt_info["target_player_id"],
                    target_stack_id=attempt_info["target_stack_id"],
                )

            case "vaccinate": #add vaccine to a healthy card
                return Attempt(
                    action="vaccinate",
                    card=self.get_card_from_hand(attempt_info["card_id"]),
                    target_stack_id=attempt_info["target_stack_id"],
                )
            
            case "heal": #heal a virus
                return Attempt(
                    action="heal",
                    card=self.get_card_from_hand(attempt_info["card_id"]),
                    target_stack_id=attempt_info["target_stack_id"], 
                )

            case "organ": #put out an organ
                return Attempt(
                    action="organ",
                    card=self.get_card_from_hand(attempt_info["card_id"]),
                )

            case "discard":
                return Attempt(
                    action="discard",
                    discard_cards_ids=attempt_info["discard_cards_ids"],
                )
            
            case "special":
                card_to_play = self.get_card_from_hand(attempt_info["card_id"]) #special card; altrnatively: self.choose_card_from_hand(100)
                
                if card_to_play is None:
                    raise ValueError("No special cards on hand!")
                

                if card_to_play.card_type in ["organ swap", "body swap"]:
                    return SwapThiefAttempt(
                        action=card_to_play.card_type,
                        player_id=self.id,
                        stack_id=attempt_info["stack_id"],
                        target_player_id=attempt_info["target_player_id"],
                        target_stack_id=attempt_info["target_stack_id"],
                    )
                
                elif card_to_play.card_type == "thieft":
                    return SwapThiefAttempt(
                        action="thieft",
                        player_id=self.id,
                        target_player_id=attempt_info["target_player_id"],
                        target_stack_id=attempt_info["target_stack_id"],
                    )

                
                elif card_to_play.card_type == "latex glove":
                    return Attempt(action="special", card=card_to_play)
                
                elif card_to_play.card_type == "epidemy":
                    # player can choose 0 - 4 viruses from their stacks to give them other players - TOBEDONE
                    # they have to choose how many and which ones and to whom to give them (FRONTEND)
                    return EpidemyAttempt(
                        action="epidemy",
                        player_id=self.id,
                        virus_cards_ids=attempt_info["virus_cards_ids"],  #list of virus cards to give away 
                        player_stacks_ids=attempt_info["player_stacks_ids"], #list of player's stacks to remove virus cards from  
                        target_stacks_ids=attempt_info["target_stacks_ids"], #list of target stacks to receive the virus cards 
                        target_players_ids=attempt_info ["target_players_ids"], #list of target players to receive the virus cards 
                    )
                else:
                    raise ValueError("Invalid special card type")
                
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
    
    def get_card_from_hand(self, card_id: int) -> Card:
        return next(c for c in self.on_hand if c.id == card_id)
    
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