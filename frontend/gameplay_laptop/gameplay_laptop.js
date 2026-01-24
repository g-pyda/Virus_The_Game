import handleWebsocketMessages, { initializeHostPage } from '/scripts/gameplay_host/websocket_handlers.js';
import { handleStartButton, handleNewGameButton } from '/scripts/gameplay_host/button_handlers.js';

const game_id = localStorage.getItem('game_id');
const room = String(game_id);

const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const socketUrl = `${ws_scheme}://${window.location.host}/ws/game/${room}/host/`;

const socket = new WebSocket(socketUrl);

// expose globally so button handlers can use it
window.hostSocket = socket;

// messages from backend
socket.onmessage = handleWebsocketMessages;

// optional debug
socket.onopen = () => console.log("HOST WS connected:", socketUrl);
socket.onerror = (e) => console.error("HOST WS error:", e);
socket.onclose = () => console.log("HOST WS closed");

// bind buttons and initialize page after DOM is ready
window.addEventListener("DOMContentLoaded", () => {
  // Initialize game ID display
  initializeHostPage();
  
  const startBtn = document.getElementById("startGameBtn");
  if (startBtn) startBtn.addEventListener("click", handleStartButton);

  const newBtn = document.getElementById("newGameBtn");
  if (newBtn) newBtn.addEventListener("click", handleNewGameButton);
});
