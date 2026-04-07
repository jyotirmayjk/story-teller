import { useEffect, useState } from 'react';
import { DiscoveryCard } from '../../components/discoveries/DiscoveryCard';
import { EmptyState } from '../../components/common/EmptyState';
import { favoriteDiscovery, getDiscoveries } from '../../api/endpoints';
import { useAuth } from '../../hooks/useAuth';
import { useLiveStore } from '../../store/liveStore';

export function DiscoveriesScreen() {
  const { ensureLogin } = useAuth();
  const discoveries = useLiveStore((state) => state.discoveries);
  const setDiscoveries = useLiveStore((state) => state.setDiscoveries);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const token = await ensureLogin();
        const items = await getDiscoveries(token);
        if (active) {
          setDiscoveries(items);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Unable to load discoveries');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    })();

    return () => {
      active = false;
    };
  }, [ensureLogin, setDiscoveries]);

  if (loading) {
    return <div className="panel">Loading discoveries...</div>;
  }

  if (error) {
    return <EmptyState title="Could not load discoveries" description={error} />;
  }

  if (!discoveries.length) {
    return (
      <EmptyState
        title="No discoveries yet"
        description="The backend will add a discovery after a completed live voice turn."
      />
    );
  }

  return (
    <div className="page-stack">
      <section className="stack">
        <div>
          <p className="eyebrow">Discoveries</p>
          <h1 className="headline">Every completed object conversation, in one place.</h1>
        </div>
        <div className="card-grid">
          {discoveries.map((item) => (
            <DiscoveryCard
              key={item.id}
              item={item}
              onFavorite={async () => {
                const token = await ensureLogin();
                const updated = await favoriteDiscovery(token, item.id);
                setDiscoveries(
                  discoveries.map((existing) => (existing.id === updated.id ? updated : existing)),
                );
              }}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
