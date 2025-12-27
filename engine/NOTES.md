# Notes - engine (documentation blueprint)

## Cards:

class *Card* - 58 basic cards; dataclass
class *SpecialCard* - 10 special cards, we'll have to implement how the work

class *Stack* - is a stack of basic cards to add viruses and vaccines


## Players:

class *Player* holds players cards on hand and laid out; player acts on their own cards but when the game makes them;
player decides what move (action) they want to attempt but the game verifies if its possible and then it does it (tells involved players what to do)

should the player always decide on which stack they want to act?; which organ to put out?, cause i would do so it happens automatically (they have to choose specific card only if they have two with that action - two viruses they can use, two vaccines)

## Game:

class game holds the deck with the all cards not "owned" by players, it checks if action (attempted by player) is legal and then resolves it

I would provide the players with buttons what they can do, not make them type it out (I think it's obvious but I want highlight that the inputs are temporary)