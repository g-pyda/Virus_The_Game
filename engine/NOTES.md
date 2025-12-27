# Notes - engine (documentation blueprint)

## Cards:

WHAT IF CARDS WERE DICTIONARY NOT DATACLASS? - not sure about it, please consider it

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

## NEXT STEPS


1) function to initialize deck with proper amount of each type of card (currently we're ignoring the rainbow cards so that also needs to be solved but I don't think it's a priority)
2) game instance should be done (starting, adding players, initializing deck, dealing cards)
3) turn implementation + move attempt validation
4) special cards need to be implemented

there also missing part that need to be implemented, they are marked with the key word TOBEDONE 