from typing import Optional
from dataclasses import dataclass
from engine.card import Card, Stack

@dataclass
class Attempt:
    action: str                # "attack", "heal", "organ", "discard"
    card: Optional['Card'] = None      # Card to play
    target_player: Optional['Player'] = None  # Needed for attack/steal
    target_stack: Optional['Stack'] = None    # Which stack to affect
    discard_cards: Optional[list['Card']] = None  # For discard action

class Player:
    max_on_hand = 3

    def __init__(self, name):
        self.id = id(self)  # unique identifier
        self.name = name
        self.on_hand = [] #list of cards on hand
        self.laid_out = [] #list of stacks initiated with organ laid on the table
        self.status = 0 #when status changes to 1 the player wins


    def attempt_move(self):
        #information to choose what to do
        action = input("What action do you want to do? (attack/heal/organ/discard)") #later moved to UI
        match action:

            case "attack":
                #implement attack which card which player + check if possible
                card_to_play = self.choose_card_from_hand(-1) #virus card
                target_player = None #for now, TOBEDONE
                target_stack = None # for now, , TOBEDONE or its not needed? player can only have one stack per color
                return Attempt(action="attack", card=card_to_play, target_player=target_player, target_stack=target_stack)

            case "heal": #add vaccine to a card or heal a virus

                card_to_play = self.choose_card_from_hand(1) #vaccine card
                return Attempt(action="heal", card=card_to_play)

            case "organ": #put out an organ
                card_to_play = self.choose_card_from_hand(0) #organ card
                return Attempt(action="organ", card=card_to_play)

            case "discard":
                # how many cards you want to discard and which ones - TO BE IMPLEMENTED, TOBEDONE
                discard_cards = [] #list of cards to discard
                return Attempt(action="discard", discard_cards=discard_cards)
            case _:
                raise ValueError("Invalid action chosen!")


    def choose_card_from_hand(self, filter_value: int):
        #filter: 1 = vaccine, -1 = virus, 0 = organ
        filtered_cards = [card for card in self.on_hand if card.value == filter_value]
        if len(filtered_cards) == 0:
            raise ValueError("No cards of the requested type on hand!")
        elif len(filtered_cards) == 1:
            return filtered_cards[0]
        else:
            #later move to UI
            card_choice = input(f"Multiple cards available. Choose one: {filtered_cards}")
            for card in filtered_cards:
                if str(card) == card_choice:
                    return card #return the chosen card but im not sure how to implement it properly TOBEDONE
            raise ValueError("Invalid card choice!")

    #actions on stacks/cards laid out
    def add_card_to_stack(self, stack: Stack, card: Card):
        stack.add_card(card)

        if stack.status == "dead":
            self.laid_out.remove(stack)

    def remove_stack(self, stack: Stack):
        self.laid_out.remove(stack)

    def lay_out_organ(self, card: Card):
        new_stack = Stack(card)
        self.laid_out.append(new_stack)

