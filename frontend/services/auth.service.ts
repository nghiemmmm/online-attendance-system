import { apiClient } from "@/lib/api-client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const AuthService = {
  login: async (username: string, password: string):Promise<LoginResponse> => {
    // OAuth2 password flow expects form data
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    const data = await apiClient.post<LoginResponse>("/login/access-token", formData, {
      requiresAuth: false,
    });
    
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", data.access_token);
    }
    
    return data;
  },

  register: async (data: { ten_dang_nhap: string; password: string; vai_tro: string }) => {
    return apiClient.post("/users/signup", data, { requiresAuth: false });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
  },
  
  isAuthenticated: () => {
    if (typeof window !== "undefined") {
      return !!localStorage.getItem("access_token");
    }
    return false;
  }
};
