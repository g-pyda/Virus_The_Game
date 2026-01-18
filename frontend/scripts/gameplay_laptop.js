import handleWebsocketMessages from './gameplay_host/websocket_handlers.js';

const game_id = localStorage.getItem('game_id');

let room = toString(game_id);
let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let socketUrl = `${ws_scheme}://${window.location.host}/ws/game/${room}/host/`;
let socket = new WebSocket(socketUrl);

socket.onmessage = handleWebsocketMessages;




