# WEBSOCKET COMMUNICATION SCHEME

## PlayerConsumer

This consumer is created when the player enters the game and works on their side.
Its role is to fetch the data from the frontend (cards chosen, end of the round etc.)
and broadcast them to the HostConsumer. 

### Received format

```json
{
    "sender": "sender_name",
    "data": {something}
}
```

#### From ```frontend``` sender:

- playing a card - each of the fields is specific to the card usecase
```json
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
"data": {
    "action": "end_turn",
}
```

#### From ```lobby``` sender:

- previous card action status
```json
"data": {
    "status" : True,
    "message" : "empty or error message"
}
```

- hand state - defines the state of the player's hand
(sent after every turn ot every player separately)
```json
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
"data": {
    "turn" : True
}
```

### Sent format

Here player id IN STRING is used as sender

```json
{
    "sender": "1",
    "data": {something}
}
```

#### To ```lobby``` receiver:

- successfull connection, adding the player to the game engine in the host
```json
"data": {
    "action": "add",
}
```

- playing a card - each of the fields is specific to the card usecase
```json
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
"data": {
    "action": "end_turn",
}
```

#### To ```frontend``` receiver:

- outcome of the operation
```json
"data": {
    "status" : True,
    "message" : "empty or error message"
}
```

## HostConsumer

This consumer is created when the lobby opens on the host side and is ready for player's actions.
Its role is to fetch the data from the players via websockets, apply them on the game logic and broadcast them to all players. 

### Received format

```json
{
    "sender": "sender_name",
    "data": {something}
}
```

#### From ```{player_id}``` sender:

- successfull connection, adding the player to the game engine in the host
```json
"data": {
    "action": "add",
}
```

- playing a card - each of the fields is specific to the card usecase
```json
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
"data": {
    "action": "end_turn",
}
```

### Sent format

```json
{
    "sender": "lobby",
    "data": {something}
}
```

#### To ```{player_id}``` receiver:

- previous card action status
```json
"data": {
    "status" : True,
    "message" : "empty or error message"
}
```

- hand state - defines the state of the player's hand
(sent after every turn ot every player separately)
```json
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
"data": {
    "turn" : True
}
```