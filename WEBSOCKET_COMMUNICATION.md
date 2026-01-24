# WEBSOCKET COMMUNICATION SCHEME

## PlayerConsumer

This consumer is created when the player enters the game and works on their side.
Its role is to fetch the data from the frontend (cards chosen, end of the round etc.)
and broadcast them to the HostConsumer. 

### Received format

```json
{
    "sender": "sender_name",
    "header": "operation type",
    "data": {something}
}
```

#### From ```frontend``` sender:

- playing a card - each of the fields is specific to the card usecase
```json
"header" : "card_play",
"data": {
    "action": "string",
    "card_id" : 1,
    "target_id" : 1,
    "target_stack" : 1,
    "player_stack" : 1,
    "target_stacks" : [1, 2, 3],
    "player_stacks" : [1, 2, 3],
    "target_players" : [1, 2, 3],
    "virus_cards" : [1, 2, 3]
}
```

- ending the turn
```json
"header" : "turn_end",
"data": {
    "action": "end_turn",
}
```

#### From ```lobby``` sender:

- previous card action status
```json
"header" : "attempt",
"data": {
    "status" : True,
    "message" : "empty or error message"
}
```

- hand state - defines the state of the player's hand
(sent after every turn ot every player separately)
```json
"header" : "hand_state",
"data": {
    "cards" : [{
        "card_id" : 1,
        "color" : "blue",
        "value" : 0,
        "card_type" : "empty or special card type",
            },
            {...}]
}
```

- player stacks state - defines the state of the player's stacks (organs visible on the lobby in the host) - required for some cards
```json
"header" : "stacks_state",
"data": {
    "stacks" : [{
        "stack_id" : 1,
        "color" : "blue",
        "value" : 0,
            }, {...}]
}
```

- others' stacks state - defines the state of the opponents' stacks (organs visible on the lobby in the host) - required for some cards
```json
"header" : "others_state",
"data": {
    "players" : [
        "player_id" : 1,
        "player_name" : "Johny",
        "stacks" : [{
            "card_id" : 1,
            "color" : "blue",
            "value" : 0,
                }, {...}]
    ]
}
```

- turn state - defines if it is player's move or not
```json
"header" : "turn_state",
"data": {
    "turn" : True
}
```

- ending the game
```json
"header" : "game_end",
"data": {
    "winner_name": "Winnie",
}
```

### Sent format

Here player id IN STRING is used as sender

```json
{
    "sender": "1",
    "header": "operation type",
    "data": {something}
}
```

#### To ```lobby``` receiver:

- successfull connection, adding the player to the game engine in the host
```json
"header" : "connection",
"data": {
    "action": "add",
}
```

- opponents' stacks state request
```json
"header" : "all_stacks",
"data" : {}
```

- playing a card - each of the fields is specific to the card usecase
```json
"header" : "card_play",
"data": {
    "action": "string",
    "card_id" : 1,
    "target_id" : 1,
    "target_stack" : 1,
    "player_stack" : 1,
    "target_stacks" : [1, 2, 3],
    "player_stacks" : [1, 2, 3],
    "target_players" : [1, 2, 3],
    "virus_cards" : [1, 2, 3]
}
```

- ending the turn
```json
"header" : "turn_end",
"data": {
    "action": "end_turn",
}
```


## HostConsumer

This consumer is created when the lobby opens on the host side and is ready for player's actions.
Its role is to fetch the data from the players via websockets, apply them on the game logic and broadcast them to all players. 

### Received format

```json
{
    "sender": "sender_name",
    "header": "operation type",
    "data": {something}
}
```

#### From ```{player_id}``` sender:

- successfull connection, adding the player to the game engine in the host
```json
"header" : "connection",
"data": {
    "action": "add",
}
```

- opponents' stacks state request
```json
"header" : "all_stacks",
"data" : {}
```

- playing a card - each of the fields is specific to the card usecase
```json
"header" : "card_play",
"data": {
    "action": "string",
    "card_id" : 1,
    "target_id" : 1,
    "target_stack" : 1,
    "player_stack" : 1,
    "target_stacks" : [1, 2, 3],
    "player_stacks" : [1, 2, 3],
    "target_players" : [1, 2, 3],
    "virus_cards" : [1, 2, 3]
}
```

- ending the turn
```json
"header" : "turn_end",
"data": {
    "action": "end_turn",
}
```

### Sent format

```json
{
    "sender": "lobby",
    "header": "operation type",
    "data": {something}
}
```

#### To ```{player_id}``` receiver:

- previous card action status
```json
"header" : "attempt",
"data": {
    "status" : True,
    "message" : "empty or error message"
}
```

- hand state - defines the state of the player's hand
(sent after every turn ot every player separately)
```json
"header" : "hand_state",
"data": {
    "cards" : [{
        "card_id" : 1,
        "color" : "blue",
        "value" : 0,
        "card_type" : "empty or special card type",
            },
            {...}]
}
```

- player stacks state - defines the state of the player's stacks (organs visible on the lobby in the host) - required for some cards
```json
"header" : "stacks_state",
"data": {
    "stacks" : [{
        "stack_id" : 1,
        "color" : "blue",
        "value" : 0,
            }, {...}]
}
```

- others' stacks state - defines the state of the opponents' stacks (organs visible on the lobby in the host) - required for some cards
```json
"header" : "others_state",
"data": {
    "players" : [
        "player_id" : 1,
        "player_name" : "Johny",
        "stacks" : [{
            "card_id" : 1,
            "color" : "blue",
            "value" : 0,
                }, {...}]
    ]
}
```

- turn state - defines if it is player's move or not
```json
"header" : "turn_state",
"data": {
    "turn" : True
}
```

- ending the game
```json
"header" : "game_end",
"data": {
    "winner_name": "Winnie",
}
```

## Frontend - HostConsumer

This part is dedicated to determine frontend - host communication.

### Received format

```json
{
    "sender": "internal",
    "header": "operation type",
    "data": {something}
}
```

- add a player - after the player is added to the lobby, they have to be displayed
```json
"header" : "player_join",
"data": {
    "player_id": 12,
    "nickname": "Jack",
}
```

- delete a player - after the player leaves the lobby, they have to be deleted
```json
"header" : "player_leave",
"data": {
    "player_id": 12,
}
```

- add organ to display
```json
"header" : "organ_add",
"data": {
    "target_id": 12,
    "organ_id": 1,
    "color": "blue"
}
```

- change of organ display
```json
"header" : "organ_change",
"data": {
    "action": "string",
    "target_id": 12,
    "organ_id": 1,
    "status": "healthy",
    "color": "blue"
}
```

- delete organ from display
```json
"header" : "organ_delete",
"data": {
    "target_id": 12,
    "organ_id": 1,
}
```

- update of game state
```json
"header" : "state_change",
"data": {
    "round": 5,
    "draw": 31,
    "rejected": 15,
    "players" : [
        {
            "id": 2
            "cards_nr": 2,
            "turn": False
        }, {
            "id": 3,
            "cards_nr": 3,
            "turn": True
        }...
    ]
}
```

- ending the turn
```json
"header" : "turn_end",
"data": {}
```


### Sent format

```json
{
    "sender": "frontend",
    "header": "operation type",
    "data": {something}
}
```

- starting the game
```json
"header" : "game_start",
"data": {}
```


## Frontend - PlayerConsumer

This part is dedicated to determine frontend - player communication.

### Received format

```json
{
    "sender": "internal",
    "header": "operation type",
    "data": {something}
}
```

- attempt validation - checks if operation was successfull
```json
"header" : "attempt",
"data": {
    "status": True,
    "message": "empty or error message"
}
```

- hand state - defines the state of the player's hand
(sent after every turn ot every player separately)
```json
"header" : "hand_state",
"data": {
    "cards" : [{
        "card_id" : 1,
        "color" : "blue",
        "value" : 0,
        "card_type" : "empty or special card type",
            },
            {...}]
}
```

- player stacks state - defines the state of the player's stacks (organs visible on the lobby in the host) - required for some cards
```json
"header" : "stacks_state",
"data": {
    "stacks" : [{
        "stack_id" : 1,
        "color" : "blue",
        "value" : 0,
            }, {...}]
}
```

- others' stacks state - defines the state of the opponents' stacks (organs visible on the lobby in the host) - required for some cards
```json
"header" : "others_state",
"data": {
    "players" : [
        "player_id" : 1,
        "player_name" : "Johny",
        "stacks" : [{
            "card_id" : 1,
            "color" : "blue",
            "value" : 0,
                }, {...}]
    ]
}
```

- turn state - defines if it is player's move or not
```json
"header" : "turn_state",
"data": {
    "turn" : True
}
```

- ending the game
```json
"header" : "game_end",
"data": {
    "winner_name": "Winnie"
}
```


### Sent format

```json
{
    "sender": "frontend",
    "header": "operation type",
    "data": {something}
}
```

- playing a card - each of the fields is specific to the card usecase
```json
"header" : "card_play",
"data": {
    "action": "string",
    "card_id" : 1,
    "target_id" : 1,
    "target_stack" : 1,
    "player_stack" : 1,
    "target_stacks" : [1, 2, 3],
    "player_stacks" : [1, 2, 3],
    "target_players" : [1, 2, 3],
    "virus_cards" : [1, 2, 3]
}
```

- ending the turn
```json
"header" : "turn_end",
"data": {
    "action": "end_turn",
}
```