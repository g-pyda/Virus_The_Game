// Body Swap (doctors mistake) card selection
const urlParams = new URLSearchParams(window.location.search);
const player_id = urlParams.get('player_id') || window.localStorage.getItem("player_id");

const pendingAction = JSON.parse(window.localStorage.getItem(`pendingAction_${player_id}`) || "{}");
const others = JSON.parse(window.localStorage.getItem(`othersData_${player_id}`) || "[]");

let selectedOpponentId = null;

const organImages = {
  "blue": "../choosing_organ/organs/brain_button.png",
  "red": "../choosing_organ/organs/heart_button.png",
  "yellow": "../choosing_organ/organs/bone_button.png",
  "green": "../choosing_organ/organs/stomach_button.png",
  "rainbow": "../choosing_organ/organs/uterus_button.png"
};

function renderPlayerSelection() {
  const playerSelect = document.getElementById('player-select');
  playerSelect.innerHTML = '';
  
  console.log('Others data:', others);
  
  if (others.length === 0) {
    playerSelect.innerHTML = '<p style="text-align: center;">No other players available.</p>';
    return;
  }
  
  others.forEach(opponent => {
    const button = document.createElement('button');
    button.className = 'player-button';
    button.textContent = opponent.player_name || `Player ${opponent.player_id}`;
    button.dataset.playerId = opponent.player_id;
    
    button.onclick = () => {
      selectedOpponentId = opponent.player_id;
      console.log('Selected opponent for body swap:', selectedOpponentId);
      
      // Highlight selected player
      document.querySelectorAll('.player-button').forEach(b => b.classList.remove('selected'));
      button.classList.add('selected');
      
      // Show preview
      showPreview(opponent);
    };
    
    playerSelect.appendChild(button);
  });
}

function showPreview(opponent) {
  const preview = document.getElementById('player-preview');
  const grid = document.getElementById('organs-preview');
  grid.innerHTML = '';
  
  if (opponent.stacks.length === 0) {
    grid.innerHTML = '<p style="text-align: center;">This player has no organs.</p>';
  } else {
    opponent.stacks.forEach(stack => {
      const div = document.createElement('div');
      div.className = 'organ-slot';
      div.style.pointerEvents = 'none';
      
      const img = document.createElement('img');
      img.src = organImages[stack.color] || organImages["blue"];
      img.alt = stack.color;
      
      div.appendChild(img);
      grid.appendChild(div);
    });
  }
  
  preview.style.display = 'block';
}

function confirmSwap() {
  if (!selectedOpponentId) {
    alert('Please select a player');
    return;
  }
  
  // For body swap, we need to provide dummy stack IDs since backend expects them
  // but body swap doesn't actually use individual stacks
  pendingAction.action = 'special';
  pendingAction.card_type = 'body swap';
  pendingAction.player_stack = 0; // Dummy value
  pendingAction.target_id = selectedOpponentId;
  pendingAction.target_stack = 0; // Dummy value
  
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
renderPlayerSelection();