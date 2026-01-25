// Leaderboard page logic

const API_BASE_URL = '/api';

// Fetch and display leaderboard
async function loadLeaderboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/players/`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Leaderboard data:', data);
        
        displayLeaderboard(data);
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        showError('Failed to load leaderboard. Please try again later.');
    }
}

// Display leaderboard data
function displayLeaderboard(players) {
    const tableBody = document.querySelector('.leaderboard-table');
    
    // Remove existing rows (keep header)
    const existingRows = tableBody.querySelectorAll('.table-row');
    existingRows.forEach(row => row.remove());
    
    // If no players, show message
    if (!players || players.length === 0) {
        const emptyRow = document.createElement('div');
        emptyRow.className = 'table-row';
        emptyRow.innerHTML = `
            <div class="place-cell" style="grid-column: 1 / -1; text-align: center;">
                No players yet. Be the first to play!
            </div>
        `;
        tableBody.appendChild(emptyRow);
        return;
    }
    
    // Limit to top 5 players
    const topPlayers = players.slice(0, 5);
    
    // Create rows for each player
    topPlayers.forEach((player, index) => {
        const rank = index + 1;
        const row = createLeaderboardRow(rank, player);
        tableBody.appendChild(row);
    });
}

// Create a single leaderboard row
function createLeaderboardRow(rank, player) {
    const row = document.createElement('div');
    row.className = `table-row rank-${rank <= 5 ? rank : 'other'}`;
    
    // Add special styling for top 3
    if (rank === 1) {
        row.style.backgroundColor = '#FFD700'; // Gold
    } else if (rank === 2) {
        row.style.backgroundColor = '#C0C0C0'; // Silver
    } else if (rank === 3) {
        row.style.backgroundColor = '#CD7F32'; // Bronze
    }
    
    row.innerHTML = `
        <div class="place-cell">${rank}</div>
        <div class="name-cell">${escapeHtml(player.nickname)}</div>
        <div class="games-cell">${player.total_score || 0}</div>
    `;
    
    return row;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Show error message
function showError(message) {
    const tableBody = document.querySelector('.leaderboard-table');
    const existingRows = tableBody.querySelectorAll('.table-row');
    existingRows.forEach(row => row.remove());
    
    const errorRow = document.createElement('div');
    errorRow.className = 'table-row';
    errorRow.style.color = 'red';
    errorRow.innerHTML = `
        <div class="place-cell" style="grid-column: 1 / -1; text-align: center;">
            ${escapeHtml(message)}
        </div>
    `;
    tableBody.appendChild(errorRow);
}

// Add refresh button functionality
function addRefreshButton() {
    const container = document.querySelector('.leaderboard-container');
    
    // Check if button already exists
    if (document.querySelector('.refresh-button')) {
        return;
    }
    
    const buttonContainer = document.createElement('div');
    buttonContainer.style.textAlign = 'center';
    buttonContainer.style.marginTop = '20px';
    
    const refreshButton = document.createElement('button');
    refreshButton.textContent = 'Refresh Leaderboard';
    refreshButton.className = 'refresh-button';
    refreshButton.style.padding = '10px 30px';
    refreshButton.style.fontSize = '18px';
    refreshButton.style.backgroundColor = '#6CBF6C';
    refreshButton.style.color = 'white';
    refreshButton.style.border = '3px solid black';
    refreshButton.style.borderRadius = '10px';
    refreshButton.style.cursor = 'pointer';
    refreshButton.style.fontWeight = 'bold';
    
    refreshButton.onclick = () => {
        refreshButton.disabled = true;
        refreshButton.textContent = 'Loading...';
        loadLeaderboard().finally(() => {
            refreshButton.disabled = false;
            refreshButton.textContent = 'Refresh Leaderboard';
        });
    };
    
    buttonContainer.appendChild(refreshButton);
    container.appendChild(buttonContainer);
    
    // Add back to home button
    const backButton = document.createElement('button');
    backButton.textContent = 'Back to Home';
    backButton.className = 'back-button';
    backButton.style.padding = '10px 30px';
    backButton.style.fontSize = '18px';
    backButton.style.backgroundColor = '#4A90E2';
    backButton.style.color = 'white';
    backButton.style.border = '3px solid black';
    backButton.style.borderRadius = '10px';
    backButton.style.cursor = 'pointer';
    backButton.style.fontWeight = 'bold';
    backButton.style.marginLeft = '10px';
    
    backButton.onclick = () => {
        window.location.href = '/';
    };
    
    buttonContainer.appendChild(backButton);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Leaderboard page loaded');
    addRefreshButton();
    loadLeaderboard();
    
    // Auto-refresh every 30 seconds
    setInterval(loadLeaderboard, 30000);
});
