// Organ Thief card selection
const urlParams = new URLSearchParams(window.location.search);
const player_id = urlParams.get('player_id') || window.localStorage.getItem("player_id");

const pendingAction = JSON.parse(window.localStorage.getItem(`pendingAction_${player_id}`) || "{}");
const myStacks = JSON.parse(window.localStorage.getItem(`myStacksData_${player_id}`) || "[]");
const others = JSON.parse(window.localStorage.getItem(`othersData_${player_id}`) || "[]");

let selectedOpponentId = null;
const myColors = myStacks.filter(s => s.color !== 'rainbow').map(s => s.color);

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
      console.log('Selected opponent:', selectedOpponentId);
      
      // Highlight selected player
      document.querySelectorAll('.player-button').forEach(b => b.classList.remove('selected'));
      button.classList.add('selected');
      
      // Show organs
      renderOrgans(opponent);
    };
    
    playerSelect.appendChild(button);
  });
}

function renderOrgans(opponent) {
  const section = document.getElementById('organs-section');
  const grid = document.getElementById('organs-grid');
  grid.innerHTML = '';
  
  // Filter: not immune, not a color I already have (unless rainbow)
  const eligibleStacks = opponent.stacks.filter(s => 
    s.value !== 2 && // Not immune
    (s.color === 'rainbow' || !myColors.includes(s.color)) // Not duplicate color
  );
  
  if (eligibleStacks.length === 0) {
    grid.innerHTML = '<p style="text-align: center;">No eligible organs to steal from this player.</p>';
  } else {
    eligibleStacks.forEach(stack => {
      const button = document.createElement('button');
      button.className = 'organ-slot available';
      button.dataset.stackId = stack.stack_id;
      
      const img = document.createElement('img');
      img.src = organImages[stack.color] || organImages["blue"];
      img.alt = stack.color;
      
      button.appendChild(img);
      
      button.onclick = () => {
        button.disabled = true;
        button.style.opacity = '0.5';
        executeTheft(stack.stack_id);
      };
      
      grid.appendChild(button);
    });
  }
  
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth' });
}

function executeTheft(stackId) {
  console.log('executeTheft called');
  console.log('selectedOpponentId:', selectedOpponentId);
  console.log('stackId:', stackId);
  
  if (selectedOpponentId == null || stackId == null) {
    alert('Please select an organ');
    return;
  }
  
  pendingAction.action = 'special';
  pendingAction.card_type = 'thieft';
  pendingAction.target_id = selectedOpponentId;
  pendingAction.target_stack = stackId;
  
  console.log('Sending pendingAction:', pendingAction);
  
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