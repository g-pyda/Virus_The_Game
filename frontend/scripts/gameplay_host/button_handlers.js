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