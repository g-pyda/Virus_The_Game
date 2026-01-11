# GAME ENGINE GUIDELEINES

## Player class

- ```Player``` class is supposed to be connected to the database player instance by id, therefore it has to be provided in constructor (more in Game section)

- ?✅? the data for ```attempt``` will be in dictionary form, create the structure of your choice, the API will adjust -> DICT 

- the attempt actions have to operate on specific cards and stacks, like choosse the specific vaccine in your hand and defining the specific organ to heal, so adjust the functions to do so (maybe add some kind of indexing in the deck?)

- ✅ ```choose_card_from_hand``` - redundant function at this point, but may be left for now -> COMMENTED


## Card class

✅ - add id field of a card - makes it easier in retrieving its characteristics from the game engine 

## Deck class

- ✅ i'd change ```cards``` nad ```discarded_pile``` lists to dictionaries in form cards[id] = card etc., it eases access to the cards data and their identification in player's hand

- ✅ ```reshuffle_cards``` - as dictionary would be used, only the addition of cards would be performed

- ✅ ```draw_card``` - the function shuffles cards (connects card and discarded) and takes the card, with the __random index__

## Game class

- ```add_player``` - it should handle both creating the player and adding it to the list (here change to dictionary players[id] = player too)~~, also should add them to the game players in a database~~
- ```add_player``` - it should take as an input player name and id~~, their's id is retrieved during the creation query from database~~
- ```add_player``` - example workflow ~~(database handles errors in this case)~~:
```
input: name, id

check if player exists in the game dict~~(getting id from the database)
    -> if no, create one (database action)~~

add a player to game ~~(database action)~~

return player's id and name (connection purposes)
```

- ```remove_player``` - it should delete the player based on their id and return their id or None

- ```draw_card_for_player``` - take id as input, return card info
- ```discard_card_from_player``` - take card id and player id as input, return player id and card info
- ✅```discard_card_from_stack``` - am I mistaken or this function is never used? -> YEP, DELETED IT
- ✅ ```check_if_winner``` - better if if it would return bool value -> RETURNS BOOL
- ```resolve_attempt``` - after each successfull attempt, return a dictionary with result info, like player id, target player id, card id etc, leave errors as they are
- ```start_game``` - this should only initialize the game (give out cards etc), do not perform the game loop
- implement ```next_player``` method that changes the current player to the next and returns the id of new current player (very important in game flow!)
 - I suggest to create additional list of player's ids in order of adding to create player queue in the turn
