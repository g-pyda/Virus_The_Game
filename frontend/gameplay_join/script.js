import {sendRequest} from "../common/api_handlers"

let form = document.getElementById('player-form');

form.onsubmit = async function(e) {
    e.preventDefault();
    let game_id_input = document.getElementById('game-id-input');
    let nickname_input = document.getElementById('nickname-input');
    let game_id = game_id_input.value;
    let nickname = nickname_input.value;

    const response = await sendRequest("POST", `/api/games/${game_id}/`, { player_name: nickname });
    const player_id = response.player_id;
    
    localStorage.setItem('playerToken', response.token);
    window.location.href = `/game/${game_id}/${player_id}`;
};

