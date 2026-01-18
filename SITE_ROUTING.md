# SITE ROUTING

## / or /home/

Allows the choice, whether we want to join the game or host it.

## /game/{game-id}/

The game host is initialized, its game id is displayed and players are able to join.

## /game/join/

The player inserts game id and their nickname, these are sent to the backend for verification and, if successful, player joins specific ```/game/{game-id}/{player-id}```.

## /game/{game-id}/{player-id}

The player is initialized. whole game logic is performed here.