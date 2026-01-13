/**
 * Send a custom HTTP request to the API
 * @param {string} method - HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
 * @param {string} url - The API endpoint URL
 * @param {Object|null} body - Request body (for POST, PUT, PATCH). Pass null for GET/DELETE requests.
 * @returns {Promise<Object>} - The parsed JSON response
 */
export async function sendRequest(method, url, body = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Request failed: ${method} ${url}`, error);
    throw error;
  }
}
