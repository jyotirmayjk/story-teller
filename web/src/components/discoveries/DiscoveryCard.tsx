import { Button } from '../common/Button';
import type { DiscoveryRecord } from '../../api/types';

export function DiscoveryCard({
  item,
  onFavorite,
}: {
  item: DiscoveryRecord;
  onFavorite?: () => void;
}) {
  return (
    <article className="panel discovery-card">
      <div className="stack stack--sm">
        <p className="section-kicker">{item.mode} mode</p>
        <h3>{item.title}</h3>
        <p className="muted">
          {item.object_name || 'Unknown object'}
          {item.object_category ? ` · ${item.object_category.replaceAll('_', ' ')}` : ''}
        </p>
        <p className="body-copy">{item.summary}</p>
      </div>
      <div className="split">
        <span className="muted">{new Date(item.created_at).toLocaleString()}</span>
        {onFavorite ? (
          <Button variant={item.is_favorite ? 'primary' : 'secondary'} onClick={onFavorite}>
            {item.is_favorite ? 'Favorited' : 'Favorite'}
          </Button>
        ) : null}
      </div>
    </article>
  );
}
