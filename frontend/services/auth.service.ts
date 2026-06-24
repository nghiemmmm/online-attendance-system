import { apiClient } from "@/lib/api-client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  refresh_token?: string | null;
}

export const AuthService = {
  login: async (username: string, password: string, remember = false): Promise<LoginResponse> => {
    const data = await apiClient.post<LoginResponse>("/login/json", {
      username,
      password,
      remember_me: remember,
    }, {
      requiresAuth: false,
    });
    
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", data.access_token);
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      } else {
        localStorage.removeItem("refresh_token");
      }
    }
    
    return data;
  },

  register: async (data: any) => {
    return apiClient.post("/users/signup", data, { requiresAuth: false });
  },

  logout: async () => {
    if (typeof window === "undefined") {
      return;
    }

    const refreshToken = localStorage.getItem("refresh_token");
    try {
      if (refreshToken) {
        await apiClient.post("/login/logout", {
          refresh_token: refreshToken,
        }, {
          requiresAuth: false,
        });
      }
    } catch (error) {
      console.warn("Khong the thu hoi refresh token khi dang xuat:", error);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      window.location.replace("/");
    }
  },
  
  isAuthenticated: () => {
    if (typeof window !== "undefined") {
      return !!localStorage.getItem("access_token");
    }
    return false;
  }
};
