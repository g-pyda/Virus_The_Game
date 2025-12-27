class Player:
    max_on_hand = 3

    def __init__(self, name):
        self.name = name
        self.on_hand = [] #list of cards on hand
        self.laid_out = [] #list of stacks initiated with organ laid on the table
        self.status = 0 #when status changes to 1 the player wins


    def move:
        #information to choose what to do
        action = input("What action do you want to do?") #later moved to UI
        match action:

            case "attack":
            #implement attack which card which player + check if possible

            case "heal":
            #add vaccine to a card or heal a virus - check on hand with +1 and whats laid_out

            case: "organ":
            #put out an organ : check on hand with 0 and which to put out (if only one on hand - default to it)

            case: "discard":
            # how many cards you want to discard 

        self.draw_card(max_on_hand - len(on_hand)) #draw to always have 3 on hand

    def draw_card(self):
        pass
        #does this happen in player or game? -> GAME DRAWS FOR PLAYER

    def add_card_to_stack(self, stack: Stack, card: Card):
        stack.add_card(card)

        if stack.status == "dead":
            self.laid_out.remove(stack)