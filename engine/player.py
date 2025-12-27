class Player:
    max_on_hand = 3

    def __init__(self, name):
        self.name = name
        self.on_hand = [] #list of cards on hand
        self.laid_out = [] #list of stacks initiated with organ laid on the table
        self.status = 0 #when status changes to 1 the player wins


    def attempt_move(self):
        #information to choose what to do
        action = input("What action do you want to do? (attack/heal/organ/discard)") #later moved to UI
        card_to_play = input("Which card do you want to play? (if needed)") #later moved to UI
        player_to_target = input("Which player do you want to target? (if needed)") #later moved to UI
        stack_to_target = input("Which stack do you want to target? (if needed)") #later moved to UI
        match action:

            case "attack":
                #implement attack which card which player + check if possible
                return Attempt(action="attack", card=card_to_play, target_player=player_to_target, target_stack=stack_to_target)

            case "heal": #add vaccine to a card or heal a virus

                # check on hand with +1 and which one they want to play (if only one on hand - default to it)
                return Attempt(action="heal", card=card_to_play, target_stack=stack_to_target)

            case "organ": #put out an organ

                #check on hand with 0 and which to put out (if only one on hand - default to it)
                return Attempt(action="organ", card=card_to_play)

            case "discard":
                # how many cards you want to discard and which ones
                discard_cards = [] #list of cards to discard
                return Attempt(action="discard", discard_cards=discard_cards)
            case _:
                raise ValueError("Invalid action chosen!")

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

@dataclass
class Attempt:
    action: str                # "attack", "heal", "organ", "discard"
    card: Optional['Card'] = None      # Card to play
    target_player: Optional['Player'] = None  # Needed for attack/steal
    target_stack: Optional['Stack'] = None    # Which stack to affect
    discard_cards: Optional[list['Card']] = None  # For discard action