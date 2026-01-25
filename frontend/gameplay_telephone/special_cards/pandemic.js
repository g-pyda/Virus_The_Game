// Pandemic (epidemy) card selection
const urlParams = new URLSearchParams(window.location.search);
const player_id = urlParams.get('player_id') || window.localStorage.getItem("player_id");

const pendingAction = JSON.parse(window.localStorage.getItem(`pendingAction_${player_id}`) || "{}");
const myStacks = JSON.parse(window.localStorage.getItem(`myStacksData_${player_id}`) || "[]");
const others = JSON.parse(window.localStorage.getItem(`othersData_${player_id}`) || "[]");

let transfers = []; // Array of {virus_card_id, player_stack_id, target_player_id, target_stack_id}
let currentVirusSelection = null;

const organImages = {
  "blue": "../choosing_organ/organs/brain_button.png",
  "red": "../choosing_organ/organs/heart_button.png",
  "yellow": "../choosing_organ/organs/bone_button.png",
  "green": "../choosing_organ/organs/stomach_button.png",
  "rainbow": "../choosing_organ/organs/uterus_button.png"
};

const organNames = {
  "blue": "Brain",
  "red": "Heart",
  "yellow": "Bone",
  "green": "Stomach",
  "rainbow": "Uterus"
};

// Find all virus cards in my stacks
function findMyViruses() {
  const viruses = [];
  
  myStacks.forEach(stack => {
    if (stack.value === -1) { // Infected
      // We don't have detailed card info, but we know there's a virus
      // Use stack info to represent the virus
      viruses.push({
        stack_id: stack.stack_id,
        stack_color: stack.color,
        virus_color: stack.top_card_color || stack.color,
        // We'll need to get actual card ID from backend or assume it's derivable
        displayName: `${organNames[stack.color]} - ${organNames[stack.top_card_color || stack.color]} Virus`
      });
    }
  });
  
  return viruses;
}

function renderViruses() {
  const grid = document.getElementById('virus-grid');
  grid.innerHTML = '';
  
  const viruses = findMyViruses();
  
  if (viruses.length === 0) {
    grid.innerHTML = '<p style="text-align: center;">You have no viruses to transfer.</p>';
    return;
  }
  
  viruses.forEach((virus, index) => {
    const card = document.createElement('div');
    card.className = 'virus-card';
    card.dataset.index = index;
    card.innerHTML = `
      <strong>${organNames[virus.stack_color]}</strong><br>
      <small>${organNames[virus.virus_color]} Virus</small>
    `;
    
    card.onclick = () => {
      // Check if already transferred
      const alreadyTransferred = transfers.some(t => t.player_stack_id === virus.stack_id);
      if (alreadyTransferred) {
        alert('This virus is already selected for transfer');
        return;
      }
      
      currentVirusSelection = virus;
      showTargetModal();
    };
    
    grid.appendChild(card);
  });
}

function showTargetModal() {
  const modal = document.getElementById('target-modal');
  modal.style.display = 'flex';
  renderTargetPlayerSelection();
}

function closeTargetModal() {
  const modal = document.getElementById('target-modal');
  modal.style.display = 'none';
  currentVirusSelection = null;
}

function renderTargetPlayerSelection() {
  const playerSelect = document.getElementById('modal-player-select');
  playerSelect.innerHTML = '';
  
  if (others.length === 0) {
    playerSelect.innerHTML = '<p style="text-align: center;">No other players available.</p>';
    return;
  }
  
  others.forEach(opponent => {
    const button = document.createElement('button');
    button.className = 'player-button';
    button.textContent = opponent.player_name || `Player ${opponent.player_id}`;
    
    button.onclick = () => {
      // Highlight selected
      document.querySelectorAll('#modal-player-select .player-button').forEach(b => b.classList.remove('selected'));
      button.classList.add('selected');
      
      renderTargetOrgans(opponent);
    };
    
    playerSelect.appendChild(button);
  });
}

function renderTargetOrgans(opponent) {
  const grid = document.getElementById('modal-organs-grid');
  grid.innerHTML = '';
  
  // Only show healthy organs
  const healthyStacks = opponent.stacks.filter(s => s.value === 0);
  
  if (healthyStacks.length === 0) {
    grid.innerHTML = '<p style="text-align: center; margin-top: 1rem;">This player has no healthy organs.</p>';
    return;
  }
  
  healthyStacks.forEach(stack => {
    const button = document.createElement('button');
    button.className = 'organ-slot available';
    button.style.width = '80px';
    button.style.height = '80px';
    
    const img = document.createElement('img');
    img.src = organImages[stack.color] || organImages["blue"];
    img.alt = stack.color;
    
    button.appendChild(img);
    
    button.onclick = () => {
      // Add transfer
      transfers.push({
        virus_card_id: null, // Will need to be filled by backend or we need card IDs
        player_stack_id: currentVirusSelection.stack_id,
        target_player_id: opponent.player_id,
        target_stack_id: stack.stack_id,
        displayText: `${currentVirusSelection.displayName} → ${opponent.player_name || 'Player ' + opponent.player_id}'s ${organNames[stack.color]}`
      });
      
      updateTransfersList();
      closeTargetModal();
    };
    
    grid.appendChild(button);
  });
}

function updateTransfersList() {
  if (transfers.length === 0) {
    document.getElementById('transfers-list').style.display = 'none';
    return;
  }
  
  const list = document.getElementById('transfers');
  list.innerHTML = '';
  
  transfers.forEach((transfer, index) => {
    const li = document.createElement('li');
    li.innerHTML = `
      ${transfer.displayText}
      <button onclick="removeTransfer(${index})" style="margin-left: 1rem; color: red;">✕</button>
    `;
    list.appendChild(li);
  });
  
  document.getElementById('transfers-list').style.display = 'block';
}

window.removeTransfer = function(index) {
  transfers.splice(index, 1);
  updateTransfersList();
};

function executeTransfers() {
  if (transfers.length === 0) {
    alert('Please select at least one virus to transfer');
    return;
  }
  
  // Note: We have an issue - we don't have actual virus card IDs
  // The backend expects virus_cards_ids, but we only have stack info
  // For now, we'll pass null and the backend will need to infer the virus card
  // from the player_stack_id
  
  pendingAction.action = 'special';
  pendingAction.card_type = 'epidemy';
  pendingAction.virus_cards = transfers.map(t => t.virus_card_id || 0); // Placeholder
  pendingAction.player_stacks = transfers.map(t => t.player_stack_id);
  pendingAction.target_stacks = transfers.map(t => t.target_stack_id);
  pendingAction.target_players = transfers.map(t => t.target_player_id);
  
  window.localStorage.setItem(`pendingAction_${player_id}`, JSON.stringify(pendingAction));
  
  const parentWin = window.parent !== window ? window.parent : window.opener;
  if (parentWin && parentWin.executeActionFromPopup) {
    parentWin.executeActionFromPopup(pendingAction);
  }
}

function cancelSelection() {
  const parentWin = window.parent !== window ? window.parent : window.opener;
  if (parentWin && parentWin.cancelActionFromPopup) {
    parentWin.cancelActionFromPopup();
  }
}

// Initialize
renderViruses();
