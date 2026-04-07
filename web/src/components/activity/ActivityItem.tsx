import type { ActivityRecord } from '../../api/types';

export function ActivityItem({ item }: { item: ActivityRecord }) {
  return (
    <article className="timeline-item">
      <div className="timeline-dot" />
      <div className="panel timeline-card">
        <p className="section-kicker">{new Date(item.created_at).toLocaleString()}</p>
        <h3>{item.event_type.replaceAll('_', ' ')}</h3>
        <p className="body-copy">
          {item.metadata_json ? JSON.stringify(item.metadata_json) : 'No additional event metadata.'}
        </p>
      </div>
    </article>
  );
}
