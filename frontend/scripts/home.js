import { sendRequest } from "./common/api_handlers.js";

const btnHost = document.getElementById('btn_host');
const btnJoin = document.getElementById('btn_join');


btnHost.addEventListener('click', async function() {
    try {
        // to be changed when the api is fixed
        const hostNickname = "placeholder";
        
        if (!hostNickname || hostNickname.trim() === '') {
            alert('Nickname is required!');
            return;
        }

        const response = await sendRequest('POST', '/api/games/', { nickname: hostNickname.trim() });
        const gameId = response.game_id;

        localStorage.setItem('host_id', gameId);
        window.location.href = `/game/${gameId}/`;
    } catch (error) {
        alert('Failed to create game: ' + error.message);
    }
});


btnJoin.addEventListener('click', function() {
    window.location.href = '/game/join/';
});
