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

    case "state_change":
      handleStateChange(data);
      break;

    case "turn_end":
      handleTurnEnd(data);
      break;

    case "game_end":
      handleGameEnd(data);
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
  const organColorsMapping = {
      'brain': ['blue'],
      'heart': ['red'],
      'bone': ['yellow'],
      'stomach': ['green'],
      'uterus': ['blue', 'red', 'yellow', 'green']
  };
  organs.forEach(organ => {
    const availableColors = organColorsMapping[organ.name] || [];

    // cover
    let organHTML = `
        <div class="organ-layer active" 
             id="organ-${organ.name}-cover-${player_id}" 
             style="background-image: url('/gameplay_laptop/graphics/${organ.folder}/Player_body_${organ.name}_cover.png')">
        </div>`;

    // Viruses and meds
    availableColors.forEach(color => {
        organHTML += `
            <div class="organ-layer inactive" 
                 id="organ-${organ.name}-virus-${color}-${player_id}" 
                 style="background-image: url('/gameplay_laptop/graphics/${organ.folder}/Virus_${organ.name}_${color}.png')">
            </div>
            <div class="organ-layer inactive" 
                 id="organ-${organ.name}-medicine-${color}-${player_id}" 
                 style="background-image: url('/gameplay_laptop/graphics/${organ.folder}/Medicine_${organ.name}_${color}.png')">
            </div>`;
    });

    // rainbow
    organHTML += `
        <div class="organ-layer inactive" 
             id="organ-${organ.name}-virus-rainbow-${player_id}" 
             style="background-image: url('/gameplay_laptop/graphics/${organ.folder}/Virus_${organ.name}_rainbow.png')">
        </div>
        <div class="organ-layer inactive" 
             id="organ-${organ.name}-medicine-rainbow-${player_id}" 
             style="background-image: url('/gameplay_laptop/graphics/${organ.folder}/Medicine_${organ.name}_rainbow.png')">
        </div>
        <div class="organ-layer inactive" 
             id="organ-${organ.name}-immune-${player_id}" 
             style="background-image: url('/gameplay_laptop/graphics/${organ.folder}/Immune_${organ.name}.png')">
        </div>`;

    // injection into player body
    playerBody.insertAdjacentHTML('beforeend', organHTML);
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
 * Handles game state changes
 * Updates round counter, draw/rejected counts, player statuses, and turn indicators and stacks
 **/
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

      // Update players organs based on stacks
      if (Array.isArray(playerState.stacks)) {
        // Get player body element for this player
        const playerBody = document.getElementById(`player-body-${player_id}`);
        if (!playerBody) {
          console.warn(`Player body not found for player ${player_id}`);
          return;
        }
        
        const colorToOrganMap = {
          'blue': 'brain',
          'red': 'heart',
          'yellow': 'bone',
          'green': 'stomach',
          'rainbow': 'uterus'
        };
        
        // First, deactivate ALL organ layers for this player (except covers)
        // and activate all covers (assume no organs initially)
        const allLayers = playerBody.querySelectorAll(`[id^="organ-"][id*="-${player_id}"]`);
        allLayers.forEach(layer => {
          if (layer.id.includes("cover")) {
            // Activate all covers initially
            layer.classList.add("active");
            layer.classList.remove("inactive");
          } else {
            // Deactivate all other layers
            layer.classList.remove("active");
            layer.classList.add("inactive");
          }
        });
        
        // Then process each stack and activate appropriate layers
        playerState.stacks.forEach((stack) => {
          const stack_id = stack.stack_id;
          const color = stack.color;
          const value = stack.value;
          const topColor = stack.top_card_color;
          const organName = colorToOrganMap[color];
          
          // Hide cover for this organ since it exists
          hideOrganCover(player_id, organName);

          switch (value) {
            case 0: // healthy
              break;
            case -1: // infected (card)
              // Activate virus layer based on top card color
              const organVirus = playerBody.querySelector(`#organ-${organName}-virus-${topColor}-${player_id}`);
              if (organVirus) {
                organVirus.classList.add("active");
                organVirus.classList.remove("inactive");
                console.log(`Activated virus layer: organ-${organName}-virus-${topColor}-${player_id}`);
              } else {
                console.warn(`Virus layer not found: organ-${organName}-virus-${topColor}-${player_id}`);
              }
              break;
            case 1: // vaccinated (medicine)
              const medicineSelectorId = `organ-${organName}-medicine-${topColor}-${player_id}`;
              console.log(`Looking for medicine layer: ${medicineSelectorId}`);
              const organMedicine = playerBody.querySelector(`#${medicineSelectorId}`);
              if (organMedicine) {
                organMedicine.classList.add("active");
                organMedicine.classList.remove("inactive");
                console.log(`Activated medicine layer: ${medicineSelectorId}`);
              } else {
                console.warn(`Medicine layer not found: ${medicineSelectorId}`);
              }
              break;
            case 2: // immune (medicine)
              const organImmune = playerBody.querySelector(`#organ-${organName}-immune-${player_id}`);
              if (organImmune) {
                organImmune.classList.add("active");
                organImmune.classList.remove("inactive");
              }
              break;
          }
        });
      }
    });
  }

  console.log("Game state updated:", data);
}

function deactivateAllOrganLayers(player_id, organName) {
  const playerBody = document.getElementById(`player-body-${player_id}`);
  if (!playerBody) return;
  const layers = playerBody.querySelectorAll(`[id^="organ-${organName}-"]`);
  layers.forEach(layer => {
    if (layer.id.includes("cover")) return; // skip cover
    layer.classList.remove("active");
    layer.classList.add("inactive");
  });
}

function hideOrganCover(player_id, organName) {
  const playerBody = document.getElementById(`player-body-${player_id}`);
  if (!playerBody) return;
  const cover = playerBody.querySelector(`#organ-${organName}-cover-${player_id}`);
  if (cover) {
    cover.classList.remove("active");
    cover.classList.add("inactive");
  }
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
 * Handles game end - displays winner announcement
 */
function handleGameEnd(data) {
  console.log("[GAME_END] Game ended:", data);
  
  // Create overlay for winner announcement
  const overlay = document.createElement('div');
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100%';
  overlay.style.height = '100%';
  overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
  overlay.style.display = 'flex';
  overlay.style.justifyContent = 'center';
  overlay.style.alignItems = 'center';
  overlay.style.zIndex = '10000';
  
  const winnerBox = document.createElement('div');
  winnerBox.style.backgroundColor = '#6CBF6C';
  winnerBox.style.padding = '50px';
  winnerBox.style.borderRadius = '20px';
  winnerBox.style.border = '5px solid black';
  winnerBox.style.textAlign = 'center';
  
  const title = document.createElement('h1');
  title.textContent = 'Game Over!';
  title.style.fontSize = '72px';
  title.style.marginBottom = '30px';
  title.style.color = 'black';
  title.style.fontWeight = 'bold';
  
  const winnerText = document.createElement('h2');
  winnerText.textContent = `Winner: ${data.winner_name}`;
  winnerText.style.fontSize = '48px';
  winnerText.style.marginBottom = '40px';
  winnerText.style.color = 'black';
  
  const backButton = document.createElement('button');
  backButton.textContent = 'Back to Main';
  backButton.style.fontSize = '32px';
  backButton.style.padding = '15px 40px';
  backButton.style.backgroundColor = 'white';
  backButton.style.color = 'black';
  backButton.style.border = '3px solid black';
  backButton.style.borderRadius = '10px';
  backButton.style.cursor = 'pointer';
  backButton.style.fontWeight = 'bold';
  backButton.onclick = () => {
    window.location.href = '/home/';
  };
  
  winnerBox.appendChild(title);
  winnerBox.appendChild(winnerText);
  winnerBox.appendChild(backButton);
  overlay.appendChild(winnerBox);
  document.body.appendChild(overlay);
  console.log('[GAME_END] Overlay created and appended to body');
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
