class player:
    max_on_hand = 3
    status = 0 #when status changes to 1 the player wins


    def __innit__(self, name):
        self.name = name
        self.on_hand = [] #list of cards on hand
        self.laid_out = [] #list of cards laid on the table

    def move:
        #information to choose what to do
        action = input("What action do you want to do?")
        match action:

            case "attack":
            #implement attack which card which player + check if possible

            case "heal":
            #add vaccine to a card or heal a virus - check on hand with +1 and whats laid_out

            case: "organ":
            #put out an organ : check on hand with 0 and which to put out (if only one on hand - default to it)

            case: "discard":
            # how many cards you want to discard 
        self.draw_card(3 - len(on_hand))

    def draw_card:
        pass
        #does this happen in player or game?