export function handleStartButton() {
  console.log("Start button clicked");

  if (!window.hostSocket) {
    console.error("hostSocket not found. Make sure gameplay_laptop.js sets window.hostSocket.");
    return;
  }

  if (window.hostSocket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket is not open yet.");
    return;
  }

  // Spec-compliant message to HostConsumer
  window.hostSocket.send(JSON.stringify({
    sender: "frontend",
    header: "game_start",
    data: {}
  }));
}

export function handleDeletePlayerButton(playerId) {
  console.log("Delete player button clicked:", playerId);

  // If you don't have a backend feature for this yet, keep it as a stub.
  // Later you can implement a header like "player_kick" and send it here.
}

export function handleNewGameButton() {
  console.log("New game button clicked");

  // Optional: simplest "new game" behavior is to reload the page
  window.location.reload();
}