import { useCallback } from 'react';
import { login } from '../api/endpoints';
import { useAuthStore } from '../store/authStore';
import { ApiError } from '../api/client';

export function useAuth() {
  const token = useAuthStore((state) => state.token);
  const householdName = useAuthStore((state) => state.householdName);
  const setToken = useAuthStore((state) => state.setToken);
  const setHouseholdName = useAuthStore((state) => state.setHouseholdName);

  const ensureLogin = useCallback(async () => {
    const currentToken = useAuthStore.getState().token;
    if (currentToken) {
      return currentToken;
    }
    const response = await login(householdName);
    setToken(response.access_token);
    return response.access_token;
  }, [householdName, setToken]);

  return {
    token,
    householdName,
    setHouseholdName,
    setToken,
    ensureLogin,
  };
}

export function isInvalidTokenError(error: unknown) {
  return error instanceof ApiError && error.status === 401;
}
