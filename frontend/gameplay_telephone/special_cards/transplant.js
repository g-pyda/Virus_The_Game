// Transplant (organ swap) card selection
const urlParams = new URLSearchParams(window.location.search);
const player_id = urlParams.get('player_id') || window.localStorage.getItem("player_id");
const game_id = window.localStorage.getItem("game_id");

const pendingAction = JSON.parse(window.localStorage.getItem(`pendingAction_${player_id}`) || "{}");
const myStacks = JSON.parse(window.localStorage.getItem(`myStacksData_${player_id}`) || "[]");
const others = JSON.parse(window.localStorage.getItem(`othersData_${player_id}`) || "[]");

let selectedMyStack = null;
let selectedOpponentId = null;
let selectedOpponentStack = null;

const organImages = {
  "blue": "../choosing_organ/organs/brain_button.png",
  "red": "../choosing_organ/organs/heart_button.png",
  "yellow": "../choosing_organ/organs/bone_button.png",
  "green": "../choosing_organ/organs/stomach_button.png",
  "rainbow": "../choosing_organ/organs/uterus_button.png"
};

// Step 1: Render my organs (exclude immune)
function renderMyOrgans() {
  const grid = document.getElementById('my-organs-grid');
  grid.innerHTML = '';
  
  const eligibleStacks = myStacks.filter(s => s.value !== 2); // Exclude immune
  
  if (eligibleStacks.length === 0) {
    grid.innerHTML = '<p style="text-align: center;">You have no organs eligible for transplant (all immune).</p>';
    return;
  }
  
  eligibleStacks.forEach(stack => {
    const button = document.createElement('button');
    button.className = 'organ-slot available';
    button.dataset.stackId = stack.stack_id;
    
    const img = document.createElement('img');
    img.src = organImages[stack.color] || organImages["blue"];
    img.alt = stack.color;
    
    button.appendChild(img);
    
    button.onclick = () => {
      selectedMyStack = stack.stack_id;
      console.log('Selected my stack:', selectedMyStack);
      
      // Show step 2
      document.getElementById('step2').style.display = 'block';
      renderOpponentSelection();
      
      // Scroll to step 2
      document.getElementById('step2').scrollIntoView({ behavior: 'smooth' });
    };
    
    grid.appendChild(button);
  });
}

// Step 2: Render opponent selection
function renderOpponentSelection() {
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
      
      // Render opponent's organs
      renderOpponentOrgans(opponent);
    };
    
    playerSelect.appendChild(button);
  });
}

function renderOpponentOrgans(opponent) {
  const grid = document.getElementById('opponent-organs-grid');
  grid.innerHTML = '';
  
  const eligibleStacks = opponent.stacks.filter(s => s.value !== 2); // Exclude immune
  
  if (eligibleStacks.length === 0) {
    grid.innerHTML = '<p style="text-align: center;">This player has no organs eligible for transplant.</p>';
    return;
  }
  
  eligibleStacks.forEach(stack => {
    const button = document.createElement('button');
    button.className = 'organ-slot available';
    button.dataset.stackId = stack.stack_id;
    
    const img = document.createElement('img');
    img.src = organImages[stack.color] || organImages["blue"];
    img.alt = stack.color;
    
    button.appendChild(img);
    
    button.onclick = () => {
      selectedOpponentStack = stack.stack_id;
      button.disabled = true;
      button.style.opacity = '0.5';
      
      console.log('Selected opponent stack:', selectedOpponentStack);
      
      // Execute action
      executeTransplant();
    };
    
    grid.appendChild(button);
  });
}

function executeTransplant() {
  console.log('executeTransplant called');
  console.log('selectedMyStack:', selectedMyStack);
  console.log('selectedOpponentId:', selectedOpponentId);
  console.log('selectedOpponentStack:', selectedOpponentStack);
  
  if (selectedMyStack == null || selectedOpponentId == null || selectedOpponentStack == null) {
    alert('Please select both organs');
    return;
  }
  
  pendingAction.action = 'special';
  pendingAction.card_type = 'organ swap';
  pendingAction.player_stack = selectedMyStack;
  pendingAction.target_id = selectedOpponentId;
  pendingAction.target_stack = selectedOpponentStack;
  
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
renderMyOrgans();
