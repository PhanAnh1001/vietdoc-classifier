import { create } from "zustand";

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token:
    typeof window !== "undefined" ? localStorage.getItem("token") : null,
  setToken: (token: string) => {
    localStorage.setItem("token", token);
    document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24}`;
    set({ token });
  },
  clearAuth: () => {
    localStorage.removeItem("token");
    document.cookie = "token=; path=/; max-age=0";
    set({ token: null });
  },
}));
