# API GUIDELINES

## Required endpoints

Every endpoint is accessible under __api/...__ endpoint, so include them like that in the game urls

__api/games/__:
- ```POST``` - creates the game:
    - validates
    - creates new game in the database (create_game())
    - returns game id (provides game access) or error message

__api/games/{game_id}/__:
- ```POST``` - adds a player based on the name in the request:
    - validates
    - retrieves player id from the database (get_player_id(str))
        - if player doesn't exist (specific error returned), creates one in the database (create_player(str))
    - returns player id or error

- ```DELETE``` - deletes a player from a game based on their id:
    - validates
    - deletes player from game in the database(delete_player_from_game(int, int))
    - returns game id or error

- ```PATCH``` - ends the game:
    - validates
    - finished the game in the database (finish_game(int, int))
    - returns success message or error

__api/players/__:
- ```GET```:
    - validates 
    - returns all players data

## Suggested request structure

### __api/games/{game_id}/__

```
{
    'player_name' : {name},
}
```

## Suggested response structure

### Success message

```
{
    'status' : 'success',
    {some additional info returned, like object id, etc}
}
```


### Error message
```
{
    'status' : 'error',
    'message' : {message}
}
```

## Serializers

### Comment to current:
- __GameCreate__: I don't think if we gonna use names of the games, only ids, so it should be exchanged in game creation

- __GameJoin__: ok, will be used in player addition, deletion and game finish (game id in url)

- __GameState__: redundant for now, but maybe we'll add games history next to the leaderboard, so may be left for now

### Serializers to add:
- __Player__: gives all player data, required to the leaderboard generation, follow the ```Player``` model in ```model.py```