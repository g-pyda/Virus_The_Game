// Player websocket implementation for the deck page.
// Receives sender="internal" messages and sends sender="frontend" messages.

const game_id = localStorage.getItem("game_id");
const player_id = localStorage.getItem("player_id");

if (!game_id || !player_id) {
  alert("Missing game_id or player_id. Please join the game again.");
}

const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const socketUrl = `${ws_scheme}://${window.location.host}/ws/game/${String(game_id)}/player/${String(player_id)}/`;
const socket = new WebSocket(socketUrl);

window.playerSocket = socket; // helpful for debugging

let lastHandState = []; // we store latest cards so we can map buttons to card_id

socket.onopen = () => console.log("PLAYER WS connected:", socketUrl);
socket.onerror = (e) => console.error("PLAYER WS error:", e);
socket.onclose = () => console.log("PLAYER WS closed");

socket.onmessage = (e) => {
  let msg;
  try {
    msg = JSON.parse(e.data);
  } catch (err) {
    console.error("PLAYER WS: invalid JSON", e.data);
    return;
  }

  if (msg.sender !== "internal") return;

  const header = msg.header;
  const data = msg.data || {};

  console.log("PLAYER WS:", header, data);

  switch (header) {
    case "attempt":
      if (data.status === false) alert(`Action failed: ${data.message}`);
      break;

    case "hand_state":
      lastHandState = Array.isArray(data.cards) ? data.cards : [];
      renderHand(lastHandState);
      break;

    case "stacks_state":
      // your own stacks (organs)
      window.myStacks = data.stacks || [];
      break;

    case "others_state":
      // opponents
      window.others = data.players || [];
      break;

    case "turn_state":
      // enable/disable actions
      setTurn(Boolean(data.turn));
      break;

    case "game_end":
      alert(`Game ended. Winner: ${data.winner_name}`);
      break;

    default:
      // ignore safely
      break;
  }
};

function sendEnvelope(header, data) {
  if (socket.readyState !== WebSocket.OPEN) {
    alert("WebSocket not connected yet.");
    return;
  }
  socket.send(JSON.stringify({
    sender: "frontend",
    header,
    data
  }));
}

function setTurn(isMyTurn) {
  const btns = document.querySelectorAll("button");
  btns.forEach((b) => (b.disabled = !isMyTurn));
}

function renderHand(cards) {
  const container = document.querySelector(".container");
  const continueBtn = document.querySelector(".continue-btn");

  // remove existing card rows
  document.querySelectorAll(".card-row").forEach((row) => row.remove());

  // re-create rows from state
  cards.forEach((c) => {
    const row = document.createElement("div");
    row.className = "card-row";

    const img = document.createElement("img");
    img.src = "cards/card.png";
    img.alt = "Card";
    img.className = "card";

    // show card info as text (simple, works immediately)
    const label = document.createElement("div");
    label.style.marginLeft = "10px";
    label.textContent = `id=${c.card_id} color=${c.color} value=${c.value} type=${c.card_type || ""}`;

    const buttons = document.createElement("div");
    buttons.className = "buttons";

    const playBtn = document.createElement("button");
    playBtn.className = "btn";
    playBtn.textContent = "Play";
    playBtn.onclick = () => playCard(c);

    const discardBtn = document.createElement("button");
    discardBtn.className = "btn";
    discardBtn.textContent = "Discard";
    discardBtn.onclick = () => discardCard(c.card_id);

    buttons.appendChild(playBtn);
    buttons.appendChild(discardBtn);

    row.appendChild(img);
    row.appendChild(label);
    row.appendChild(buttons);

    // insert above continue button
    container.insertBefore(row, continueBtn);
  });
}

// ----- Actions -----

function discardCard(card_id) {
  // Engine expects action="discard" and card_id is OK (translator normalizes to list)
  sendEnvelope("card_play", {
    action: "discard",
    card_id: card_id
  });
}

function playCard(card) {
  // Minimal heuristics:
  // - value 0 => organ
  // - value 1 => vaccinate (needs target_stack)
  // - value -1 => attack (needs target player + target_stack)
  // - special => action "special" (may need parameters)

  if (card.color === "special" || (card.card_type && card.card_type.length > 0)) {
    return playSpecial(card);
  }

  if (card.value === 0) {
    // organ card
    sendEnvelope("card_play", {
      action: "organ",
      card_id: card.card_id
    });
    return;
  }

  if (card.value === 1) {
    const target_stack = prompt("Enter target_stack id to vaccinate/heal:");
    if (!target_stack) return;

    // You can decide heal vs vaccinate by your UI later.
    // For now use vaccinate:
    sendEnvelope("card_play", {
      action: "vaccinate",
      card_id: card.card_id,
      target_stack: Number(target_stack)
    });
    return;
  }

  if (card.value === -1) {
    const target_id = prompt("Enter target player_id to attack:");
    if (!target_id) return;

    const target_stack = prompt("Enter target_stack id to attack:");
    if (!target_stack) return;

    sendEnvelope("card_play", {
      action: "attack",
      card_id: card.card_id,
      target_id: Number(target_id),
      target_stack: Number(target_stack)
    });
    return;
  }

  alert("Unknown card type/value.");
}

function playSpecial(card) {
  // Your backend translator can infer card_type from hand if not provided,
  // but we also pass it if present.

  const card_type = card.card_type || null;

  // For complicated specials we ask via prompt (simple but works).
  // organ swap / body swap => need player_stack, target_id, target_stack
  if (card_type === "organ swap" || card_type === "body swap") {
    const player_stack = prompt("Enter YOUR stack id (player_stack) to swap:");
    if (!player_stack) return;

    const target_id = prompt("Enter target player_id:");
    if (!target_id) return;

    const target_stack = prompt("Enter target stack id (target_stack):");
    if (!target_stack) return;

    sendEnvelope("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: card_type,
      player_stack: Number(player_stack),
      target_id: Number(target_id),
      target_stack: Number(target_stack)
    });
    return;
  }

  // thieft (note spelling in your engine: "thieft")
  if (card_type === "thieft") {
    const target_id = prompt("Enter target player_id:");
    if (!target_id) return;

    const target_stack = prompt("Enter target stack id (target_stack):");
    if (!target_stack) return;

    sendEnvelope("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: "thieft",
      target_id: Number(target_id),
      target_stack: Number(target_stack)
    });
    return;
  }

  // latex glove needs nothing else
  if (card_type === "latex glove") {
    sendEnvelope("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: "latex glove"
    });
    return;
  }

  // epidemy is complex; we do not implement UI here
  if (card_type === "epidemy") {
    alert("Epidemy is not implemented in the simple deck UI yet.");
    return;
  }

  // If card_type is missing, still try sending special with just card_id
  sendEnvelope("card_play", {
    action: "special",
    card_id: card.card_id
  });
}

// Continue button = end turn
const continueBtn = document.querySelector(".continue-btn");
if (continueBtn) {
  continueBtn.onclick = () => {
    sendEnvelope("turn_end", { action: "end_turn" });
  };
}
