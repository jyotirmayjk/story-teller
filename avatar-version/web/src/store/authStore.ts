import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  householdName: string;
  setToken: (token: string | null) => void;
  setHouseholdName: (name: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      householdName: import.meta.env.VITE_DEFAULT_HOUSEHOLD_NAME || 'Web Explorer Family',
      setToken: (token) => set({ token }),
      setHouseholdName: (householdName) => set({ householdName }),
      clear: () => set({ token: null }),
    }),
    {
      name: 'whimsicalexplorer-auth',
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
