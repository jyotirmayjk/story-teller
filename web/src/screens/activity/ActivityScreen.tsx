import { useEffect, useState } from 'react';
import { getActivity } from '../../api/endpoints';
import { ActivityItem } from '../../components/activity/ActivityItem';
import { EmptyState } from '../../components/common/EmptyState';
import { useAuth } from '../../hooks/useAuth';
import type { ActivityRecord } from '../../api/types';

export function ActivityScreen() {
  const { ensureLogin } = useAuth();
  const [items, setItems] = useState<ActivityRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const token = await ensureLogin();
        const result = await getActivity(token);
        if (active) {
          setItems(result);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Unable to load activity');
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
  }, [ensureLogin]);

  if (loading) {
    return <div className="panel">Loading activity...</div>;
  }

  if (error) {
    return <EmptyState title="Could not load activity" description={error} />;
  }

  if (!items.length) {
    return (
      <EmptyState
        title="Activity is not available yet"
        description="This backend target does not currently expose activity items, so the screen stays ready but empty."
      />
    );
  }

  return (
    <div className="page-stack">
      <section className="stack">
        <div>
          <p className="eyebrow">Activity</p>
          <h1 className="headline">Timeline of session events and interactions.</h1>
        </div>
        <div className="timeline">
          {items.map((item) => (
            <ActivityItem key={item.id} item={item} />
          ))}
        </div>
      </section>
    </div>
  );
}
