// Choosing Organ page for virus/attack/medicine cards
// Displays selected player's organs and allows selection

// Get player_id from URL parameter (passed by parent)
const urlParams = new URLSearchParams(window.location.search);
const player_id = urlParams.get('player_id') || window.localStorage.getItem("player_id");
const game_id = window.localStorage.getItem("game_id");
const playerName = window.localStorage.getItem("playerName") || `Player ${player_id}`;

// Get the pending action
const pendingAction = JSON.parse(window.localStorage.getItem(`pendingAction_${player_id}`) || "{}");

if (!pendingAction.card_id || !pendingAction.target_id) {
  alert("Invalid action state. Closing selection.");
  // Close modal by calling parent's cancel function
  const parentWin = window.parent !== window ? window.parent : window.opener;
  if (parentWin && parentWin.cancelActionFromPopup) {
    parentWin.cancelActionFromPopup();
  }
  // Don't navigate - this would reload deck in iframe
  throw new Error("Invalid action state");
}

// Set page title
document.querySelector("h1.player-title").textContent = playerName;

// Set opponent title
const opponentTitle = document.querySelector(".opponent-title");
if (opponentTitle) {
  opponentTitle.textContent = `Organism of ${pendingAction.targetPlayerName}`;
}

// Get target player's stacks
const targetStacks = pendingAction.targetPlayerStacks || [];

console.log('Choosing organ - pendingAction:', pendingAction);
console.log('Target player:', pendingAction.target_id, pendingAction.targetPlayerName);
console.log('Target stacks to render:', targetStacks);

// Render organs
const organsGrid = document.querySelector(".organs-grid");
organsGrid.innerHTML = "";

const organImages = {
  "blue": "organs/brain_button.png",
  "red": "organs/heart_button.png",
  "yellow": "organs/bone_button.png",
  "green": "organs/stomach_button.png",
  "rainbow": "organs/uterus_button.png"
};

if (targetStacks.length === 0) {
  const message = document.createElement("p");
  message.textContent = "This player has no organs yet.";
  message.style.textAlign = "center";
  message.style.marginTop = "2rem";
  organsGrid.appendChild(message);
} else {
  targetStacks.forEach(stack => {
    const button = document.createElement("button");
    button.className = "organ-slot available";
    button.dataset.stackId = stack.stack_id;
    
    const img = document.createElement("img");
    img.src = organImages[stack.color] || "organs/brain_button.png";
    img.alt = stack.color;
    
    button.appendChild(img);
    
    button.onclick = () => {
      console.log('Organ button clicked, stack_id:', stack.stack_id);
      
      // Disable button immediately to prevent double-clicks
      button.disabled = true;
      button.style.opacity = '0.5';
      
      // Store selected stack
      pendingAction.target_stack = stack.stack_id;
      
      console.log('Calling parent executeActionFromPopup with:', pendingAction);
      
      // Call callback in parent window (iframe) or opener (popup)
      const parentWin = window.parent !== window ? window.parent : window.opener;
      if (parentWin && parentWin.executeActionFromPopup) {
        parentWin.executeActionFromPopup(pendingAction);
      } else {
        console.error('Parent window or executeActionFromPopup not found!');
      }
      
      // Clear and close
      window.localStorage.removeItem(`pendingAction_${player_id}`);
      if (window.opener) window.close(); // Close if popup
    };
    
    organsGrid.appendChild(button);
  });
}

// Back button - return to player selection
const backBtn = document.querySelector(".back-btn");
if (backBtn) {
  backBtn.onclick = () => {
    // Remove target selection but keep the action
    delete pendingAction.target_id;
    delete pendingAction.targetPlayerName;
    delete pendingAction.targetPlayerStacks;
    delete pendingAction.target_stack;
    window.localStorage.setItem(`pendingAction_${player_id}`, JSON.stringify(pendingAction));
    
    // Navigate back to player selection in same iframe (pass player_id)
    window.location.href = `/gameplay_telephone/choosing_player/ChPl.html?player_id=${player_id}`;
  };
}

// Continue button (disabled - must select an organ)
const continueBtn = document.querySelector(".continue-btn");
if (continueBtn) {
  continueBtn.disabled = true;
  continueBtn.style.opacity = "0.5";
}
