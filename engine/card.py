colors = ["red", "green", "blue", "yellow", "rainbow"]
status = ["sick", "vaccinated", "immune", "dead"]

#when a player decides to put out their organ, we initialize a stack for this color -> cant initialize stacks with same color + control whether the card is immune or the organ died

class Card:

    def __innit__(self, color, value):
        self.color = color
        self.value = value
        #where for value: 1 is vaccine, -1 is virus, 0 is an organ

class Stack:
    #stack for a card (to add viruses or vaccines)
    # value 2 = immune, -2 = dead, 1 = vaccinated, -1 = sick
    stack_value = 0
    status = ""
    def __innit__(self, Card):
        if(Card.value != 0):
            raise TypeError("Your first card of the color has to be an organ!") 
        else:
            self.color = Card.color
            self.add_card(Card)

    def add_card(self, Card):
        if(self.color != Card.color):
            raise TypeError("Wrong color!") 
        if(self.status == "immune"):
            raise ValueError("Card is immune. Nothing left to do.") 
        else:
            self.stack_value += Card.value
        self.set_status()

    def set_status(self):
        match stack_value:
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
    pass


