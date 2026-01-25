// Choosing Player page for virus/attack cards
// Displays available players and allows selection

// Get player_id from URL parameter (passed by parent)
const urlParams = new URLSearchParams(window.location.search);
const player_id = urlParams.get('player_id') || window.localStorage.getItem("player_id");
const game_id = window.localStorage.getItem("game_id");
const playerName = window.localStorage.getItem("playerName") || `Player ${player_id}`;

console.log('[choosing_player] game_id:', game_id, 'player_id:', player_id, '(from URL)');

// Get the card being played and action context
const pendingActionKey = `pendingAction_${player_id}`;
console.log('[choosing_player] Looking for key:', pendingActionKey);
const pendingAction = JSON.parse(window.localStorage.getItem(pendingActionKey) || "{}");
console.log('[choosing_player] Found pendingAction:', pendingAction);

if (!pendingAction.card_id || !pendingAction.action) {
  alert("No pending action found. Closing selection.");
  // Close modal by calling parent's cancel function
  const parentWin = window.parent !== window ? window.parent : window.opener;
  if (parentWin && parentWin.cancelActionFromPopup) {
    parentWin.cancelActionFromPopup();
  }
  // Don't navigate - this would reload deck in iframe
  throw new Error("No pending action");
}

// Set page title
document.querySelector("h1.player-title").textContent = playerName;

// Get others data from localStorage (populated by deck page, player-specific)
const othersDataRaw = window.localStorage.getItem(`othersData_${player_id}`);
console.log("Raw othersData from localStorage:", othersDataRaw);
const othersData = JSON.parse(othersDataRaw || "[]");

console.log("Current player_id:", player_id);
console.log("Parsed others data:", othersData);
console.log("Number of other players:", othersData.length);

// Render players
const playersSection = document.querySelector(".players-section");
playersSection.innerHTML = "";

if (othersData.length === 0) {
  const message = document.createElement("p");
  message.textContent = "No other players available.";
  message.style.textAlign = "center";
  message.style.marginTop = "2rem";
  playersSection.appendChild(message);
}

othersData.forEach(player => {
  console.log("Rendering player:", player.player_id, player.player_name);
  const button = document.createElement("button");
  button.className = "player-button available";
  button.dataset.playerId = player.player_id;
  
  const span = document.createElement("span");
  span.textContent = player.player_name;
  
  button.appendChild(span);
  
  button.onclick = () => {
    // Store selected player
    console.log('Selected player:', player.player_id, player.player_name);
    console.log('Player stacks:', player.stacks);
    pendingAction.target_id = player.player_id;
    pendingAction.targetPlayerName = player.player_name;
    pendingAction.targetPlayerStacks = player.stacks;
    console.log('Updated pendingAction:', pendingAction);
    window.localStorage.setItem(`pendingAction_${player_id}`, JSON.stringify(pendingAction));
    
    // Open organ selection in same iframe (pass player_id)
    window.location.href = `/gameplay_telephone/choosing_organ/ChOr.html?player_id=${player_id}`;
  };
  
  playersSection.appendChild(button);
});

// Back button
const backBtn = document.querySelector(".back-button");
if (backBtn) {
  backBtn.onclick = () => {
    // Call cancel callback in parent window (iframe) or opener (popup)
    const parentWin = window.parent !== window ? window.parent : window.opener;
    if (parentWin && parentWin.cancelActionFromPopup) {
      parentWin.cancelActionFromPopup();
    }
    window.localStorage.removeItem(`pendingAction_${player_id}`);
    if (window.opener) window.close(); // Close if popup
  };
}

// Continue button (disabled - must select a player)
const continueBtn = document.querySelector(".continue-button");
if (continueBtn) {
  continueBtn.disabled = true;
  continueBtn.style.opacity = "0.5";
}
