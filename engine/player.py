class player:
    max_on_hand = 3
    status = 0 #when status changes to 1 the player wins


    def __innit__(self, name):
        self.name = name
        self.on_hand = [] #list of cards on hand
        self.laid_out = [] #list of cards laid on the table
        

        
    