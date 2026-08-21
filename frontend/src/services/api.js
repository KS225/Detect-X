const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Get the JWT token stored by the application.
 */
export function getToken() {
  return localStorage.getItem("access_token");
}

/**
 * Store JWT token.
 */
export function saveToken(token) {
  localStorage.setItem("access_token", token);
}

/**
 * Remove JWT token.
 */
export function removeToken() {
  localStorage.removeItem("access_token");
}

/**
 * Common headers for authenticated requests.
 */
function getAuthHeaders() {
  const token = getToken();

  return {
    "Content-Type": "application/json",

    ...(token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {}),
  };
}

/**
 * Login user.
 */
export async function loginUser(email, password) {
  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || "Login failed."
    );
  }

  saveToken(data.access_token);

  return data;
}

/**
 * Register a new user.
 */
export async function registerUser(
  name,
  email,
  password
) {
  const response = await fetch(
    `${API_BASE_URL}/auth/register`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name,
        email,
        password,
      }),
    }
  );

  const data =
    await response
      .json()
      .catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Registration failed."
    );
  }

  return data;
}

/**
 * Get current logged-in user.
 */
export async function getCurrentUser() {
  const response = await fetch(
    `${API_BASE_URL}/auth/me`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to get current user."
    );
  }

  return data;
}

/**
 * Logout user.
 */
export function logoutUser() {
  removeToken();
}

/**
 * Get all websites belonging to the current user.
 */
export async function getWebsites() {
  const response = await fetch(
    `${API_BASE_URL}/websites`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to fetch websites."
    );
  }

  return data;
}

/**
 * Create a new website.
 */
export async function createWebsite(
  name,
  url,
  description = ""
) {
  const response = await fetch(
    `${API_BASE_URL}/websites`,
    {
      method: "POST",

      headers: getAuthHeaders(),

      body: JSON.stringify({
        name,
        url,
        description,
      }),
    }
  );

  const data =
    await response
      .json()
      .catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to create website."
    );
  }

  return data;
}

/**
 * Start a security scan for a website.
 */
export async function startScan(websiteId) {
  const response = await fetch(
    `${API_BASE_URL}/scanner/scan/${websiteId}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to start scan."
    );
  }

  return data;
}

/**
 * Get one scan by ID.
 */
export async function getScan(scanId) {
  const response = await fetch(
    `${API_BASE_URL}/scanner/${scanId}`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to fetch scan."
    );
  }

  return data;
}

/**
 * Stop a running scan.
 */
export async function stopScan(scanId) {
  const response = await fetch(
    `${API_BASE_URL}/scanner/stop/${scanId}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to stop scan."
    );
  }

  return data;
}

/**
 * Get scan history.
 */
export async function getScanHistory() {
  const response = await fetch(
    `${API_BASE_URL}/scanner/history`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to fetch scan history."
    );
  }

  return data;
}