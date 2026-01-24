 /*
 * Common WebSocket utilities and helpers
 * Shared functions for both host and player handlers
 */

/**
 * Escape HTML special characters to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} Escaped text safe for HTML
 */
export function escapeHtml(text) {
  if (!text) return "";
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

/**
 * Safe JSON parse with error handling
 * @param {string} jsonString - JSON string to parse
 * @returns {object|null} Parsed object or null if invalid
 */
export function safeJsonParse(jsonString) {
  try {
    return JSON.parse(jsonString);
  } catch (err) {
    console.error("JSON parse error:", err);
    return null;
  }
}

/**
 * Validate WebSocket message format
 * @param {object} message - Message object to validate
 * @returns {boolean} True if message has required fields
 */
export function isValidMessage(message) {
  return (
    message &&
    typeof message === "object" &&
    message.hasOwnProperty("sender") &&
    message.hasOwnProperty("header") &&
    message.hasOwnProperty("data")
  );
}

/**
 * Debounce function to limit event handler calls
 * @param {function} fn - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {function} Debounced function
 */
export function debounce(fn, delay = 300) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Throttle function to limit event handler calls
 * @param {function} fn - Function to throttle
 * @param {number} limit - Minimum delay in milliseconds
 * @returns {function} Throttled function
 */
export function throttle(fn, limit = 300) {
  let lastRun = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastRun >= limit) {
      fn(...args);
      lastRun = now;
    }
  };
}

/**
 * Create a color-coded visual indicator for card colors
 * @param {string} color - Color name (red, blue, green, yellow, purple, etc.)
 * @returns {string} CSS color value
 */
export function getColorValue(color) {
  const colorMap = {
    red: "#ff4444",
    blue: "#4444ff",
    green: "#44ff44",
    yellow: "#ffff44",
    purple: "#ff44ff",
    cyan: "#44ffff",
    orange: "#ff8844",
    pink: "#ff44cc",
    brown: "#885522",
    gray: "#888888",
    white: "#ffffff",
    black: "#000000"
  };

  return colorMap[color.toLowerCase()] || "#999999";
}

/**
 * Create a readable status text with emoji
 * @param {string} status - Status name (healthy, infected, vaccinated, cured, etc.)
 * @returns {string} Status with emoji
 */
export function getStatusDisplay(status) {
  const statusMap = {
    healthy: "✅ Healthy",
    infected: "🦠 Infected",
    vaccinated: "💉 Vaccinated",
    cured: "🏥 Cured",
    dead: "☠️ Dead",
    active: "⚡ Active",
    inactive: "⏸️ Inactive"
  };

  return statusMap[status] || status;
}

/**
 * Get card type emoji/icon
 * @param {string} cardType - Card type name
 * @returns {string} Emoji/icon for card type
 */
export function getCardTypeIcon(cardType) {
  const iconMap = {
    organ: "🫀",
    virus: "🦠",
    vaccine: "💉",
    medicine: "💊",
    "special": "✨",
    "body swap": "🔄",
    "organ swap": "🔄",
    thieft: "🤏",
    theft: "🤏",
    "latex glove": "🧤",
    epidemy: "📊"
  };

  if (!cardType) return "🃏";
  return iconMap[cardType.toLowerCase()] || "🃏";
}

/**
 * Format large numbers with thousands separator
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Create a toast notification element
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (0 for persistent)
 * @returns {HTMLElement} Notification element
 */
export function createNotification(message, type = "info", duration = 3000) {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  // Auto-remove after duration
  if (duration > 0) {
    setTimeout(() => {
      notification.style.opacity = "0";
      notification.style.transition = "opacity 0.3s";
      setTimeout(() => notification.remove(), 300);
    }, duration);
  }

  return notification;
}

/**
 * Add notification to page
 * @param {string} message - Message to display
 * @param {string} type - Notification type
 * @param {number} duration - Duration in milliseconds
 */
export function showNotification(message, type = "info", duration = 3000) {
  const container = document.getElementById("notifications") ||
                   document.querySelector(".notifications") ||
                   document.body;

  const notification = createNotification(message, type, duration);
  container.appendChild(notification);
}

/**
 * Parse card data and provide recommendations for playing
 * @param {object} card - Card object
 * @returns {object} Card analysis with recommendations
 */
export function analyzeCard(card) {
  const analysis = {
    card_id: card.card_id,
    category: "",
    playable: true,
    recommendation: ""
  };

  if (card.color === "special" || (card.card_type && card.card_type.length > 0)) {
    analysis.category = "special";
    analysis.recommendation = `Special card: ${card.card_type || "unknown"}`;
  } else if (card.value === 0) {
    analysis.category = "organ";
    analysis.recommendation = "Play to add an organ to your body";
  } else if (card.value === 1) {
    analysis.category = "vaccine";
    analysis.recommendation = "Play to heal or vaccinate a stack";
  } else if (card.value === -1) {
    analysis.category = "virus";
    analysis.recommendation = "Play to attack an opponent's organ";
  } else {
    analysis.category = "unknown";
    analysis.playable = false;
    analysis.recommendation = "Unknown card type";
  }

  return analysis;
}

/**
 * Get a random element from an array
 * @param {array} arr - Array to pick from
 * @returns {*} Random element
 */
export function randomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Safely get nested object property
 * @param {object} obj - Object to access
 * @param {string} path - Dot-separated path (e.g., "player.stacks.0.color")
 * @returns {*} Property value or undefined
 */
export function getNestedProperty(obj, path) {
  return path.split(".").reduce((current, prop) => current?.[prop], obj);
}

/**
 * Compare two cards for sorting
 * @param {object} a - Card A
 * @param {object} b - Card B
 * @returns {number} Comparison result for sorting
 */
export function compareCards(a, b) {
  // Sort by: color, then by value, then by type
  if (a.color !== b.color) {
    return a.color.localeCompare(b.color);
  }
  if (a.value !== b.value) {
    return b.value - a.value; // Higher value first
  }
  return (a.card_type || "").localeCompare(b.card_type || "");
}

/**
 * Group cards by color
 * @param {array} cards - Cards to group
 * @returns {object} Cards grouped by color
 */
export function groupCardsByColor(cards) {
  return cards.reduce((groups, card) => {
    const color = card.color;
    if (!groups[color]) {
      groups[color] = [];
    }
    groups[color].push(card);
    return groups;
  }, {});
}

/**
 * Filter cards by criteria
 * @param {array} cards - Cards to filter
 * @param {object} criteria - Filter criteria (color, value, card_type)
 * @returns {array} Filtered cards
 */
export function filterCards(cards, criteria) {
  return cards.filter(card => {
    if (criteria.color && card.color !== criteria.color) return false;
    if (criteria.value !== undefined && card.value !== criteria.value) return false;
    if (criteria.card_type && card.card_type !== criteria.card_type) return false;
    return true;
  });
}

/**
 * Create a card element with consistent structure
 * @param {object} card - Card data
 * @param {object} options - Customization options
 * @returns {HTMLElement} Card element
 */
export function createCardElement(card, options = {}) {
  const {
    showButtons = true,
    onClick = null,
    disabled = false,
    className = ""
  } = options;

  const cardDiv = document.createElement("div");
  cardDiv.className = `card-element ${className}`;
  cardDiv.id = `card-${card.card_id}`;
  cardDiv.dataset.cardId = card.card_id;
  cardDiv.dataset.color = card.color;
  cardDiv.dataset.value = card.value;
  cardDiv.dataset.type = card.card_type || "";

  if (disabled) cardDiv.style.opacity = "0.6";

  // Card content
  cardDiv.innerHTML = `
    <div class="card-content">
      <div class="card-value">${card.value}</div>
      <div class="card-color">${escapeHtml(card.color)}</div>
      ${card.card_type ? `<div class="card-type">${escapeHtml(card.card_type)}</div>` : ""}
    </div>
  `;

  if (showButtons && !disabled) {
    const buttonContainer = document.createElement("div");
    buttonContainer.className = "card-buttons";

    const playBtn = document.createElement("button");
    playBtn.textContent = "Play";
    playBtn.className = "btn btn-play";
    playBtn.onclick = onClick || (() => console.log("Play:", card));

    buttonContainer.appendChild(playBtn);
    cardDiv.appendChild(buttonContainer);
  }

  return cardDiv;
}

/**
 * Animate an element
 * @param {HTMLElement} element - Element to animate
 * @param {string} animation - Animation name
 * @param {number} duration - Duration in milliseconds
 */
export function animateElement(element, animation, duration = 300) {
  element.style.animation = `${animation} ${duration}ms ease-in-out`;
  setTimeout(() => {
    element.style.animation = "none";
  }, duration);
}

/**
 * Log debug information with context
 * @param {string} context - Context/source of log
 * @param {*} data - Data to log
 */
export function debugLog(context, data) {
  if (window.DEBUG_WS !== false) {
    console.log(`[${context}]`, data);
  }
}

/**
 * Enable debug mode
 */
export function enableDebugMode() {
  window.DEBUG_WS = true;
  console.log("WebSocket debug mode enabled");
}

/**
 * Disable debug mode
 */
export function disableDebugMode() {
  window.DEBUG_WS = false;
  console.log("WebSocket debug mode disabled");
}
