// Player websocket implementation for the deck page.
// Receives sender="internal" messages and sends sender="frontend" messages.

import {
  getCard,
  setCardImage,
  disableAllPlayButtons,
  disableAllDiscardButtons,
  enableContinueButton,
  disableContinueButton,
  enableAllPlayButtons,
  enableAllDiscardButtons
} from '/gameplay_telephone/player_deck/cards_dictionary.js';

const game_id = window.localStorage.getItem("game_id");
const player_id = window.localStorage.getItem("player_id");
const playerName = window.localStorage.getItem("playerName") || `Player ${player_id}`;

if (!game_id || !player_id) {
  alert("Missing game_id or player_id. Please join the game again.");
}

// Clear potentially stale data from localStorage (player-specific keys)
window.localStorage.removeItem(`othersData_${player_id}`);
window.localStorage.removeItem(`myStacksData_${player_id}`);
window.localStorage.removeItem(`pendingAction_${player_id}`);

let title = document.querySelector("title");
if (title) {
  title.textContent = `Virus The Game - ${playerName}`;
}

let h1 = document.querySelector("h1");
if (h1) {
  h1.textContent = `${playerName}`;
}

let windowObjects = [
  window.lastHandState,
  window.discardStarted,
  window.lastCardPlayed,
  window.actionCompleted
]

windowObjects.forEach(obj => {
  if (obj === undefined) {
    obj = null;
  }
});

// Track if successful action (play or discard) has been completed this turn
window.actionCompleted = false;
window.actionPending = false;
window.lastActionType = null; // 'play' or 'discard' or 'refill'
window.cardsDiscardedThisTurn = 0;
window.autoEndingSent = false;
window.autoDrawSent = false;
window.isMyTurn = false;
window.waitingForNewTurn = false;
window.cardRefillInProgress = false;

function handleButtonsState() {
  console.log('handleButtonsState called - actionCompleted:', window.actionCompleted, 'actionPending:', window.actionPending, 'lastActionType:', window.lastActionType);
  
  // Continue button: available after successful action (play or discard)
  if (window.actionCompleted) {
    enableContinueButton();
    console.log('Continue button ENABLED');
  } else {
    disableContinueButton();
    console.log('Continue button DISABLED');
  }
  
  // Play buttons: disabled after any action or if pending
  if (!window.actionCompleted && !window.actionPending) {
    enableAllPlayButtons();
    console.log('Play buttons ENABLED');
  } else {
    disableAllPlayButtons();
    console.log('Play buttons DISABLED');
  }
  
  // Discard buttons:
  // - Enabled if no action pending AND (no action completed OR last action was discard)
  // - Disabled if action pending OR last action was play OR last action was refill
  if (window.actionPending) {
    disableAllDiscardButtons();
    console.log('Discard buttons DISABLED (action pending)');
  } else if (window.actionCompleted && (window.lastActionType === 'play' || window.lastActionType === 'refill')) {
    disableAllDiscardButtons();
    console.log('Discard buttons DISABLED (after play or refill)');
  } else {
    enableAllDiscardButtons();
    console.log('Discard buttons ENABLED');
  }
}

const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const socketUrl = `${ws_scheme}://${window.location.host}/ws/game/${String(game_id)}/player/${String(player_id)}/`;
const socket = new WebSocket(socketUrl);

window.playerSocket = socket;

socket.onopen = () => {
  console.log("PLAYER WS connected:", socketUrl);
  
  // Send connection message with player nickname
  const connectionMessage = {
    sender: "frontend",
    header: "connection",
    data: {
      action: "add_to_lobby",
      nickname: playerName
    }
  };
  socket.send(JSON.stringify(connectionMessage));
  console.log("PLAYER WS: sent connection with nickname:", playerName);
};

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
      if (data.status === false){
        // Action failed - reset pending and re-enable buttons
        window.lastCardPlayed = null;
        window.discardStarted = false;
        window.actionPending = false;
        handleButtonsState();
        alert(`Action failed: ${data.message}`);
      } else {
        // remove played/discarded card from hand
        if (data.message === "connected") break;
        console.log('Action successful! Card played:', window.lastCardPlayed, 'Action type:', window.lastActionType);
        window.actionCompleted = true;
        window.actionPending = false;
        
        if (window.lastActionType === 'discard') {
          window.cardsDiscardedThisTurn++;
        }
        
        handleButtonsState();
        deleteCardById(window.lastCardPlayed);
      }
      break;

    case "hand_state":
      console.log('Received hand_state with', data.cards?.length, 'cards');
      const previousHandSize = window.lastHandState ? window.lastHandState.length : 0;
      window.lastHandState = Array.isArray(data.cards) ? data.cards : [];
      renderHand(window.lastHandState);
      
      // Auto-draw 3 cards if player has no cards and it's their turn
      if (window.isMyTurn && window.lastHandState.length === 0 && !window.autoDrawSent) {
        console.log('No cards left - automatically drawing 3 cards');
        window.autoDrawSent = true;
        window.cardRefillInProgress = true;
        sendEnvelope("draw_cards", { count: 3 });
      } else if (window.cardRefillInProgress && window.lastHandState.length > 0) {
        // Cards were just refilled - treat as completing an action
        console.log('Cards refilled - blocking discards');
        window.actionCompleted = true;
        window.lastActionType = 'refill';
        window.cardRefillInProgress = false;
        handleButtonsState();
      }
      break;

    case "stacks_state":
      // your own stacks (organs)
      window.myStacks = data.stacks || [];
      // Store in localStorage for choosing pages (player-specific)
      window.localStorage.setItem(`myStacksData_${player_id}`, JSON.stringify(window.myStacks));
      break;

    case "others_state":
      // opponents
      window.others = data.players || [];
      console.log("Received others_state. Current player:", player_id, "Others:", window.others);
      console.log("Storing to localStorage - othersData:", JSON.stringify(window.others));
      // Store in localStorage for choosing pages (player-specific)
      window.localStorage.setItem(`othersData_${player_id}`, JSON.stringify(window.others));
      break;

    case "turn_state":
      // Reset action tracking when turn changes
      const wasMyTurn = window.isMyTurn || false;
      const isNowMyTurn = Boolean(data.turn);
      const waitingForNewTurn = window.waitingForNewTurn || false;
      
      console.log('=========================================');
      console.log('[TURN_STATE] Received turn_state');
      console.log('[TURN_STATE] wasMyTurn:', wasMyTurn);
      console.log('[TURN_STATE] isNowMyTurn:', isNowMyTurn);
      console.log('[TURN_STATE] waitingForNewTurn:', waitingForNewTurn);
      console.log('[TURN_STATE] Current action state:', {
        actionCompleted: window.actionCompleted,
        actionPending: window.actionPending,
        lastActionType: window.lastActionType
      });
      
      if (isNowMyTurn && !wasMyTurn) {
        // NEW turn starting (changed from false to true) - reset action flags
        console.log('[TURN_STATE] ✅ NEW TURN - Resetting all action flags');
        window.actionCompleted = false;
        window.actionPending = false;
        window.lastActionType = null;
        window.cardsDiscardedThisTurn = 0;
        window.autoEndingSent = false;
        window.autoDrawSent = false;
        window.waitingForNewTurn = false;
      } else if (!isNowMyTurn) {
        // Turn ending or not our turn - reset flags
        console.log('[TURN_STATE] ❌ TURN ENDING - Resetting all action flags');
        window.actionCompleted = false;
        window.actionPending = false;
        window.lastActionType = null;
        window.cardsDiscardedThisTurn = 0;
        window.autoEndingSent = false;
        window.autoDrawSent = false;
        window.waitingForNewTurn = false;
      } else if (waitingForNewTurn && isNowMyTurn) {
        // Turn came back after auto-skip - reset flags for new turn
        console.log('[TURN_STATE] 🔄 TURN RETURNED AFTER SKIP - Resetting all action flags');
        window.actionCompleted = false;
        window.actionPending = false;
        window.lastActionType = null;
        window.cardsDiscardedThisTurn = 0;
        window.autoEndingSent = false;
        window.autoDrawSent = false;
        window.waitingForNewTurn = false;
      } else {
        // Turn state unchanged (still our turn) - keep action state
        console.log('[TURN_STATE] ⏸️  TURN CONTINUES - Keeping action state');
      }
      
      window.isMyTurn = isNowMyTurn;
      console.log('[TURN_STATE] Final state:', {
        isMyTurn: window.isMyTurn,
        actionCompleted: window.actionCompleted,
        actionPending: window.actionPending,
        lastActionType: window.lastActionType
      });
      console.log('=========================================');
      setTurn(isNowMyTurn);
      break;

    case "game_end":
       console.log('[GAME_END] Received game_end message:', data);
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
        window.location.href = '/';
      };
      
      winnerBox.appendChild(title);
      winnerBox.appendChild(winnerText);
      winnerBox.appendChild(backButton);
      overlay.appendChild(winnerBox);
      document.body.appendChild(overlay);
      console.log('[GAME_END] Overlay created and appended to body');
      break;

    default:
      // ignore safely
      break;
  }
};

function sendEnvelope(header, data) {
  if (socket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket not connected - cannot send message");
    alert("WebSocket not connected yet.");
    return;
  }
  const message = {
    sender: "frontend",
    header,
    data
  };
  console.log('Sending WebSocket message:', header, message);
  socket.send(JSON.stringify(message));
}

function setTurn(isMyTurn) {
  if (!isMyTurn) {
    // Not my turn - disable all buttons
    const btns = document.querySelectorAll("button");
    btns.forEach((b) => {
      b.disabled = true;
    });
  } else {
    // My turn - enable buttons based on action state
    handleButtonsState();
  }
}

function renderHand(cards) {
  function getSpecialType(card_type){
    const specialTypes = {
      "thieft": "organ_thief",
      "organ swap": "transplant",
      "body swap": "doctors_mistake",
      "latex glove": "latex_glove",
      "epidemy": "pandemics"
    }

    return specialTypes[card_type] || "doctors_mistake";
  }

  const container = document.querySelector(".container");
  const continueBtn = document.querySelector(".continue-btn");

  // remove existing card rows
  document.querySelectorAll(".card-row").forEach((row) => row.remove());

  // re-create rows from state
  cards.forEach((c) => {
    const row = document.createElement("div");
    row.className = "card-row";
    row.id = `card-${c.card_id}`;

    const category = c.value === 0 ? "organs" : (c.value === 1 ? "medicines" : (c.value === -1 ? "virus" : "special"));
    const type = c.color === "special" ? (getSpecialType(c.card_type)) : c.color;

    const img = document.createElement("img");
    img.src = getCard(category, type);
    console.log(category, type, img.src);
    img.alt = "Card";
    img.className = "card";

    const buttons = document.createElement("div");
    buttons.className = "buttons";

    const playBtn = document.createElement("button");
    playBtn.className = "btn play-btn";
    playBtn.textContent = "Play";
    playBtn.onclick = () => playCard(c);

    const discardBtn = document.createElement("button");
    discardBtn.className = "btn discard-btn";
    discardBtn.textContent = "Discard";
    discardBtn.onclick = () => discardCard(c.card_id);

    buttons.appendChild(playBtn);
    buttons.appendChild(discardBtn);

    row.appendChild(img);
    row.appendChild(buttons);

    // insert above continue button
    container.insertBefore(row, continueBtn);
  });

  handleButtonsState();
}

function deleteCardById(card_id) {
  const row = document.querySelector(`#card-${card_id}`);
  if (row) {
    row.remove();
  } else {
    console.warn('Card row not found for deletion:', card_id);
  }
}

// ----- Actions -----

function discardCard(card_id) {
  // Track the card being discarded
  window.lastCardPlayed = card_id;
  window.lastActionType = 'discard';
  window.actionPending = true;
  handleButtonsState();
  
  // Engine expects action="discard" and card_id is OK (translator normalizes to list)
  sendEnvelope("card_play", {
    action: "discard",
    card_id: card_id
  });
}

function playCard(card) {
  console.log('playCard called with card:', card);
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
    window.lastCardPlayed = card.card_id;
    window.lastActionType = 'play';
    window.actionPending = true;
    handleButtonsState();
    sendEnvelope("card_play", {
      action: "organ",
      card_id: card.card_id
    });
    return;
  }

  if (card.value === 1) {
    // Medicine card - show own organ selection in modal
    window.lastCardPlayed = card.card_id;
    window.lastActionType = 'play';
    window.actionPending = true;
    
    // Store pending action in localStorage for modal (player-specific)
    const pendingAction = {
      card_id: card.card_id,
      action: "vaccinate",
      card_value: card.value,
      card_color: card.color
    };
    console.log('Storing pendingAction for medicine card:', pendingAction);
    console.log('Using key:', `pendingAction_${player_id}`);
    window.localStorage.setItem(`pendingAction_${player_id}`, JSON.stringify(pendingAction));
    console.log('Stored value:', window.localStorage.getItem(`pendingAction_${player_id}`));
    
    // Show modal with own organ selection (pass player_id as URL parameter)
    showModalPage(`/gameplay_telephone/choosing_organ/own_organ.html?player_id=${player_id}`);
    return;
  }

  if (card.value === -1) {
    // Virus/attack card - show player selection in modal
    window.lastCardPlayed = card.card_id;
    window.lastActionType = 'play';
    window.actionPending = true;
    
    // Store pending action in localStorage for modal
    const pendingAction = {
      card_id: card.card_id,
      action: "attack",
      card_value: card.value,
      card_color: card.color
    };
    console.log('Storing pendingAction for virus card:', pendingAction);
    console.log('Using key:', `pendingAction_${player_id}`);
    window.localStorage.setItem(`pendingAction_${player_id}`, JSON.stringify(pendingAction));
    console.log('Stored value:', window.localStorage.getItem(`pendingAction_${player_id}`));
    
    // Show modal with player selection (pass player_id as URL parameter)
    showModalPage(`/gameplay_telephone/choosing_player/ChPl.html?player_id=${player_id}`);
    return;
  }

  alert("Unknown card type/value.");
}

function playSpecial(card) {
  const card_type = card.card_type || null;
  
  console.log('Playing special card:', card_type);

  // Store pending action with card info
  const pendingAction = {
    card_id: card.card_id,
    action: "special",
    card_type: card_type
  };
  window.localStorage.setItem(`pendingAction_${player_id}`, JSON.stringify(pendingAction));
  
  window.lastCardPlayed = card.card_id;
  window.lastActionType = 'play';
  window.actionPending = true;
  handleButtonsState();

  // Open appropriate modal based on card type
  if (card_type === "organ swap") {
    showModalPage(`/gameplay_telephone/special_cards/transplant.html?player_id=${player_id}`);
    return;
  }

  if (card_type === "body swap") {
    showModalPage(`/gameplay_telephone/special_cards/body_swap.html?player_id=${player_id}`);
    return;
  }

  if (card_type === "thieft") {
    showModalPage(`/gameplay_telephone/special_cards/organ_thief.html?player_id=${player_id}`);
    return;
  }

  if (card_type === "epidemy") {
    showModalPage(`/gameplay_telephone/special_cards/pandemic.html?player_id=${player_id}`);
    return;
  }

  // latex glove needs no selection - execute immediately
  if (card_type === "latex glove") {
    sendEnvelope("card_play", {
      action: "special",
      card_id: card.card_id,
      card_type: "latex glove"
    });
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
    // Draw cards to refill hand to 3 before ending turn
    if (window.lastHandState && window.lastHandState.length < 3) {
      const cardsToDraw = 3 - window.lastHandState.length;
      console.log('Drawing', cardsToDraw, 'cards before ending turn');
      sendEnvelope("draw_cards", { count: cardsToDraw });
    }
    
    window.actionCompleted = false;
    window.actionPending = false;
    window.lastActionType = null;
    window.cardsDiscardedThisTurn = 0;
    sendEnvelope("turn_end", { action: "end_turn" });
  };
  disableContinueButton();
}

// Check if returning from action selection pages
function checkPendingAction() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('executeAction') === 'true') {
    const pendingAction = JSON.parse(window.localStorage.getItem("pendingAction") || "{}");
    
    if (pendingAction.action && pendingAction.card_id && pendingAction.target_stack) {
      console.log('Executing pending action:', pendingAction);
      
      // Set state
      window.lastCardPlayed = pendingAction.card_id;
      window.lastActionType = 'play';
      window.actionPending = true;
      handleButtonsState();
      
      // Build envelope based on action type
      const envelope = {
        action: pendingAction.action,
        card_id: pendingAction.card_id,
        target_stack: Number(pendingAction.target_stack)
      };
      
      // Add target_id for attack actions
      if (pendingAction.target_id) {
        envelope.target_id = Number(pendingAction.target_id);
      }
      
      // Send the action
      sendEnvelope("card_play", envelope);
      
      // Clear pending action
      window.localStorage.removeItem("pendingAction");
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }
}

// Function to be called from popup window when selection is complete
window.executeActionFromPopup = function(pendingAction) {
  console.log('executeActionFromPopup called with:', pendingAction);
  
  // Prevent duplicate calls
  if (window._executingAction) {
    console.log('Already executing action, ignoring duplicate call');
    return;
  }
  
  window._executingAction = true;
  
  // Set state
  window.lastCardPlayed = pendingAction.card_id;
  window.lastActionType = 'play';
  window.actionPending = true;
  handleButtonsState();
  
  // Build envelope based on action type
  let envelope = {
    action: pendingAction.action,
    card_id: pendingAction.card_id
  };
  
  // Handle special cards
  if (pendingAction.action === "special") {
    envelope.card_type = pendingAction.card_type;
    
    // Add fields based on card type
    if (pendingAction.card_type === "organ swap" || pendingAction.card_type === "body swap") {
      envelope.player_stack = Number(pendingAction.player_stack);
      envelope.target_id = Number(pendingAction.target_id);
      envelope.target_stack = Number(pendingAction.target_stack);
    } else if (pendingAction.card_type === "thieft") {
      envelope.target_id = Number(pendingAction.target_id);
      envelope.target_stack = Number(pendingAction.target_stack);
    } else if (pendingAction.card_type === "epidemy") {
      envelope.virus_cards = pendingAction.virus_cards;
      envelope.player_stacks = pendingAction.player_stacks;
      envelope.target_stacks = pendingAction.target_stacks;
      envelope.target_players = pendingAction.target_players;
    }
  } else {
    // Regular cards (attack, vaccinate, heal)
    if (pendingAction.target_stack != null) {
      envelope.target_stack = Number(pendingAction.target_stack);
    }
    if (pendingAction.target_id != null) {
      envelope.target_id = Number(pendingAction.target_id);
    }
  }
  
  console.log('Sending card_play envelope:', envelope);
  
  // Send the action
  sendEnvelope("card_play", envelope);
  
  // Clear pending action
  window.localStorage.removeItem(`pendingAction_${player_id}`);
  
  console.log('Closing modal...');
  // Close modal
  closeModal();
  
  // Reset flag after a short delay
  setTimeout(() => {
    window._executingAction = false;
    console.log('Reset _executingAction flag');
  }, 1000);
};

// Function to be called from popup when cancelled
window.cancelActionFromPopup = function() {
  console.log('Action cancelled from popup');
  window.actionPending = false;
  handleButtonsState();
  window.localStorage.removeItem("pendingAction");
  closeModal();
};

// Modal functions for mobile-friendly selection
function showModalPage(url) {
  // Create modal overlay if it doesn't exist
  let modal = document.getElementById('selection-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'selection-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
      width: 90%;
      max-width: 500px;
      height: 80%;
      background: white;
      border-radius: 10px;
      overflow: hidden;
      position: relative;
    `;
    
    const iframe = document.createElement('iframe');
    iframe.id = 'selection-iframe';
    iframe.style.cssText = `
      width: 100%;
      height: 100%;
      border: none;
    `;
    
    modalContent.appendChild(iframe);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
  }
  
  // Load URL in iframe
  const iframe = document.getElementById('selection-iframe');
  iframe.src = url;
  modal.style.display = 'flex';
}

function closeModal() {
  console.log('closeModal called');
  const modal = document.getElementById('selection-modal');
  console.log('Modal element:', modal);
  if (modal) {
    console.log('Setting modal display to none');
    modal.style.display = 'none';
    const iframe = document.getElementById('selection-iframe');
    if (iframe) {
      console.log('Clearing iframe src');
      iframe.src = 'about:blank';
    }
  } else {
    console.log('Modal element not found!');
  }
}

// Execute pending action on page load (for backwards compatibility)
// (No longer needed since we don't navigate)
