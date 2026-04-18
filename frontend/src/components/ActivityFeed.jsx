function ActivityFeed({ items = [] }) {
  return (
    <section className="surface-card dashboard-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Momentum</p>
          <h2>Recent activity</h2>
        </div>
      </div>

      <div className="activity-feed">
        {items.map((item) => (
          <article key={`${item.title}-${item.status}`} className="activity-item">
            <div className="activity-item__status">{item.status}</div>
            <div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default ActivityFeed;
