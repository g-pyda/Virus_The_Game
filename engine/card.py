from dataclasses import dataclass
from game import Game

colors = ["red", "green", "blue", "yellow", "rainbow"]
status = ["healthy", "sick", "vaccinated", "immune", "dead"]

#when a player decides to put out their organ, we initialize a stack for this color -> cant initialize stacks with same color + control whether the card is immune or the organ died

#or maybe card doesnt have to be a class? too late imo (chyba że chcę ci się)
@dataclass
class Card:
    color: str
    value: int #where for value: 1 is vaccine, -1 is virus, 0 is an organ; do we want it to bt an enum?
    id: int #unique identifier for each card

class Stack:
    #stack for a card (to add viruses or vaccines)
    # value 2 = immune, -2 = dead, 1 = vaccinated, -1 = sick

    def __init__(self, Card):
        if(Card.value != 0):
            raise TypeError("Your first card of the color has to be an organ!") 
        else:
            self.cards = []
            self.stack_value = 0
            self.status = "healthy"
            self.color = Card.color
            self.add_card(Card)

    def add_card(self, Card):
        if(self.color != Card.color):
            raise TypeError("Wrong color!") 
        if(self.status == "immune"):
            raise ValueError("Card is immune. Nothing left to do.") 
        else:
            self.stack_value += Card.value
            self.cards.append(Card)
        self.set_status()

    def remove_card(self, Card):
        if(self.color != Card.color):
            raise TypeError("Wrong color!") 

        else:
            self.stack_value -= Card.value
            self.cards.remove(Card)
            self.set_status()

    def set_status(self):
        match self.stack_value:
            case 0:
                self.status = "healthy"
            case 1:
                self.status = "vaccinated"
            case -1:
                self.status = "sick"
            case 2:
                self.status = "immune"
            case -2:
                self.status = "dead"
            case _:
                #self.status = "unknown"
                raise ValueError("There occured a problem while setting the status of the stack!") 

    

class SpecialCard:
    card_types = ["organ swap", "thieft", "body swap", "latex glove", "epidemy"]
    value = 100 #to filter later by that

    def __init__(self, card_type: str):
        if card_type not in self.card_types:
            raise ValueError("Invalid special card type!")
        self.card_type = card_type

    #to implement later; they will do ✨something✨



