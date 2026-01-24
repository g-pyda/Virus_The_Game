/**
 * WebSocket message handler for the Host (HostConsumer)
 * Processes messages from the backend and updates the HTML display accordingly
 */

export default function handleWebsocketMessages(event) {
  let msg;
  try {
    msg = JSON.parse(event.data);
    console.log(msg);
  } catch (err) {
    console.error("HOST WS: invalid JSON", event.data);
    return;
  }

  // Only process messages from "internal" sender
  if (msg.sender !== "internal") {
    console.warn("HOST WS: ignoring message from sender:", msg.sender);
    return;
  }

  const header = msg.header;
  const data = msg.data || {};

  console.log("HOST WS received:", header, data);

  switch (header) {
    case "player_join":
      handlePlayerJoin(data);
      break;

    case "player_leave":
      handlePlayerLeave(data);
      break;

    case "organ_add":
      handleOrganAdd(data);
      break;

    case "organ_change":
      handleOrganChange(data);
      break;

    case "organ_delete":
      handleOrganDelete(data);
      break;

    case "state_change":
      handleStateChange(data);
      break;

    case "turn_end":
      handleTurnEnd(data);
      break;

    default:
      console.log("HOST WS: unknown header:", header);
      break;
  }

  // Also broadcast as custom event for modular listeners
  window.dispatchEvent(new CustomEvent(`ws:${header}`, { detail: data }));
}

/**
 * Handles player joining the game
 * Dynamically creates a new player card with organ layers matching the HTML structure
 */
function handlePlayerJoin(data) {
  console.log("handlePlayerJoin received data:", data);
  
  const player_id = data.player_id;
  const nickname = data.nickname;

  console.log(`Creating card for player ${player_id}: "${nickname}"`);

  // Check if player already exists
  let playerCard = document.getElementById(`player-card-${player_id}`);
  if (playerCard) {
    console.log("Player already exists:", player_id);
    return;
  }

  // Define organ structure with all graphics layers
  const organs = [
    { name: "brain", folder: "brain" },
    { name: "heart", folder: "heart" },
    { name: "stomach", folder: "stomach" },
    { name: "bone", folder: "bone" },
    { name: "uterus", folder: "uterus" }
  ];

  // Create player card
  playerCard = document.createElement("div");
  playerCard.id = `player-card-${player_id}`;
  playerCard.className = "player-card";
  playerCard.dataset.playerId = player_id;

  // Create header
  const header = document.createElement("div");
  header.className = "player-header";
  header.textContent = escapeHtml(nickname);

  // Create player body with organ layers
  const playerBody = document.createElement("div");
  playerBody.className = "player-body";
  playerBody.id = `player-body-${player_id}`;

  // Add organ layers for each organ
  organs.forEach(organ => {
    // Cover layer (initial healthy state)
    const coverLayer = document.createElement("div");
    coverLayer.className = "organ-layer active";
    coverLayer.style.backgroundImage = `url('/gameplay_laptop/graphics/${organ.folder}/Player_body_${organ.name}_cover.png')`;
    playerBody.appendChild(coverLayer);

    // Virus layers (blue, rainbow)
    const virusBlue = document.createElement("div");
    virusBlue.className = "organ-layer inactive";
    virusBlue.style.backgroundImage = `url('/gameplay_laptop/graphics/${organ.folder}/Virus_${organ.name}_blue.png')`;
    playerBody.appendChild(virusBlue);

    const virusRainbow = document.createElement("div");
    virusRainbow.className = "organ-layer inactive";
    virusRainbow.style.backgroundImage = `url('/gameplay_laptop/graphics/${organ.folder}/Virus_${organ.name}_rainbow.png')`;
    playerBody.appendChild(virusRainbow);

    // Medicine layers
    const medicineBlue = document.createElement("div");
    medicineBlue.className = "organ-layer inactive";
    medicineBlue.style.backgroundImage = `url('/gameplay_laptop/graphics/${organ.folder}/Medicine_${organ.name}_blue.png')`;
    playerBody.appendChild(medicineBlue);

    const medicineRainbow = document.createElement("div");
    medicineRainbow.className = "organ-layer inactive";
    medicineRainbow.style.backgroundImage = `url('/gameplay_laptop/graphics/${organ.folder}/Medicine_${organ.name}_rainbow.png')`;
    playerBody.appendChild(medicineRainbow);

    // Immune layer
    const immune = document.createElement("div");
    immune.className = "organ-layer inactive";
    immune.style.backgroundImage = `url('/gameplay_laptop/graphics/${organ.folder}/Immune_${organ.name}.png')`;
    playerBody.appendChild(immune);
  });

  // Create footer with card count
  const footer = document.createElement("div");
  footer.className = "player-footer";
  const cardIcon = document.createElement("div");
  cardIcon.className = "card-icon";
  const cardCount = document.createElement("div");
  cardCount.className = "card-count";
  cardCount.id = `cards-${player_id}`;
  cardCount.textContent = "0";
  cardIcon.appendChild(cardCount);
  footer.appendChild(cardIcon);

  playerCard.appendChild(header);
  playerCard.appendChild(playerBody);
  playerCard.appendChild(footer);

  // Add to players area
  const playersArea = document.querySelector(".players-area");
  if (playersArea) {
    playersArea.appendChild(playerCard);
    console.log(`Successfully added player card for ${player_id} to players-area`);
  } else {
    console.warn("players-area container not found");
  }

  console.log("Player joined:", nickname, player_id);
}

/**
 * Handles player leaving the game
 * Removes the player card from the display
 */
function handlePlayerLeave(data) {
  const player_id = data.player_id;

  const playerCard = document.getElementById(`player-card-${player_id}`);
  if (playerCard) {
    playerCard.remove();
    console.log("Player left:", player_id);
  }
}

/**
 * Handles adding an organ (stack) to a player
 * In the current HTML structure, organs are pre-created as layers
 * This function can log the addition or be used for game logic
 */
function handleOrganAdd(data) {
  const target_id = data.target_id;
  const organ_id = data.organ_id;
  const color = data.color;

  console.log("Organ added:", target_id, organ_id, color);
  // Organs are pre-rendered as layers in the player body
  // Status is controlled through organ-change events
}

/**
 * Maps organ ID to organ name and layer index
 * Organs: brain (0-5), heart (6-11), stomach (12-17), bone (18-23), uterus (24-29)
 */
function getOrganLayerIndex(organ_id, layer_type) {
  const organs = ["brain", "heart", "stomach", "bone", "uterus"];
  const organ_index = organ_id - 1; // organ_id is 1-based
  const organ_name = organs[organ_index];

  const base_index = organ_index * 6;
  
  // Layer mapping: 0=cover, 1=virus_blue, 2=virus_rainbow, 3=medicine_blue, 4=medicine_rainbow, 5=immune
  const layer_map = {
    "healthy": 0,
    "infected": 1,
    "vaccinated": 3,
    "cured": 5
  };

  return { name: organ_name, index: base_index + (layer_map[layer_type] || 0) };
}

/**
 * Handles changing an organ's status
 * Toggles visibility of organ layers based on status (healthy, infected, vaccinated, cured)
 */
function handleOrganChange(data) {
  const target_id = data.target_id;
  const organ_id = data.organ_id;
  const status = data.status;

  const playerBody = document.getElementById(`player-body-${target_id}`);
  if (!playerBody) {
    console.warn("Player body not found for:", target_id);
    return;
  }

  const organ_info = getOrganLayerIndex(organ_id, status);
  const layers = playerBody.querySelectorAll(".organ-layer");

  // Hide all layers first
  layers.forEach(layer => layer.classList.remove("active"));
  
  // Activate the correct layer for this status
  if (organ_info.index < layers.length) {
    layers[organ_info.index].classList.add("active");
  }

  console.log("Organ changed:", target_id, organ_id, status);
}

/**
 * Handles removing an organ from display
 * Resets the organ back to healthy state (hides all layers except cover)
 */
function handleOrganDelete(data) {
  const target_id = data.target_id;
  const organ_id = data.organ_id;

  const playerBody = document.getElementById(`player-body-${target_id}`);
  if (!playerBody) {
    console.warn("Player body not found for:", target_id);
    return;
  }

  // Reset organ to healthy state by showing only the cover layer
  const organ_info = getOrganLayerIndex(organ_id, "healthy");
  const layers = playerBody.querySelectorAll(".organ-layer");

  // Hide all layers for this organ first
  const organ_index = organ_id - 1;
  const base_index = organ_index * 6;
  for (let i = 0; i < 6; i++) {
    if (base_index + i < layers.length) {
      layers[base_index + i].classList.remove("active");
    }
  }

  // Show only the cover layer (healthy state)
  if (base_index < layers.length) {
    layers[base_index].classList.add("active");
  }

  console.log("Organ deleted (reset to healthy):", target_id, organ_id);
}

/**
 * Handles game state changes
 * Updates round counter, draw/rejected counts, player statuses, and turn indicators
 */
function handleStateChange(data) {
  console.log("handleStateChange received:", data);
  
  // Update game info display (in the top-bar)
  if (data.round !== undefined) {
    const roundText = document.getElementById("roundText");
    if (roundText) {
      roundText.textContent = `Round ${data.round}`;
    }
  }

  if (data.draw !== undefined) {
    const drawCount = document.getElementById("drawCount");
    if (drawCount) {
      drawCount.textContent = data.draw;
    }
  }

  if (data.rejected !== undefined) {
    const rejectedCount = document.getElementById("rejectedCount");
    if (rejectedCount) {
      rejectedCount.textContent = data.rejected;
    }
  }

  // Update player count display
  if (Array.isArray(data.players) && data.players.length > 0) {
    const playerText = document.getElementById("playerText");
    if (playerText) {
      playerText.textContent = `Players: ${data.players.length}`;
    }

    // Update individual player card counts
    data.players.forEach((playerState) => {
      const player_id = playerState.id;
      const cards_nr = playerState.cards_nr;

      console.log(`Updating cards for player ${player_id}: ${cards_nr}`);

      // Update card count in player card
      const cardCountElement = document.getElementById(`cards-${player_id}`);
      if (cardCountElement) {
        cardCountElement.textContent = cards_nr;
        console.log(`Successfully updated cards-${player_id} to ${cards_nr}`);
      } else {
        console.warn(`Card count element not found: cards-${player_id}`);
      }
    });
  }

  console.log("Game state updated:", data);
}

/**
 * Handles end of turn message
 * Can trigger animations or updates if needed
 */
function handleTurnEnd(data) {
  // Fade all turn indicators
  const allTurnIndicators = document.querySelectorAll(".turn-indicator.active-turn");
  allTurnIndicators.forEach((indicator) => {
    indicator.classList.remove("active-turn");
    indicator.classList.add("hidden");
  });

  console.log("Turn ended");
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
 * Send a message to the WebSocket server
 * Use this function to send messages from frontend to backend
 */
export function sendWebsocketMessage(header, data = {}) {
  const socket = window.hostSocket;

  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket not connected");
    alert("WebSocket connection lost. Please refresh the page.");
    return;
  }

  const message = {
    sender: "frontend",
    header,
    data
  };

  socket.send(JSON.stringify(message));
  console.log("HOST WS sent:", header, data);
}

/**
 * Initialize the host page
 * Sets game ID from URL and prepares the game display
 */
export function initializeHostPage() {
  // Extract game ID from URL (format: /game/<game_id>/)
  const pathMatch = window.location.pathname.match(/\/game\/(\d+)/);
  const gameId = pathMatch ? pathMatch[1] : "Unknown";
  
  // Update game ID display
  const gameIdText = document.getElementById("gameIDText");
  if (gameIdText) {
    gameIdText.textContent = `Game ID ${gameId}`;
  }
  
  console.log("Host page initialized for game:", gameId);
}
