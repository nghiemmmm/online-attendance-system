const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5050/api";

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

export const apiClient = {
  async fetch<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { requiresAuth = true, headers, ...customConfig } = options;
    
    const config: RequestInit = {
      ...customConfig,
      headers: {
        ...headers,
      },
    };

    // Only set default Content-Type if it's not a FormData request
    // We determine this by checking if the Content-Type was explicitly removed or is not present
    // actually, a better way is to pass a flag or check if the body is FormData, but body is not available here easily.
    // However, if the caller didn't pass Content-Type, we default to json.
    if (!config.headers || !("Content-Type" in (config.headers as Record<string, string>))) {
      // It's possible Content-Type was explicitly set to undefined or deleted in post(),
      // but let's make it simpler: we will set application/json by default unless it's explicitly missing
      // Actually, if headers is passed from post() where Content-Type is deleted, it won't be in `headers`.
    }

    // A more robust way:
    const finalHeaders: Record<string, string> = { ...((headers as Record<string, string>) || {}) };
    if (!("Content-Type" in finalHeaders)) {
       finalHeaders["Content-Type"] = "application/json";
    } else if (finalHeaders["Content-Type"] === "multipart/form-data") {
        delete finalHeaders["Content-Type"]; // let browser set it with boundary
    }
    
    config.headers = finalHeaders;

    if (requiresAuth) {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      if (token) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        };
      }
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      // Handle unauthorized (e.g., token expired)
      if (response.status === 401) {
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          localStorage.removeItem("user");
          // Redirect to login page
          window.location.replace("/");
        }
      }
      
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  get<T>(endpoint: string, options?: RequestOptions) {
    return this.fetch<T>(endpoint, { ...options, method: "GET" });
  },

  post<T>(endpoint: string, body: any, options?: RequestOptions) {
    // If body is FormData, don't set Content-Type header so browser sets it with boundary
    const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
    
    const headers: Record<string, string> = { ...((options?.headers as Record<string, string>) || {}) };
    if (isFormData) {
       headers["Content-Type"] = "multipart/form-data";
    }

    return this.fetch<T>(endpoint, {
      ...options,
      method: "POST",
      headers,
      body: isFormData ? body : JSON.stringify(body),
    });
  },

  put<T>(endpoint: string, body: any, options?: RequestOptions) {
    return this.fetch<T>(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  patch<T>(endpoint: string, body: any, options?: RequestOptions) {
    return this.fetch<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(body),
    });
  },

  delete<T>(endpoint: string, options?: RequestOptions) {
    return this.fetch<T>(endpoint, { ...options, method: "DELETE" });
  },
};
