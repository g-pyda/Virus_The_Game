/**
 * WebSocket message handler for the Player (PlayerConsumer)
 * Processes messages from the backend and updates the player's UI accordingly
 */

export default function handleWebsocketMessages(event) {
  let msg;
  try {
    msg = JSON.parse(event.data);
    console.log(msg);
  } catch (err) {
    console.error("PLAYER WS: invalid JSON", event.data);
    return;
  }

  // Only process messages from "internal" sender
  if (msg.sender !== "internal") {
    console.warn("PLAYER WS: ignoring message from sender:", msg.sender);
    return;
  }

  const header = msg.header;
  const data = msg.data || {};

  console.log("PLAYER WS received:", header, data);

  switch (header) {
    case "attempt":
      handleAttempt(data);
      break;

    case "hand_state":
      handleHandState(data);
      break;

    case "stacks_state":
      handleStacksState(data);
      break;

    case "others_state":
      handleOthersState(data);
      break;

    case "turn_state":
      handleTurnState(data);
      break;

    case "game_end":
      handleGameEnd(data);
      break;

    default:
      console.log("PLAYER WS: unknown header:", header);
      break;
  }

  // Also broadcast as custom event for modular listeners
  window.dispatchEvent(new CustomEvent(`ws:${header}`, { detail: data }));
}

/**
 * Handles action validation response from backend
 * Shows success/error notifications to the player
 */
function handleAttempt(data) {
  const status = data.status;
  const message = data.message || "";

  if (status === true) {
    // Success notification
    showNotification("Action successful!", "success");
    console.log("Action succeeded:", message);
  } else {
    // Error notification
    showNotification(`Action failed: ${message}`, "error");
    console.warn("Action failed:", message);
  }

  // Store attempt status globally for debugging
  window.lastAttemptStatus = { status, message };
}

/**
 * Handles hand state update
 * Renders the player's hand of cards
 */
function handleHandState(data) {
  const cards = Array.isArray(data.cards) ? data.cards : [];

  // Store latest hand state globally for card interactions
  window.lastHandState = cards;

  console.log("Hand state received:", cards);
  renderHand(cards);
}

/**
 * Handles player's own stacks (organs) state
 * Updates the organs displayed on player's side
 */
function handleStacksState(data) {
  const stacks = Array.isArray(data.stacks) ? data.stacks : [];

  // Store player's stacks globally
  window.myStacks = stacks;

  console.log("Player stacks state:", stacks);
  renderPlayerStacks(stacks);
}

/**
 * Handles opponents' stacks state
 * Updates the view of other players' organs
 */
function handleOthersState(data) {
  const players = Array.isArray(data.players) ? data.players : [];

  // Store opponents globally
  window.opponentPlayers = players;

  console.log("Opponents state:", players);
  renderOpponentStacks(players);
}

/**
 * Handles turn state update
 * Enables/disables player actions based on whose turn it is
 */
function handleTurnState(data) {
  const isMyTurn = Boolean(data.turn);

  window.isMyTurn = isMyTurn;

  // Update UI to reflect turn state
  updateTurnIndicator(isMyTurn);
  setActionButtonsEnabled(isMyTurn);

  console.log("Turn state:", isMyTurn ? "My turn" : "Opponent's turn");
}

/**
 * Handles game end message
 * Displays winner and ends game
 */
function handleGameEnd(data) {
  const winner_name = data.winner_name || "Unknown";

  // Show game end modal
  showGameEndModal(winner_name);

  // Disable all actions
  setActionButtonsEnabled(false);

  console.log("Game ended. Winner:", winner_name);
}

/**
 * Renders the player's hand of cards
 * Creates card elements and attaches event listeners
 */
function renderHand(cards) {
  const handContainer = document.getElementById("hand-container") ||
                       document.querySelector(".player-deck") ||
                       document.querySelector(".hand");

  if (!handContainer) {
    console.warn("Hand container not found");
    return;
  }

  // Clear existing cards (except special elements)
  const cardElements = handContainer.querySelectorAll(".card-element");
  cardElements.forEach(el => el.remove());

  // Create card elements
  cards.forEach((card) => {
    const cardElement = createCardElement(card);
    handContainer.appendChild(cardElement);
  });

  console.log("Hand rendered with", cards.length, "cards");
}

/**
 * Creates a single card element with appropriate styling and handlers
 */
function createCardElement(card) {
  const cardDiv = document.createElement("div");
  cardDiv.className = "card-element";
  cardDiv.id = `card-${card.card_id}`;
  cardDiv.dataset.cardId = card.card_id;
  cardDiv.dataset.color = card.color;
  cardDiv.dataset.value = card.value;
  cardDiv.dataset.type = card.card_type || "";

  // Color-coded styling
  cardDiv.style.borderColor = card.color;

  // Card content
  const cardContent = document.createElement("div");
  cardContent.className = "card-content";
  cardContent.innerHTML = `
    <div class="card-value">${card.value}</div>
    <div class="card-color">${escapeHtml(card.color)}</div>
    ${card.card_type ? `<div class="card-type">${escapeHtml(card.card_type)}</div>` : ""}
  `;

  // Button container
  const buttonContainer = document.createElement("div");
  buttonContainer.className = "card-buttons";

  // Play button
  const playBtn = document.createElement("button");
  playBtn.textContent = "Play";
  playBtn.className = "btn btn-play";
  playBtn.onclick = () => handlePlayCard(card);

  // Discard button
  const discardBtn = document.createElement("button");
  discardBtn.textContent = "Discard";
  discardBtn.className = "btn btn-discard";
  discardBtn.onclick = () => handleDiscardCard(card.card_id);

  buttonContainer.appendChild(playBtn);
  buttonContainer.appendChild(discardBtn);

  cardDiv.appendChild(cardContent);
  cardDiv.appendChild(buttonContainer);

  return cardDiv;
}

/**
 * Renders player's own stacks (organs)
 * Displays health status of player's organs
 */
function renderPlayerStacks(stacks) {
  const stacksContainer = document.getElementById("my-stacks-container") ||
                         document.querySelector(".my-stacks") ||
                         document.querySelector(".player-organs");

  if (!stacksContainer) {
    console.warn("Player stacks container not found");
    return;
  }

  // Clear existing stacks
  const stackElements = stacksContainer.querySelectorAll(".stack-element");
  stackElements.forEach(el => el.remove());

  // Create stack elements
  stacks.forEach((stack) => {
    const stackElement = createStackElement(stack, "own");
    stacksContainer.appendChild(stackElement);
  });

  console.log("Player stacks rendered:", stacks.length);
}

/**
 * Renders opponents' stacks (organs)
 * Displays other players and their organs
 */
function renderOpponentStacks(players) {
  const opponentsContainer = document.getElementById("opponents-container") ||
                            document.querySelector(".opponents") ||
                            document.querySelector(".other-players");

  if (!opponentsContainer) {
    console.warn("Opponents container not found");
    return;
  }

  // Clear existing opponents
  const playerElements = opponentsContainer.querySelectorAll(".opponent-player");
  playerElements.forEach(el => el.remove());

  // Create opponent player elements
  players.forEach((player) => {
    const playerElement = createOpponentPlayerElement(player);
    opponentsContainer.appendChild(playerElement);
  });

  console.log("Opponent stacks rendered for", players.length, "players");
}

/**
 * Creates a single stack (organ) element
 */
function createStackElement(stack, type = "own") {
  const stackDiv = document.createElement("div");
  stackDiv.className = `stack-element stack-${type}`;
  stackDiv.id = `stack-${stack.stack_id}`;
  stackDiv.dataset.stackId = stack.stack_id;
  stackDiv.dataset.color = stack.color;
  stackDiv.dataset.value = stack.value;
  stackDiv.dataset.status = stack.status || "healthy";

  // Color-coded border
  stackDiv.style.borderColor = stack.color;

  // Stack content
  stackDiv.innerHTML = `
    <div class="stack-id">#${stack.stack_id}</div>
    <div class="stack-color">${escapeHtml(stack.color)}</div>
    <div class="stack-value">${stack.value}</div>
    <div class="stack-status">${stack.status || "healthy"}</div>
  `;

  // Apply status styling
  updateStackStyling(stackDiv, stack.status || "healthy");

  return stackDiv;
}

/**
 * Creates an opponent player element with their stacks
 */
function createOpponentPlayerElement(player) {
  const playerDiv = document.createElement("div");
  playerDiv.className = "opponent-player";
  playerDiv.id = `opponent-${player.player_id}`;
  playerDiv.dataset.playerId = player.player_id;

  // Player header
  const playerHeader = document.createElement("div");
  playerHeader.className = "opponent-header";
  playerHeader.innerHTML = `
    <h4>${escapeHtml(player.player_name)}</h4>
    <span class="player-id">(ID: ${player.player_id})</span>
  `;

  // Stacks container
  const stacksContainer = document.createElement("div");
  stacksContainer.className = "opponent-stacks";

  const stacks = Array.isArray(player.stacks) ? player.stacks : [];
  stacks.forEach((stack) => {
    const stackElement = createStackElement(stack, "opponent");
    stacksContainer.appendChild(stackElement);
  });

  playerDiv.appendChild(playerHeader);
  playerDiv.appendChild(stacksContainer);

  return playerDiv;
}

/**
 * Applies styling to a stack based on its status
 */
function updateStackStyling(stackElement, status) {
  // Remove previous status classes
  stackElement.classList.remove("healthy", "infected", "vaccinated", "cured");
  stackElement.classList.add(status);

  // Apply background colors based on status
  if (status === "infected") {
    stackElement.style.backgroundColor = "rgba(255, 0, 0, 0.15)";
  } else if (status === "vaccinated") {
    stackElement.style.backgroundColor = "rgba(0, 255, 0, 0.15)";
  } else if (status === "cured") {
    stackElement.style.backgroundColor = "rgba(0, 0, 255, 0.15)";
  } else {
    stackElement.style.backgroundColor = "transparent";
  }
}

/**
 * Updates turn indicator display
 */
function updateTurnIndicator(isMyTurn) {
  const indicator = document.getElementById("turn-indicator") ||
                   document.querySelector(".turn-indicator");

  if (!indicator) {
    console.warn("Turn indicator element not found");
    return;
  }

  if (isMyTurn) {
    indicator.classList.remove("hidden");
    indicator.classList.add("active");
    indicator.textContent = "🔄 Your Turn!";
  } else {
    indicator.classList.add("hidden");
    indicator.classList.remove("active");
    indicator.textContent = "Waiting...";
  }
}

/**
 * Enables/disables all action buttons based on turn state
 */
function setActionButtonsEnabled(enabled) {
  const buttons = document.querySelectorAll(".card-buttons button, .btn-play, .btn-discard, .continue-btn");
  buttons.forEach((btn) => {
    btn.disabled = !enabled;
  });
}

/**
 * Shows a notification toast to the player
 */
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  const container = document.getElementById("notifications") ||
                   document.querySelector(".notifications") ||
                   document.body;

  container.appendChild(notification);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    notification.style.opacity = "0";
    notification.style.transition = "opacity 0.3s";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

/**
 * Shows game end modal
 */
function showGameEndModal(winnerName) {
  const modal = document.createElement("div");
  modal.className = "game-end-modal";
  modal.innerHTML = `
    <div class="modal-content">
      <h2>Game Over</h2>
      <p>Winner: <strong>${escapeHtml(winnerName)}</strong></p>
      <button class="btn btn-primary" onclick="window.location.reload()">Play Again</button>
    </div>
  `;

  document.body.appendChild(modal);
}

/**
 * Handle playing a card
 * Routes to appropriate handler based on card type
 */
function handlePlayCard(card) {
  if (!window.isMyTurn) {
    showNotification("It's not your turn!", "error");
    return;
  }

  console.log("Playing card:", card);

  // Card type detection
  if (card.color === "special" || (card.card_type && card.card_type.length > 0)) {
    handlePlaySpecial(card);
  } else if (card.value === 0) {
    handlePlayOrgan(card);
  } else if (card.value === 1) {
    handlePlayVaccine(card);
  } else if (card.value === -1) {
    handlePlayVirus(card);
  } else {
    showNotification("Unknown card type", "error");
  }
}

/**
 * Handle discarding a card
 */
function handleDiscardCard(card_id) {
  if (!window.isMyTurn) {
    showNotification("It's not your turn!", "error");
    return;
  }

  sendWebsocketMessage("card_play", {
    action: "discard",
    card_id: card_id
  });

  console.log("Card discarded:", card_id);
}

/**
 * Handle playing an organ card
 */
function handlePlayOrgan(card) {
  sendWebsocketMessage("card_play", {
    action: "organ",
    card_id: card.card_id
  });

  showNotification("Organ played", "success");
}

/**
 * Handle playing a vaccine/heal card
 */
function handlePlayVaccine(card) {
  // Prompt for target stack
  const target_stack = prompt("Enter target stack ID to vaccinate/heal:");
  if (!target_stack) return;

  const action = confirm("Vaccinate? (OK) or Heal? (Cancel)") ? "vaccinate" : "heal";

  sendWebsocketMessage("card_play", {
    action: action,
    card_id: card.card_id,
    target_stack: Number(target_stack)
  });

  showNotification(`Card ${action}d`, "success");
}

/**
 * Handle playing a virus card (attack)
 */
function handlePlayVirus(card) {
  const target_id = prompt("Enter target player ID to attack:");
  if (!target_id) return;

  const target_stack = prompt("Enter target stack ID to attack:");
  if (!target_stack) return;

  sendWebsocketMessage("card_play", {
    action: "attack",
    card_id: card.card_id,
    target_id: Number(target_id),
    target_stack: Number(target_stack)
  });

  showNotification("Attack played", "success");
}

/**
 * Handle playing special cards
 */
function handlePlaySpecial(card) {
  const card_type = card.card_type || null;

  // Organ swap / body swap
  if (card_type === "organ swap" || card_type === "body swap") {
    const player_stack = prompt("Enter YOUR stack ID (player_stack) to swap:");
    if (!player_stack) return;

    const target_id = prompt("Enter target player ID:");
    if (!target_id) return;

    const target_stack = prompt("Enter target stack ID (target_stack) to swap:");
    if (!target_stack) return;

    sendWebsocketMessage("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: card_type,
      player_stack: Number(player_stack),
      target_id: Number(target_id),
      target_stack: Number(target_stack)
    });

    showNotification(`${card_type} played`, "success");
    return;
  }

  // Theft
  if (card_type === "thieft" || card_type === "theft") {
    const target_id = prompt("Enter target player ID:");
    if (!target_id) return;

    const target_stack = prompt("Enter target stack ID (target_stack):");
    if (!target_stack) return;

    sendWebsocketMessage("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: card_type,
      target_id: Number(target_id),
      target_stack: Number(target_stack)
    });

    showNotification("Theft played", "success");
    return;
  }

  // Latex glove
  if (card_type === "latex glove") {
    sendWebsocketMessage("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: "latex glove"
    });

    showNotification("Latex glove played", "success");
    return;
  }

  // Epidemy (complex, needs custom UI)
  if (card_type === "epidemy") {
    showNotification("Epidemy UI not yet implemented", "warning");
    return;
  }

  // Fallback: send as generic special
  sendWebsocketMessage("card_play", {
    action: "special",
    card_id: card.card_id,
    card_type: card_type
  });

  showNotification("Special card played", "success");
}

/**
 * Send a message to the WebSocket server
 */
export function sendWebsocketMessage(header, data = {}) {
  const socket = localStorage.playerSocket;

  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket not connected");
    showNotification("Connection lost. Please refresh.", "error");
    return;
  }

  const message = {
    sender: "frontend",
    header,
    data
  };

  socket.send(JSON.stringify(message));
  console.log("PLAYER WS sent:", header, data);
}

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Initialize player websocket handlers
 * Call this after DOM is loaded
 */
export function initializePlayerHandlers() {
  const continueBtn = document.querySelector(".continue-btn") ||
                     document.getElementById("end-turn-btn");

  if (continueBtn) {
    continueBtn.onclick = () => {
      sendWebsocketMessage("turn_end", { action: "end_turn" });
      showNotification("Turn ended", "success");
    };
  }

  console.log("Player handlers initialized");
}
