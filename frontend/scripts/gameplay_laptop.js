const game_id = localStorage.getItem('game_id');

let room = toString(game_id);
let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let socketUrl = `${ws_scheme}://${window.location.host}/ws/game/${room}/host/`;
let socket = new WebSocket(socketUrl);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Message from server: ', data);
    if (data.type === 'chat') {
        let messagesDiv = document.getElementById('mother-messages');
        let messageElem = document.createElement('div');
        messageElem.textContent = data.message;
        messagesDiv.appendChild(messageElem);
    }
};

let form = document.getElementById('mother-form');
form.onsubmit = function(e) {
    e.preventDefault();
    let input = document.getElementById('mother-input');
    let message = input.value;
    motherSocket.send(JSON.stringify({
        'message': message
    }));
    input.value = '';
};
