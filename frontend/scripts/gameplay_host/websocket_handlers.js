export default function handleWebsocketMessages(e) {
  let msg;
  try {
    msg = JSON.parse(e.data);
  } catch (err) {
    console.error("WS: invalid JSON", e.data);
    return;
  }

  // Host frontend should receive sender="internal"
  if (msg.sender !== "internal") return;

  const header = msg.header;
  const data = msg.data || {};

  // For now: broadcast to the rest of your UI as DOM events
  // You can listen with: window.addEventListener("ws:state_change", (ev)=>{...})
  window.dispatchEvent(new CustomEvent(`ws:${header}`, { detail: data }));

  // Debug logging (you can keep it)
  console.log("HOST WS:", header, data);
}
