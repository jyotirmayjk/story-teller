import { useEffect, useRef, useState } from 'react';
import { useSettings } from './useSettings';
import { useSession } from './useSession';
import { useAuth, isInvalidTokenError } from './useAuth';

export function useBootstrap() {
  const { voiceStyle, defaultMode, refreshSettings } = useSettings();
  const { bootstrapSession } = useSession();
  const { setToken, ensureLogin } = useAuth();
  const [bootstrapped, setBootstrapped] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    if (startedRef.current) {
      return;
    }
    startedRef.current = true;
    let active = true;
    (async () => {
      try {
        await ensureLogin();
        const settings = await refreshSettings();
        await bootstrapSession({
          defaultMode: settings.default_mode ?? defaultMode,
          voiceStyle: settings.voice_style ?? voiceStyle,
        });
        if (active) {
          setBootstrapped(true);
          setError(null);
        }
      } catch (err) {
        if (isInvalidTokenError(err)) {
          try {
            setToken(null);
            await ensureLogin();
            const settings = await refreshSettings();
            await bootstrapSession({
              defaultMode: settings.default_mode ?? defaultMode,
              voiceStyle: settings.voice_style ?? voiceStyle,
            });
            if (active) {
              setBootstrapped(true);
              setError(null);
            }
            return;
          } catch (retryError) {
            if (active) {
              setError(retryError instanceof Error ? retryError.message : 'Bootstrap failed');
            }
            return;
          }
        }
        if (active) {
          setError(err instanceof Error ? err.message : 'Bootstrap failed');
        }
      }
    })();

    return () => {
      active = false;
    };
    // Bootstrap should run once per page load. Re-running on store-driven callback
    // identity changes causes repeated settings/session fetches and socket churn.
  }, []);

  return { bootstrapped, error };
}
